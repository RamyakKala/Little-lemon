from datetime import date

from django.db import IntegrityError, transaction
from django.test import TestCase

from .models import Booking, Menu


class MenuModelTests(TestCase):
    def test_menu_stores_fields_and_string_representation(self):
        menu = Menu.objects.create(
            name='Lemon pasta', description='Pasta with lemon', price='12.50'
        )

        self.assertEqual(menu.name, 'Lemon pasta')
        self.assertEqual(menu.description, 'Pasta with lemon')
        self.assertEqual(str(menu.price), '12.50')
        self.assertEqual(str(menu), 'Lemon pasta')


class BookingModelTests(TestCase):
    def test_booking_stores_fields_and_string_representation(self):
        booking = Booking.objects.create(
            first_name='Ari', reservation_date=date(2026, 10, 21), reservation_slot='10:00'
        )

        self.assertEqual(booking.first_name, 'Ari')
        self.assertEqual(booking.reservation_date, date(2026, 10, 21))
        self.assertEqual(booking.reservation_slot, '10:00')
        self.assertEqual(str(booking), 'Ari - 2026-10-21 10:00')

    def test_booking_prevents_duplicate_slots_on_the_same_date(self):
        Booking.objects.create(
            first_name='Ari', reservation_date=date(2026, 10, 21), reservation_slot='10:00'
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Booking.objects.create(
                    first_name='Sam', reservation_date=date(2026, 10, 21), reservation_slot='10:00'
                )