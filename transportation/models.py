from django.db import models
from djongo import models as djongo_models
from datetime import datetime, time

class TransportationType(djongo_models.Model):
    name = models.CharField(max_length=50, unique=True)  # Bus, Train, Flight
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)  # For UI icons

    def __str__(self):
        return self.name

class Route(djongo_models.Model):
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    distance = models.FloatField()  # in kilometers
    estimated_duration = models.DurationField()  # travel time
    transportation_type = models.ForeignKey(TransportationType, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['origin', 'destination', 'transportation_type']

    def __str__(self):
        return f"{self.origin} to {self.destination} ({self.transportation_type.name})"

class Vehicle(djongo_models.Model):
    vehicle_number = models.CharField(max_length=20, unique=True)
    transportation_type = models.ForeignKey(TransportationType, on_delete=models.CASCADE)
    capacity = models.IntegerField()
    amenities = djongo_models.JSONField(default=list)  # WiFi, AC, etc.
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.vehicle_number} ({self.transportation_type.name})"

class Schedule(djongo_models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    departure_date = models.DateField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available_seats = models.IntegerField()
    status = models.CharField(
        max_length=20,
        choices=[
            ('scheduled', 'Scheduled'),
            ('delayed', 'Delayed'),
            ('cancelled', 'Cancelled'),
            ('completed', 'Completed'),
        ],
        default='scheduled'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.route} - {self.departure_date} {self.departure_time}"

class Seat(djongo_models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    seat_number = models.CharField(max_length=10)
    seat_type = models.CharField(
        max_length=20,
        choices=[
            ('window', 'Window'),
            ('aisle', 'Aisle'),
            ('middle', 'Middle'),
        ]
    )
    is_available = models.BooleanField(default=True)

    class Meta:
        unique_together = ['vehicle', 'seat_number']

    def __str__(self):
        return f"{self.vehicle.vehicle_number} - Seat {self.seat_number}"
