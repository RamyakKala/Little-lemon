from django.contrib.auth.models import User
from django.db import models


class Category(models.Model):
	title = models.CharField(max_length=100, unique=True)

	def __str__(self):
		return self.title


class MenuItem(models.Model):
	title = models.CharField(max_length=100)
	price = models.DecimalField(max_digits=6, decimal_places=2)
	category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='menu_items')
	featured = models.BooleanField(default=False)

	def __str__(self):
		return self.title


class Cart(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
	menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
	quantity = models.PositiveIntegerField(default=1)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=['user', 'menu_item'], name='unique_user_menu_item'),
		]


class Order(models.Model):
	PENDING = 'pending'
	DELIVERED = 'delivered'
	STATUS_CHOICES = [(PENDING, 'Pending'), (DELIVERED, 'Delivered')]

	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
	delivery_crew = models.ForeignKey(
		User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_orders'
	)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
	date = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f'Order {self.pk}'
