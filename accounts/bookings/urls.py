from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('create/', views.CreateBookingView.as_view(), name='create_booking'),
    path('confirm/<str:booking_id>/', views.ConfirmBookingView.as_view(), name='confirm_booking'),
    path('my-bookings/', views.MyBookingsView.as_view(), name='my_bookings'),
    path('booking/<str:booking_id>/', views.BookingDetailView.as_view(), name='booking_detail'),
    path('cancel/<str:booking_id>/', views.CancelBookingView.as_view(), name='cancel_booking'),
]
