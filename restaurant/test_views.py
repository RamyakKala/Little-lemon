from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Booking, Menu


class RestaurantViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='reviewer', password='StrongPass123!')
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_root_renders_index(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h1>Little Lemon</h1>')

    def test_menu_viewset_crud(self):
        payload = {'name': 'Lemon pasta', 'description': 'Pasta with lemon', 'price': '12.50'}
        response = self.client.post('/api/menu/', payload, format='json')
        self.assertEqual(response.status_code, 201)
        menu_id = response.data['id']

        self.assertEqual(self.client.get('/api/menu/').status_code, 200)
        self.assertEqual(self.client.get(f'/api/menu/{menu_id}/').status_code, 200)

        updated_payload = {**payload, 'name': 'Updated pasta'}
        response = self.client.put(f'/api/menu/{menu_id}/', updated_payload, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'Updated pasta')

        self.assertEqual(self.client.delete(f'/api/menu/{menu_id}/').status_code, 204)
        self.assertFalse(Menu.objects.exists())

    def test_booking_viewset_crud(self):
        payload = {
            'first_name': 'Ari',
            'reservation_date': '2026-10-21',
            'reservation_slot': '10:00',
        }
        response = self.client.post('/api/bookings/', payload, format='json')
        self.assertEqual(response.status_code, 201)
        booking_id = response.data['id']

        self.assertEqual(self.client.get('/api/bookings/').status_code, 200)
        self.assertEqual(self.client.get(f'/api/bookings/{booking_id}/').status_code, 200)

        updated_payload = {**payload, 'first_name': 'Arianna'}
        response = self.client.put(f'/api/bookings/{booking_id}/', updated_payload, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['first_name'], 'Arianna')

        self.assertEqual(self.client.delete(f'/api/bookings/{booking_id}/').status_code, 204)
        self.assertFalse(Booking.objects.exists())

    def test_api_viewsets_require_authentication(self):
        self.client.force_authenticate(user=None)

        self.assertEqual(self.client.get('/api/menu/').status_code, 401)
        self.assertEqual(self.client.get('/api/bookings/').status_code, 401)

    def test_api_collections_render_browsable_api(self):
        for endpoint in ['/api/menu/', '/api/bookings/']:
            response = self.client.get(endpoint, HTTP_ACCEPT='text/html')

            self.assertEqual(response.status_code, 200)
            self.assertIn('text/html', response['Content-Type'])

    def test_token_authentication_endpoint(self):
        response = APIClient().post(
            '/api-token-auth/',
            {'username': 'reviewer', 'password': 'StrongPass123!'},
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)

        authenticated_client = APIClient()
        authenticated_client.credentials(HTTP_AUTHORIZATION=f"Token {response.data['token']}")
        self.assertEqual(authenticated_client.get('/api/bookings/').status_code, 200)