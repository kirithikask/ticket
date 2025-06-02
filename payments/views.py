from django.shortcuts import get_object_or_404, redirect
from django.views.generic import CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import Payment, PaymentHistory
from bookings.models import Booking
import uuid
import random
import decimal
from decimal import Decimal
try:
    from bson.decimal128 import Decimal128
except ImportError:
    Decimal128 = None

class ProcessPaymentView(LoginRequiredMixin, CreateView):
    model = Payment
    template_name = 'payments/process_payment.html'
    fields = ['payment_method']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        booking_id = self.kwargs.get('booking_id')
        context['booking'] = get_object_or_404(Booking, booking_id=booking_id, user=self.request.user)
        return context

    def form_valid(self, form):
        booking_id = self.kwargs.get('booking_id')
        try:
            booking = get_object_or_404(Booking, booking_id=booking_id, user=self.request.user)
            
            # Validate payment method is selected
            if not form.cleaned_data.get('payment_method'):
                messages.error(self.request, 'Please select a payment method')
                return self.form_invalid(form)

            # Check if payment already exists for this booking
            existing_payment = Payment.objects.filter(booking=booking).first()
            if existing_payment:
                # If payment already exists, redirect based on its status
                if existing_payment.payment_status == 'completed':
                    messages.info(self.request, 'Payment has already been completed for this booking.')
                    return redirect('payments:payment_success', payment_id=existing_payment.payment_id)
                elif existing_payment.payment_status == 'failed':
                    # Allow retry by updating the existing payment
                    payment = existing_payment
                    payment.payment_method = form.cleaned_data.get('payment_method')
                    payment.payment_status = 'processing'
                else:
                    # Payment is pending or processing, redirect to current status
                    messages.info(self.request, 'Payment is already being processed for this booking.')
                    return redirect('payments:payment_success', payment_id=existing_payment.payment_id)
            else:
                # Create new payment
                payment = form.save(commit=False)
                payment.booking = booking
                payment.payment_id = f"PAY{str(uuid.uuid4())[:8].upper()}"
            
            # Handle the booking.total_amount conversion to Decimal
            try:
                # Print debug information
                print(f"Original total_amount: {booking.total_amount}, type: {type(booking.total_amount)}")

                # Convert booking total_amount to proper Decimal
                if isinstance(booking.total_amount, Decimal):
                    payment.amount = booking.total_amount
                elif Decimal128 and hasattr(booking.total_amount, 'to_decimal'):
                    # Handle MongoDB Decimal128 type
                    payment.amount = booking.total_amount.to_decimal()
                elif Decimal128 and str(type(booking.total_amount)).find('Decimal128') != -1:
                    # Handle MongoDB Decimal128 type (alternative check)
                    payment.amount = Decimal(str(booking.total_amount))
                elif isinstance(booking.total_amount, (int, float)):
                    payment.amount = Decimal(str(booking.total_amount))
                elif isinstance(booking.total_amount, str):
                    # Remove any quotes and non-numeric characters except decimal point
                    import re
                    cleaned_amount = re.sub(r'[^\d.]', '', str(booking.total_amount).strip('"\''))
                    if cleaned_amount:
                        payment.amount = Decimal(cleaned_amount)
                    else:
                        raise ValueError("Invalid amount string")
                else:
                    # Try direct conversion as last resort
                    payment.amount = Decimal(str(booking.total_amount))

                # Validate the amount is positive
                if payment.amount <= 0:
                    raise ValueError("Amount must be positive")

                print(f"Successfully converted amount: {payment.amount}")

            except (ValueError, TypeError, decimal.InvalidOperation) as e:
                print(f"Amount conversion error: {e}")
                # Log the error and use booking total_amount as fallback
                try:
                    # Try to extract numeric value from booking.total_amount
                    amount_str = str(booking.total_amount).replace('"', '').replace("'", "")
                    payment.amount = Decimal(amount_str)
                except:
                    # Final fallback - calculate from schedule price
                    seat_count = booking.booked_seats.count() if hasattr(booking, 'booked_seats') else 1
                    payment.amount = Decimal(str(booking.schedule.price)) * seat_count + Decimal('2.00')

                print(f"Fallback amount used: {payment.amount}")
            
            payment.transaction_id = f"TXN{random.randint(100000, 999999)}"
            payment.payment_gateway = "Mock Gateway"
            payment.payment_status = 'processing'
            payment.save()
            
            # Simulate payment processing
            success_rate = 1.0  # 100% success rate for testing
            if random.random() < success_rate:
                payment.payment_status = 'completed'
                booking.status = 'confirmed'
                booking.save()
                messages.success(self.request, 'Payment processed successfully!')
                redirect_url = 'payments:payment_success'
            else:
                payment.payment_status = 'failed'
                messages.error(self.request, 'Payment failed. Please try again.')
                redirect_url = 'payments:payment_failed'

            payment.save()

            # Create payment history
            PaymentHistory.objects.create(
                payment=payment,
                status_change=f"Payment {payment.payment_status}",
                changed_by=self.request.user,
                change_reason="Payment processing"
            )

            return redirect(redirect_url, payment_id=payment.payment_id)
            
        except Exception as e:
            import traceback
            print(f"Payment processing error: {str(e)}")
            print(traceback.format_exc())
            messages.error(self.request, f'An error occurred while processing your payment: {str(e)}')
            return redirect('payments:process_payment', booking_id=booking_id)

class PaymentSuccessView(LoginRequiredMixin, DetailView):
    model = Payment
    template_name = 'payments/payment_success.html'
    context_object_name = 'payment'
    slug_field = 'payment_id'
    slug_url_kwarg = 'payment_id'

class PaymentFailedView(LoginRequiredMixin, DetailView):
    model = Payment
    template_name = 'payments/payment_failed.html'
    context_object_name = 'payment'
    slug_field = 'payment_id'
    slug_url_kwarg = 'payment_id'

class RefundView(LoginRequiredMixin, DetailView):
    model = Payment
    template_name = 'payments/refund.html'
    context_object_name = 'payment'
    slug_field = 'payment_id'
    slug_url_kwarg = 'payment_id'

    def post(self, request, *args, **kwargs):
        payment = self.get_object()
        refund_reason = request.POST.get('refund_reason', '')

        if payment.payment_status == 'completed':
            payment.payment_status = 'refunded'
            payment.refund_amount = payment.amount
            payment.refund_reason = refund_reason
            payment.save()

            # Update booking status
            payment.booking.status = 'cancelled'
            payment.booking.save()

            # Create payment history
            PaymentHistory.objects.create(
                payment=payment,
                status_change="Payment refunded",
                changed_by=request.user,
                change_reason=refund_reason
            )

            messages.success(request, 'Refund processed successfully!')
        else:
            messages.error(request, 'This payment cannot be refunded.')

        return redirect('bookings:my_bookings')
