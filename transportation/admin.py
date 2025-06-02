from django.contrib import admin
from .models import TransportationType, Route, Vehicle, Schedule, Seat

@admin.register(TransportationType)
class TransportationTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('origin', 'destination', 'transportation_type', 'distance', 'is_active')
    list_filter = ('transportation_type', 'is_active')
    search_fields = ('origin', 'destination')

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('vehicle_number', 'transportation_type', 'capacity', 'is_active')
    list_filter = ('transportation_type', 'is_active')
    search_fields = ('vehicle_number',)

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('route', 'vehicle', 'departure_date', 'departure_time', 'price', 'available_seats', 'status')
    list_filter = ('status', 'departure_date', 'route__transportation_type')
    search_fields = ('route__origin', 'route__destination', 'vehicle__vehicle_number')
    date_hierarchy = 'departure_date'

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'seat_number', 'seat_type', 'is_available')
    list_filter = ('seat_type', 'is_available', 'vehicle__transportation_type')
    search_fields = ('vehicle__vehicle_number', 'seat_number')
