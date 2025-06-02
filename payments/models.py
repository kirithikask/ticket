from django.db import models
from djongo import models as djongo_models
from django.contrib.auth import get_user_model
from bookings.models import Booking
import decimal
from decimal import Decimal
try:
    from bson.decimal128 import Decimal128
except ImportError:
    Decimal128 = None

User = get_user_model()

class Payment(djongo_models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(
        max_length=20,
        choices=[
            ('credit_card', 'Credit Card'),
            ('debit_card', 'Debit Card'),
            ('paypal', 'PayPal'),
            ('bank_transfer', 'Bank Transfer'),
            ('wallet', 'Digital Wallet'),
        ]
    )
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
            ('refunded', 'Refunded'),
        ],
        default='pending'
    )
    transaction_id = models.CharField(max_length=100, blank=True)
    payment_gateway = models.CharField(max_length=50, blank=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    refund_reason = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        # Ensure amount is a proper Decimal before saving
        if self.amount is not None and not isinstance(self.amount, Decimal):
            try:
                # Handle MongoDB Decimal128 type
                if Decimal128 and hasattr(self.amount, 'to_decimal'):
                    self.amount = self.amount.to_decimal()
                elif Decimal128 and str(type(self.amount)).find('Decimal128') != -1:
                    self.amount = Decimal(str(self.amount))
                # Handle string values that might have quotes
                elif isinstance(self.amount, str):
                    # Remove quotes and whitespace
                    cleaned_amount = str(self.amount).strip().strip('"\'')
                    self.amount = Decimal(cleaned_amount)
                else:
                    # Convert numeric types to string first, then to Decimal
                    self.amount = Decimal(str(self.amount))
            except (ValueError, TypeError, decimal.InvalidOperation):
                # If conversion fails, set to 0.00 as fallback
                self.amount = Decimal('0.00')

        # Ensure refund_amount is also a proper Decimal
        if self.refund_amount is not None and not isinstance(self.refund_amount, Decimal):
            try:
                # Handle MongoDB Decimal128 type
                if Decimal128 and hasattr(self.refund_amount, 'to_decimal'):
                    self.refund_amount = self.refund_amount.to_decimal()
                elif Decimal128 and str(type(self.refund_amount)).find('Decimal128') != -1:
                    self.refund_amount = Decimal(str(self.refund_amount))
                elif isinstance(self.refund_amount, str):
                    cleaned_refund = str(self.refund_amount).strip().strip('"\'')
                    self.refund_amount = Decimal(cleaned_refund)
                else:
                    self.refund_amount = Decimal(str(self.refund_amount))
            except (ValueError, TypeError, decimal.InvalidOperation):
                self.refund_amount = Decimal('0.00')

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Payment {self.payment_id} - {self.booking.booking_id}"

class PaymentHistory(djongo_models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    status_change = models.CharField(max_length=50)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    change_reason = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.payment.payment_id} - {self.status_change}"
