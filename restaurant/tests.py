from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from .models import Booking


class BookingTests(TestCase):
    def test_booking_form_renders_date_picker_and_slots(self):
        response = self.client.get(reverse('booking-form'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'type="date"')
        self.assertContains(response, 'name="reservation_slot"')

    def test_menu_page_renders(self):
        response = self.client.get(reverse('menu-page'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Little Lemon Menu')

    def test_list_bookings_and_filter_by_date(self):
        Booking.objects.create(
            first_name='Ari', reservation_date=date(2026, 10, 7), reservation_slot='10:00'
        )

        response = self.client.get('/bookings')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

        response = self.client.get('/bookings', {'date': '2026-10-07'})
        self.assertEqual(response.json()[0]['first_name'], 'Ari')

        response = self.client.get('/bookings', {'date': '2026-10-08'})
        self.assertEqual(response.json(), {'message': 'No Booking'})

    def test_duplicate_slot_is_rejected(self):
        payload = {
            'first_name': 'Ari',
            'reservation_date': '2026-10-07',
            'reservation_slot': '10:00',
        }
        first_response = self.client.post('/bookings', payload)
        second_response = self.client.post('/bookings', payload)

        self.assertEqual(first_response.status_code, 201)
        self.assertEqual(second_response.status_code, 409)
        self.assertEqual(Booking.objects.count(), 1)


class BookingAPITests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='reviewer', password='StrongPass123!')
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.payload = {
            'first_name': 'Ari',
            'reservation_date': '2026-10-07',
            'reservation_slot': '10:00',
        }

    def test_booking_api_crud(self):
        response = self.client.post('/api/bookings/', self.payload, format='json')
        self.assertEqual(response.status_code, 201)
        booking_id = response.data['id']

        self.assertEqual(self.client.get('/api/bookings/').status_code, 200)
        self.assertEqual(self.client.get(f'/api/bookings/{booking_id}/').status_code, 200)

        updated_payload = {**self.payload, 'first_name': 'Arianna'}
        response = self.client.put(f'/api/bookings/{booking_id}/', updated_payload, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['first_name'], 'Arianna')

        self.assertEqual(self.client.delete(f'/api/bookings/{booking_id}/').status_code, 204)
        self.assertEqual(Booking.objects.count(), 0)

    def test_duplicate_booking_is_rejected(self):
        self.assertEqual(self.client.post('/api/bookings/', self.payload, format='json').status_code, 201)
        response = self.client.post('/api/bookings/', self.payload, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Booking.objects.count(), 1)

    def test_booking_api_requires_authentication(self):
        self.client.force_authenticate(user=None)

        self.assertEqual(self.client.get('/api/bookings/').status_code, 401)

    def test_registration_and_token_authentication(self):
        response = APIClient().post(
            '/api/registration/',
            {'username': 'new_reviewer', 'password': 'StrongPass123!'},
            format='json',
        )
        self.assertEqual(response.status_code, 201)

        response = APIClient().post(
            '/api/token/login/',
            {'username': 'new_reviewer', 'password': 'StrongPass123!'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('auth_token', response.data)

        authenticated_client = APIClient()
        authenticated_client.credentials(HTTP_AUTHORIZATION=f"Token {response.data['auth_token']}")
        self.assertEqual(authenticated_client.get('/api/bookings/').status_code, 200)
