from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Category, MenuItem


class MenuItemAPITests(TestCase):
	def setUp(self):
		self.admin = User.objects.create_superuser(username='menu_admin', password='StrongPass123!')
		self.category = Category.objects.create(title='Mains')
		self.client = APIClient()

	def test_menu_items_are_readable_without_authentication(self):
		response = self.client.get('/api/menu-items/')

		self.assertEqual(response.status_code, 200)

	def test_menu_item_api_crud(self):
		self.client.force_authenticate(self.admin)
		payload = {'title': 'Lemon Pasta', 'price': '12.50', 'category': self.category.id, 'featured': False}

		response = self.client.post('/api/menu-items/', payload, format='json')
		self.assertEqual(response.status_code, 201)
		menu_item_id = response.data['id']
		self.assertEqual(self.client.get(f'/api/menu-items/{menu_item_id}/').status_code, 200)

		updated_payload = {**payload, 'title': 'Lemon Pasta Special'}
		response = self.client.put(f'/api/menu-items/{menu_item_id}/', updated_payload, format='json')
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data['title'], 'Lemon Pasta Special')

		self.assertEqual(self.client.delete(f'/api/menu-items/{menu_item_id}/').status_code, 204)
		self.assertFalse(MenuItem.objects.filter(pk=menu_item_id).exists())
