import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'littlelemon.settings')

import django

django.setup()

from django.contrib.auth.models import Group, User
from LittleLemonAPI.models import Category, MenuItem


def user(username, password, group=None, superuser=False):
    account, created = User.objects.get_or_create(username=username)
    account.set_password(password)
    account.is_staff = superuser
    account.is_superuser = superuser
    account.save()
    if group:
        account.groups.add(Group.objects.get(name=group))
    return account


for group_name in ['Admin', 'Manager', 'DeliveryCrew', 'Customer']:
    Group.objects.get_or_create(name=group_name)

user('admin', 'AdminPass123!', 'Admin', True)
user('manager', 'ManagerPass123!', 'Manager')
user('delivery', 'DeliveryPass123!', 'DeliveryCrew')
user('customer', 'CustomerPass123!', 'Customer')

italian, _ = Category.objects.get_or_create(title='Italian')
main, _ = Category.objects.get_or_create(title='Main Course')
MenuItem.objects.get_or_create(title='Bruschetta', category=italian, defaults={'price': '7.50'})
MenuItem.objects.get_or_create(title='Pasta Primavera', category=main, defaults={'price': '14.00', 'featured': True})
MenuItem.objects.get_or_create(title='Tiramisu', category=italian, defaults={'price': '8.00'})
print('Seed data created.')
