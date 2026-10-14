import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'littlelemon.settings')

import django

django.setup()

from rest_framework.test import APIClient
from django.contrib.auth.models import User
from LittleLemonAPI.models import Cart, Order


def login(username, password):
    response = APIClient().post('/auth/token/login/', {'username': username, 'password': password}, format='json')
    assert response.status_code == 200, response.data
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Token {response.data['auth_token']}")
    return client


public = APIClient()
assert public.get('/api/categories/').status_code == 200
assert public.get('/api/menu-items/?ordering=price').status_code == 200

role_user, _ = User.objects.get_or_create(username='role_test_user')
role_user.set_password('RolePass123!')
role_user.save()
admin_client = login('admin', 'AdminPass123!')
assert admin_client.post('/api/groups/manager/users', {'username': role_user.username}, format='json').status_code == 201
manager_client = login('manager', 'ManagerPass123!')
assert manager_client.post('/api/groups/delivery-crew/users', {'username': role_user.username}, format='json').status_code == 201
role_user.delete()

Cart.objects.filter(user__username='customer').delete()
Order.objects.filter(user__username='customer').delete()

customer = login('customer', 'CustomerPass123!')
assert customer.post('/api/cart/', {'menu_item': 1, 'quantity': 2}, format='json').status_code == 201
assert customer.get('/api/cart/').status_code == 200
order = customer.post('/api/orders/', {}, format='json')
assert order.status_code == 201, order.data
order_id = order.data['id']

manager = login('manager', 'ManagerPass123!')
assert manager.patch(f'/api/orders/{order_id}/', {'delivery_crew': User.objects.get(username='delivery').id}, format='json').status_code == 200

crew = login('delivery', 'DeliveryPass123!')
assert crew.get('/api/orders/').status_code == 200
assert crew.patch(f'/api/orders/{order_id}/mark_delivered/').status_code == 200
assert crew.get(f'/api/orders/{order_id}/').data['status'] == 'delivered'

print('Smoke test passed.')
