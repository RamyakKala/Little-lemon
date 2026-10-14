from django.db import models


class Menu(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.name


AVAILABLE_SLOTS = [
    ('10:00', '10:00'),
    ('11:00', '11:00'),
    ('12:00', '12:00'),
    ('13:00', '13:00'),
    ('14:00', '14:00'),
    ('15:00', '15:00'),
    ('16:00', '16:00'),
    ('17:00', '17:00'),
    ('18:00', '18:00'),
    ('19:00', '19:00'),
    ('20:00', '20:00'),
    ('21:00', '21:00'),
]


class Booking(models.Model):
    first_name = models.CharField(max_length=100)
    reservation_date = models.DateField()
    reservation_slot = models.CharField(max_length=5, choices=AVAILABLE_SLOTS)

    class Meta:
        ordering = ['reservation_date', 'reservation_slot', 'id']
        constraints = [
            models.UniqueConstraint(
                fields=['reservation_date', 'reservation_slot'],
                name='unique_reservation_slot_per_date',
            ),
        ]

    def __str__(self):
        return f'{self.first_name} - {self.reservation_date} {self.reservation_slot}'
