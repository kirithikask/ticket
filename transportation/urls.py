from django.urls import path
from . import views

app_name = 'transportation'

urlpatterns = [
    path('search/', views.SearchView.as_view(), name='search'),
    path('schedule/<int:schedule_id>/', views.ScheduleDetailView.as_view(), name='schedule_detail'),
    path('seat-map/<int:schedule_id>/', views.SeatMapView.as_view(), name='seat_map'),
]
