from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta, time
from transportation.models import TransportationType, Route, Vehicle, Schedule, Seat
from decimal import Decimal

class Command(BaseCommand):
    help = 'Populate database with sample transportation data'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create transportation types
        bus_type, _ = TransportationType.objects.get_or_create(
            name='Bus',
            defaults={'description': 'Comfortable bus transportation', 'icon': 'fas fa-bus'}
        )
        
        train_type, _ = TransportationType.objects.get_or_create(
            name='Train',
            defaults={'description': 'Fast and reliable train service', 'icon': 'fas fa-train'}
        )
        
        flight_type, _ = TransportationType.objects.get_or_create(
            name='Flight',
            defaults={'description': 'Quick air travel', 'icon': 'fas fa-plane'}
        )
        
        self.stdout.write('Transportation types created.')
        
        # Create routes
        routes_data = [
            ('New York', 'Boston', 215.0, timedelta(hours=4), bus_type),
            ('New York', 'Philadelphia', 95.0, timedelta(hours=2), bus_type),
            ('Los Angeles', 'San Francisco', 380.0, timedelta(hours=6), bus_type),
            ('Chicago', 'Detroit', 280.0, timedelta(hours=4, minutes=30), train_type),
            ('New York', 'Washington DC', 225.0, timedelta(hours=3), train_type),
            ('New York', 'Los Angeles', 2445.0, timedelta(hours=5, minutes=30), flight_type),
            ('Chicago', 'Miami', 1190.0, timedelta(hours=3), flight_type),
        ]
        
        routes = []
        for origin, destination, distance, duration, transport_type in routes_data:
            route, created = Route.objects.get_or_create(
                origin=origin,
                destination=destination,
                transportation_type=transport_type,
                defaults={
                    'distance': distance,
                    'estimated_duration': duration,
                    'is_active': True
                }
            )
            routes.append(route)
        
        self.stdout.write('Routes created.')
        
        # Create vehicles
        vehicles_data = [
            ('BUS001', bus_type, 45, ['WiFi', 'AC', 'Reclining Seats']),
            ('BUS002', bus_type, 50, ['WiFi', 'AC', 'USB Charging']),
            ('BUS003', bus_type, 40, ['AC', 'Reclining Seats']),
            ('TRAIN001', train_type, 120, ['WiFi', 'Dining Car', 'Power Outlets']),
            ('TRAIN002', train_type, 100, ['WiFi', 'AC', 'Quiet Car']),
            ('FLIGHT001', flight_type, 180, ['WiFi', 'Entertainment', 'Meals']),
            ('FLIGHT002', flight_type, 150, ['WiFi', 'Entertainment']),
        ]
        
        vehicles = []
        for vehicle_num, transport_type, capacity, amenities in vehicles_data:
            vehicle, created = Vehicle.objects.get_or_create(
                vehicle_number=vehicle_num,
                defaults={
                    'transportation_type': transport_type,
                    'capacity': capacity,
                    'amenities': amenities,
                    'is_active': True
                }
            )
            vehicles.append(vehicle)
        
        self.stdout.write('Vehicles created.')
        
        # Create seats for each vehicle
        for vehicle in vehicles:
            if not Seat.objects.filter(vehicle=vehicle).exists():
                self.create_seats_for_vehicle(vehicle)
        
        self.stdout.write('Seats created.')
        
        # Create schedules for the next 7 days
        today = timezone.now().date()
        
        schedule_data = [
            (routes[0], vehicles[0], time(8, 0), time(12, 0), Decimal('45.00')),  # NY-Boston Bus
            (routes[0], vehicles[1], time(14, 0), time(18, 0), Decimal('45.00')),
            (routes[1], vehicles[0], time(9, 0), time(11, 0), Decimal('25.00')),  # NY-Philadelphia Bus
            (routes[2], vehicles[2], time(7, 0), time(13, 0), Decimal('65.00')),  # LA-SF Bus
            (routes[3], vehicles[3], time(10, 0), time(14, 30), Decimal('85.00')), # Chicago-Detroit Train
            (routes[4], vehicles[4], time(16, 0), time(19, 0), Decimal('95.00')),  # NY-DC Train
            (routes[5], vehicles[5], time(6, 0), time(11, 30), Decimal('350.00')), # NY-LA Flight
            (routes[6], vehicles[6], time(13, 0), time(16, 0), Decimal('280.00')), # Chicago-Miami Flight
        ]
        
        for i in range(7):  # Next 7 days
            schedule_date = today + timedelta(days=i)
            
            for route, vehicle, dep_time, arr_time, price in schedule_data:
                Schedule.objects.get_or_create(
                    route=route,
                    vehicle=vehicle,
                    departure_date=schedule_date,
                    departure_time=dep_time,
                    defaults={
                        'arrival_time': arr_time,
                        'price': price,
                        'available_seats': vehicle.capacity,
                        'status': 'scheduled'
                    }
                )
        
        self.stdout.write('Schedules created.')
        self.stdout.write(self.style.SUCCESS('Sample data populated successfully!'))
    
    def create_seats_for_vehicle(self, vehicle):
        """Create seats for a vehicle based on its type and capacity"""
        if vehicle.transportation_type.name == 'Bus':
            # Bus layout: 2+2 seating
            seats_per_row = 4
            rows = vehicle.capacity // seats_per_row
            
            for row in range(1, rows + 1):
                for seat_pos in range(1, seats_per_row + 1):
                    seat_number = f"{row}{chr(64 + seat_pos)}"  # 1A, 1B, 1C, 1D
                    
                    if seat_pos in [1, 4]:  # Window seats
                        seat_type = 'window'
                    elif seat_pos in [2, 3]:  # Aisle seats
                        seat_type = 'aisle'
                    else:
                        seat_type = 'middle'
                    
                    Seat.objects.create(
                        vehicle=vehicle,
                        seat_number=seat_number,
                        seat_type=seat_type,
                        is_available=True
                    )
        
        elif vehicle.transportation_type.name == 'Train':
            # Train layout: 2+2 seating
            seats_per_row = 4
            rows = vehicle.capacity // seats_per_row
            
            for row in range(1, rows + 1):
                for seat_pos in range(1, seats_per_row + 1):
                    seat_number = f"{row}{chr(64 + seat_pos)}"
                    
                    if seat_pos in [1, 4]:
                        seat_type = 'window'
                    else:
                        seat_type = 'aisle'
                    
                    Seat.objects.create(
                        vehicle=vehicle,
                        seat_number=seat_number,
                        seat_type=seat_type,
                        is_available=True
                    )
        
        elif vehicle.transportation_type.name == 'Flight':
            # Flight layout: 3+3 seating
            seats_per_row = 6
            rows = vehicle.capacity // seats_per_row
            
            for row in range(1, rows + 1):
                for seat_pos in range(1, seats_per_row + 1):
                    seat_number = f"{row}{chr(64 + seat_pos)}"
                    
                    if seat_pos in [1, 6]:  # Window seats
                        seat_type = 'window'
                    elif seat_pos in [3, 4]:  # Aisle seats
                        seat_type = 'aisle'
                    else:  # Middle seats
                        seat_type = 'middle'
                    
                    Seat.objects.create(
                        vehicle=vehicle,
                        seat_number=seat_number,
                        seat_type=seat_type,
                        is_available=True
                    )
