from django.db import models
from django.contrib.auth.models import User
import uuid


class TicketType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Booking(models.Model):
    BOOKING_STATUS = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
    ]

    booking_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    visitor_name = models.CharField(max_length=100)
    visitor_email = models.EmailField()

    ticket_type = models.ForeignKey(
        TicketType,
        on_delete=models.PROTECT
    )

    quantity = models.PositiveIntegerField(default=1)
    visit_date = models.DateField()

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=BOOKING_STATUS,
        default='PENDING'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.visitor_name} - {self.booking_id}"