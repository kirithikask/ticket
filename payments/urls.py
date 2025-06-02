from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('process/<str:booking_id>/', views.ProcessPaymentView.as_view(), name='process_payment'),
    path('success/<str:payment_id>/', views.PaymentSuccessView.as_view(), name='payment_success'),
    path('failed/<str:payment_id>/', views.PaymentFailedView.as_view(), name='payment_failed'),
    path('refund/<str:payment_id>/', views.RefundView.as_view(), name='refund'),
]
