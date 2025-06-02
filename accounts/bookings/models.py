from django.db import models
from djongo import models as djongo_models
from django.contrib.auth import get_user_model
from transportation.models import Schedule, Seat
import uuid
import decimal
from decimal import Decimal
try:
    from bson.decimal128 import Decimal128
except ImportError:
    Decimal128 = None

User = get_user_model()

class Booking(djongo_models.Model):
    booking_id = models.CharField(max_length=20, unique=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    booking_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('confirmed', 'Confirmed'),
            ('cancelled', 'Cancelled'),
            ('completed', 'Completed'),
        ],
        default='pending'
    )
    passenger_details = djongo_models.JSONField(default=list)
    special_requests = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Ensure total_amount is a proper Decimal before saving
        if self.total_amount is not None and not isinstance(self.total_amount, Decimal):
            try:
                # Handle MongoDB Decimal128 type
                if Decimal128 and hasattr(self.total_amount, 'to_decimal'):
                    self.total_amount = self.total_amount.to_decimal()
                elif Decimal128 and str(type(self.total_amount)).find('Decimal128') != -1:
                    self.total_amount = Decimal(str(self.total_amount))
                # Handle string values that might have quotes
                elif isinstance(self.total_amount, str):
                    # Remove quotes and whitespace
                    cleaned_amount = str(self.total_amount).strip().strip('"\'')
                    self.total_amount = Decimal(cleaned_amount)
                else:
                    # Convert numeric types to string first, then to Decimal
                    self.total_amount = Decimal(str(self.total_amount))
            except (ValueError, TypeError, decimal.InvalidOperation):
                # If conversion fails, set to 0.00 as fallback
                self.total_amount = Decimal('0.00')

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking {self.booking_id} - {self.user.username}"

class BookingSeat(djongo_models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='booked_seats')
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    passenger_name = models.CharField(max_length=100)
    passenger_age = models.IntegerField()
    passenger_gender = models.CharField(
        max_length=10,
        choices=[
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other'),
        ]
    )

    class Meta:
        unique_together = ['booking', 'seat']

    def __str__(self):
        return f"{self.booking.booking_id} - {self.seat.seat_number}"

class BookingHistory(djongo_models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    status_change = models.CharField(max_length=50)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    change_reason = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.booking.booking_id} - {self.status_change}"
