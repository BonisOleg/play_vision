from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from .models import Plan, Subscription


class PricingView(TemplateView):
    """Pricing page with subscription plans"""
    template_name = 'subscriptions/pricing.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['plans'] = Plan.objects.filter(is_active=True).order_by('price')
        
        # Check if user has active subscription
        if self.request.user.is_authenticated:
            context['current_subscription'] = self.request.user.subscriptions.filter(
                status='active'
            ).first()
        
        return context


class SubscribeView(LoginRequiredMixin, View):
    """Subscribe to a plan"""
    
    def post(self, request, plan_id):
        plan = get_object_or_404(Plan, id=plan_id, is_active=True)
        
        # Add subscription to cart
        from apps.cart.services import CartService
        cart_service = CartService(request)
        success, message = cart_service.add_subscription(plan)
        
        if success:
            messages.success(request, message)
            return redirect('cart:cart')
        else:
            messages.error(request, message)
            return redirect('subscriptions:pricing')


class CancelSubscriptionView(LoginRequiredMixin, View):
    """Cancel user subscription"""
    
    def post(self, request):
        subscription = request.user.subscriptions.filter(status='active').first()
        
        if subscription:
            subscription.status = 'cancelled'
            subscription.save()
            messages.success(request, 'Підписку скасовано')
        else:
            messages.error(request, 'Активна підписка не знайдена')
        
        return redirect('cabinet:subscription')


class ReactivateSubscriptionView(LoginRequiredMixin, View):
    """Reactivate cancelled subscription"""
    
    def post(self, request):
        # Basic implementation - extend as needed
        messages.info(request, 'Функція реактивації буде доступна незабаром')
        return redirect('cabinet:subscription')


class PlanDetailView(TemplateView):
    """Plan detail page"""
    template_name = 'subscriptions/plan_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        plan_id = kwargs.get('plan_id')
        context['plan'] = get_object_or_404(Plan, id=plan_id, is_active=True)
        return context
