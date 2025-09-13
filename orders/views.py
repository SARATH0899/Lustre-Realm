from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View, ListView, DetailView
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db import transaction
from django.core.exceptions import ValidationError
from cart.models import Cart, CartItem
from products.models import Product
from .models import Order, OrderItem
from decimal import Decimal
import json


class CheckoutView(LoginRequiredMixin, View):
    template_name = 'orders/checkout.html'
    
    def get(self, request):
        try:
            cart, created = Cart.objects.get_or_create(user=request.user)
            cart_items = cart.items.all().select_related('product', 'product__category').prefetch_related('product__images')
            
            if not cart_items.exists():
                messages.warning(request, 'Your cart is empty. Add some items before checkout.')
                return redirect('cart:view')
            
            # Calculate totals
            subtotal = sum(item.get_total_price() for item in cart_items)
            tax_rate = Decimal('0.08')  # 8% tax
            tax_amount = subtotal * tax_rate
            shipping = Decimal('0.00')  # Free shipping
            total = subtotal + tax_amount + shipping
            
            context = {
                'cart_items': cart_items,
                'subtotal': subtotal,
                'tax_amount': tax_amount,
                'tax_rate': tax_rate * 100,  # Convert to percentage
                'shipping': shipping,
                'total': total,
            }
            
            return render(request, self.template_name, context)
            
        except Exception as e:
            messages.error(request, 'There was an error accessing your cart.')
            return redirect('cart:view')


class OrderCreateView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            with transaction.atomic():
                cart, created = Cart.objects.get_or_create(user=request.user)
                cart_items = cart.items.select_for_update().select_related('product')
                
                if not cart_items.exists():
                    return JsonResponse({'success': False, 'message': 'Your cart is empty'})
                
                # Validate stock availability with database locks
                for item in cart_items:
                    product = Product.objects.select_for_update().get(id=item.product.id)
                    if not product.in_stock or item.quantity > product.stock_quantity:
                        return JsonResponse({
                            'success': False, 
                            'message': f'{product.name} is not available in the requested quantity'
                        })
                
                # Get form data
                shipping_address = request.POST.get('shipping_address', '').strip()
                billing_address = request.POST.get('billing_address', '').strip()
                phone_number = request.POST.get('phone_number', '').strip()
                special_instructions = request.POST.get('special_instructions', '').strip()
                payment_method = request.POST.get('payment_method', 'card')
                
                # Basic validation
                if not shipping_address:
                    return JsonResponse({'success': False, 'message': 'Shipping address is required'})
                if not billing_address:
                    billing_address = shipping_address  # Use shipping as billing if not provided
                
                # Calculate totals
                subtotal = sum(item.get_total_price() for item in cart_items)
                tax_rate = Decimal('0.08')
                tax_amount = subtotal * tax_rate
                shipping_cost = Decimal('0.00')
                total_amount = subtotal + tax_amount + shipping_cost
                
                # Create order
                order = Order.objects.create(
                    user=request.user,
                    status='pending',
                    total_amount=total_amount,
                    shipping_address=shipping_address,
                    billing_address=billing_address,
                    phone_number=phone_number,
                    payment_method=payment_method,
                    payment_status='pending',
                    special_instructions=special_instructions
                )
                
                # Create order items and update stock atomically
                for item in cart_items:
                    # Get locked product instance
                    product = Product.objects.select_for_update().get(id=item.product.id)
                    
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=item.quantity,
                        price=product.discounted_price
                    )
                    
                    # Update product stock atomically
                    product.stock_quantity -= item.quantity
                    product.save()
                
                # Clear cart
                cart.items.all().delete()
                
                # DEMO ONLY: Mark as paid for demonstration purposes
                # In production, integrate with Stripe/PayPal and verify payment
                order.payment_status = 'pending_demo'  # Changed to indicate demo status
                order.status = 'processing'
                order.save()
                
                return JsonResponse({
                    'success': True, 
                    'message': 'Order placed successfully!',
                    'order_id': order.id,
                    'redirect_url': f'/orders/confirmation/{order.id}/'
                })
                
        except Exception as e:
            return JsonResponse({'success': False, 'message': 'An error occurred while processing your order'})


class OrderSuccessView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/order_confirmation.html'
    context_object_name = 'order'
    pk_url_kwarg = 'order_number'
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related(
            'items__product__images', 'items__product__category'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.object
        
        # Calculate breakdown
        subtotal = sum(item.get_total_price() for item in order.items.all())
        tax_amount = subtotal * Decimal('0.08')
        
        context.update({
            'subtotal': subtotal,
            'tax_amount': tax_amount,
            'shipping': Decimal('0.00'),
            'estimated_delivery': order.estimated_delivery_date(),
        })
        
        return context


class OrderHistoryView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/order_history.html'
    context_object_name = 'orders'
    paginate_by = 10
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related(
            'items__product__images'
        )


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'
    pk_url_kwarg = 'order_number'
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related(
            'items__product__images', 'items__product__category'
        )
