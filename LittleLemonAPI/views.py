from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Cart, Category, MenuItem, Order
from .permissions import IsAdmin, IsCustomer, IsDeliveryCrew, IsManager, IsManagerOrAdmin
from .serializers import CartSerializer, CategorySerializer, MenuItemSerializer, OrderSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('title')
    serializer_class = CategorySerializer

    def get_permissions(self):
        return [AllowAny()] if self.action == 'list' else [IsAdmin()]


class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.select_related('category').all().order_by('id')
    serializer_class = MenuItemSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
        ordering = self.request.query_params.get('ordering')
        if ordering in {'price', '-price'}:
            queryset = queryset.order_by(ordering)
        return queryset

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        if self.action in ['update', 'partial_update']:
            return [IsAdmin() if self.request.user.is_superuser or self.request.user.groups.filter(name='Admin').exists() else IsManager()]
        return [IsAdmin()]

    def perform_update(self, serializer):
        if not (self.request.user.is_superuser or self.request.user.groups.filter(name='Admin').exists()):
            serializer.save(title=self.get_object().title, price=self.get_object().price, category=self.get_object().category)
        else:
            serializer.save()


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user).select_related('menu_item').order_by('id')

    def get_permissions(self):
        return [IsCustomer()]

    def perform_create(self, serializer):
        cart_item, created = Cart.objects.get_or_create(
            user=self.request.user,
            menu_item=serializer.validated_data['menu_item'],
            defaults={'quantity': serializer.validated_data['quantity']},
        )
        if not created:
            cart_item.quantity += serializer.validated_data['quantity']
            cart_item.save(update_fields=['quantity'])


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.groups.filter(name__in=['Admin', 'Manager']).exists():
            return Order.objects.all().order_by('-date')
        if user.groups.filter(name='DeliveryCrew').exists():
            return Order.objects.filter(delivery_crew=user).order_by('-date')
        return Order.objects.filter(user=user).order_by('-date')

    def get_permissions(self):
        if self.action == 'create':
            return [IsCustomer()]
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        if self.action == 'mark_delivered':
            return [IsDeliveryCrew()]
        return [IsManagerOrAdmin()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        Cart.objects.filter(user=self.request.user).delete()

    @action(detail=True, methods=['patch'])
    def mark_delivered(self, request, pk=None):
        order = get_object_or_404(self.get_queryset(), pk=pk)
        order.status = Order.DELIVERED
        order.save(update_fields=['status'])
        return Response(self.get_serializer(order).data)

    def update(self, request, *args, **kwargs):
        if 'delivery_crew' in request.data:
            crew = get_object_or_404(User, pk=request.data['delivery_crew'])
            if not crew.groups.filter(name='DeliveryCrew').exists():
                return Response({'detail': 'User must belong to DeliveryCrew.'}, status=status.HTTP_400_BAD_REQUEST)
            order = self.get_object()
            order.delivery_crew = crew
            order.save(update_fields=['delivery_crew'])
            return Response(self.get_serializer(order).data)
        return super().update(request, *args, **kwargs)

    partial_update = update
