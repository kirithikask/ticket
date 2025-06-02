from django.db import models
from django.contrib.auth.models import AbstractUser
from djongo import models as djongo_models

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    preferred_seat_type = models.CharField(
        max_length=20,
        choices=[
            ('window', 'Window'),
            ('aisle', 'Aisle'),
            ('middle', 'Middle'),
            ('any', 'Any'),
        ],
        default='any'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

class UserProfile(djongo_models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True)
    travel_preferences = djongo_models.JSONField(default=dict)
    loyalty_points = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username}'s Profile"
