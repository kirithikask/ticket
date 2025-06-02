from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.http import JsonResponse
from .models import Schedule, Seat, Route, TransportationType
from datetime import datetime

class SearchView(ListView):
    model = Schedule
    template_name = 'transportation/search.html'
    context_object_name = 'schedules'
    paginate_by = 10

    def get_queryset(self):
        queryset = Schedule.objects.filter(status='scheduled')

        origin = self.request.GET.get('origin')
        destination = self.request.GET.get('destination')
        departure_date = self.request.GET.get('departure_date')
        transport_type = self.request.GET.get('transport_type')

        if origin:
            queryset = queryset.filter(route__origin__icontains=origin)
        if destination:
            queryset = queryset.filter(route__destination__icontains=destination)
        if departure_date:
            queryset = queryset.filter(departure_date=departure_date)
        if transport_type:
            queryset = queryset.filter(route__transportation_type__name=transport_type)

        return queryset.order_by('departure_date', 'departure_time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['transportation_types'] = TransportationType.objects.all()
        context['search_params'] = {
            'origin': self.request.GET.get('origin', ''),
            'destination': self.request.GET.get('destination', ''),
            'departure_date': self.request.GET.get('departure_date', ''),
            'transport_type': self.request.GET.get('transport_type', ''),
        }
        return context

class ScheduleDetailView(DetailView):
    model = Schedule
    template_name = 'transportation/schedule_detail.html'
    context_object_name = 'schedule'
    pk_url_kwarg = 'schedule_id'

class SeatMapView(DetailView):
    model = Schedule
    template_name = 'transportation/seat_map.html'
    context_object_name = 'schedule'
    pk_url_kwarg = 'schedule_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        schedule = self.get_object()
        seats = Seat.objects.filter(vehicle=schedule.vehicle).order_by('seat_number')
        context['seats'] = seats
        return context

    def post(self, request, *args, **kwargs):
        # AJAX endpoint for seat selection
        schedule = self.get_object()
        seat_ids = request.POST.getlist('seat_ids')

        selected_seats = Seat.objects.filter(
            id__in=seat_ids,
            vehicle=schedule.vehicle,
            is_available=True
        )

        seat_data = [{
            'id': seat.id,
            'seat_number': seat.seat_number,
            'seat_type': seat.seat_type,
        } for seat in selected_seats]

        return JsonResponse({'seats': seat_data})
