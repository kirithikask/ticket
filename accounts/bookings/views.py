from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse
from .models import Booking, BookingSeat
from transportation.models import Schedule, Seat
from payments.models import Payment
import uuid
from decimal import Decimal

class CreateBookingView(LoginRequiredMixin, CreateView):
    model = Booking
    template_name = 'bookings/create_booking.html'
    fields = ['special_requests']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        schedule_id = self.request.GET.get('schedule_id')
        seat_ids = self.request.GET.getlist('seat_ids')

        if schedule_id:
            context['schedule'] = get_object_or_404(Schedule, id=schedule_id)

        if seat_ids:
            # Get seat information for display
            seats = Seat.objects.filter(id__in=seat_ids)
            context['selected_seats'] = seats
            context['seat_ids'] = seat_ids

            # Calculate total amount
            if schedule_id:
                schedule = context['schedule']
                service_fee = Decimal('2.00')
                subtotal = Decimal(str(schedule.price)) * len(seat_ids)
                context['subtotal'] = subtotal
                context['service_fee'] = service_fee
                context['total_amount'] = subtotal + service_fee

        return context

    def form_valid(self, form):
        schedule_id = self.request.POST.get('schedule_id')
        seat_ids = self.request.POST.getlist('seat_ids')
        passenger_names = self.request.POST.getlist('passenger_names')
        passenger_ages = self.request.POST.getlist('passenger_ages')
        passenger_genders = self.request.POST.getlist('passenger_genders')

        schedule = get_object_or_404(Schedule, id=schedule_id)

        # Create booking
        booking = form.save(commit=False)
        booking.user = self.request.user
        booking.schedule = schedule
        booking.booking_id = str(uuid.uuid4())[:8].upper()

        # Calculate total amount including service fee
        subtotal = Decimal(str(schedule.price)) * len(seat_ids)
        service_fee = Decimal('2.00')
        booking.total_amount = subtotal + service_fee
        booking.save()

        # Create booking seats
        for i, seat_id in enumerate(seat_ids):
            seat = get_object_or_404(Seat, id=seat_id)
            BookingSeat.objects.create(
                booking=booking,
                seat=seat,
                passenger_name=passenger_names[i],
                passenger_age=int(passenger_ages[i]),
                passenger_gender=passenger_genders[i]
            )
            # Mark seat as unavailable
            seat.is_available = False
            seat.save()

        messages.success(self.request, f'Booking {booking.booking_id} created successfully!')
        return redirect('bookings:confirm_booking', booking_id=booking.booking_id)

class ConfirmBookingView(LoginRequiredMixin, DetailView):
    model = Booking
    template_name = 'bookings/confirm_booking.html'
    context_object_name = 'booking'
    slug_field = 'booking_id'
    slug_url_kwarg = 'booking_id'

class MyBookingsView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'bookings/my_bookings.html'
    context_object_name = 'bookings'

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).order_by('-created_at')

class BookingDetailView(LoginRequiredMixin, DetailView):
    model = Booking
    template_name = 'bookings/booking_detail.html'
    context_object_name = 'booking'
    slug_field = 'booking_id'
    slug_url_kwarg = 'booking_id'

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

class CancelBookingView(LoginRequiredMixin, DetailView):
    model = Booking
    template_name = 'bookings/cancel_booking.html'
    context_object_name = 'booking'
    slug_field = 'booking_id'
    slug_url_kwarg = 'booking_id'

    def post(self, request, *args, **kwargs):
        booking = self.get_object()
        if booking.status in ['pending', 'confirmed']:
            booking.status = 'cancelled'
            booking.save()

            # Make seats available again
            for booking_seat in booking.booked_seats.all():
                booking_seat.seat.is_available = True
                booking_seat.seat.save()

            messages.success(request, f'Booking {booking.booking_id} cancelled successfully!')
        else:
            messages.error(request, 'This booking cannot be cancelled.')

        return redirect('bookings:my_bookings')
