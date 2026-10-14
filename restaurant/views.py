import json

from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_http_methods
from rest_framework import viewsets

from LittleLemonAPI.models import MenuItem
from .models import AVAILABLE_SLOTS, Booking
from .serializers import BookingSerializer


def booking_form(request):
    return render(request, 'restaurant/booking_form.html', {'available_slots': AVAILABLE_SLOTS})


def menu_page(request):
    menu_items = MenuItem.objects.select_related('category').all()
    return render(request, 'restaurant/menu.html', {'menu_items': menu_items})


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer


@require_http_methods(['GET', 'POST'])
def bookings(request):
    if request.method == 'GET':
        queryset = Booking.objects.all()
        requested_date = request.GET.get('date')
        if requested_date:
            parsed_date = parse_date(requested_date)
            if parsed_date is None:
                return JsonResponse({'message': 'Invalid date. Use YYYY-MM-DD.'}, status=400)
            queryset = queryset.filter(reservation_date=parsed_date)

        results = [
            {
                'id': booking.id,
                'first_name': booking.first_name,
                'reservation_date': booking.reservation_date.isoformat(),
                'reservation_slot': booking.reservation_slot,
            }
            for booking in queryset
        ]
        if requested_date and not results:
            return JsonResponse({'message': 'No Booking'})
        return JsonResponse(results, safe=False)

    try:
        if request.content_type == 'application/json':
            payload = json.loads(request.body)
        else:
            payload = request.POST
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'message': 'Invalid request body.'}, status=400)

    first_name = str(payload.get('first_name', '')).strip()
    reservation_date = parse_date(str(payload.get('reservation_date', '')))
    reservation_slot = str(payload.get('reservation_slot', ''))
    if not first_name or len(first_name) > 100 or reservation_date is None:
        return JsonResponse({'message': 'Enter a first name and valid reservation date.'}, status=400)
    if reservation_slot not in dict(AVAILABLE_SLOTS):
        return JsonResponse({'message': 'Choose an available reservation slot.'}, status=400)

    try:
        with transaction.atomic():
            booking = Booking.objects.create(
                first_name=first_name,
                reservation_date=reservation_date,
                reservation_slot=reservation_slot,
            )
    except IntegrityError:
        return JsonResponse({'message': 'That reservation slot is already booked.'}, status=409)

    return JsonResponse(
        {
            'id': booking.id,
            'first_name': booking.first_name,
            'reservation_date': booking.reservation_date.isoformat(),
            'reservation_slot': booking.reservation_slot,
        },
        status=201,
    )
