from django.contrib import admin

from .models import Cart, Category, MenuItem, Order

admin.site.register([Category, MenuItem, Cart, Order])
