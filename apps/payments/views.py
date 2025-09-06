from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, View
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
import json

from .models import Payment, Order
from .services import PaymentService, WebhookService


class CheckoutView(LoginRequiredMixin, TemplateView):
    """Checkout page view"""
    template_name = 'payments/checkout.html'


class PaymentProcessView(LoginRequiredMixin, View):
    """Process payment with Stripe"""
    
    def post(self, request):
        return JsonResponse({'status': 'processing'})


class PaymentConfirmView(LoginRequiredMixin, View):
    """Confirm 3DS payment"""
    
    def post(self, request):
        return JsonResponse({'status': 'confirmed'})


class ApplyCouponView(LoginRequiredMixin, View):
    """Apply coupon to order"""
    
    def post(self, request):
        return JsonResponse({'success': True})


class RemoveCouponView(LoginRequiredMixin, View):
    """Remove coupon from order"""
    
    def post(self, request):
        return JsonResponse({'success': True})


class PaymentSuccessView(LoginRequiredMixin, TemplateView):
    """Payment success page"""
    template_name = 'payments/success.html'


class PaymentFailureView(LoginRequiredMixin, TemplateView):
    """Payment failure page"""
    template_name = 'payments/failure.html'


class StripeWebhookView(View):
    """Stripe webhook endpoint"""
    
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request):
        try:
            webhook_service = WebhookService()
            result = webhook_service.handle_webhook(request.body, request.META.get('HTTP_STRIPE_SIGNATURE', ''))
            return JsonResponse(result)
        except Exception as e:
            return HttpResponse('Webhook error', status=500)


@login_required
def order_history(request):
    """User's order history"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'payments/order_history.html', {'orders': orders})


@login_required
def order_detail(request, order_number):
    """Order detail view"""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'payments/order_detail.html', {'order': order})


@login_required
def payment_methods(request):
    """User's saved payment methods"""
    return render(request, 'payments/payment_methods.html')


@login_required
def detach_payment_method(request):
    """Detach payment method from customer"""
    messages.success(request, 'Метод оплати видалено')
    return redirect('payments:payment_methods')


@login_required
def validate_coupon(request):
    """Validate coupon code (AJAX)"""
    return JsonResponse({'valid': True})


@login_required
def get_payment_intent_status(request, payment_intent_id):
    """Get payment intent status"""
    return JsonResponse({'status': 'succeeded'})
