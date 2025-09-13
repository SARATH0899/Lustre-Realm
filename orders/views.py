from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View, ListView, DetailView
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.core.exceptions import ValidationError
from django.conf import settings
from cart.models import Cart, CartItem
from products.models import Product
from .models import Order, OrderItem
from decimal import Decimal
import json
import razorpay

# Initialize Razorpay client
razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET)
)


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
    pk_url_kwarg = 'order_id'
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related(
            'items__product__images', 'items__product__category'
        )


# Razorpay Payment Views
class CreateRazorpayOrderView(LoginRequiredMixin, View):
    """Create a Razorpay order for payment"""
    def post(self, request):
        try:
            cart, created = Cart.objects.get_or_create(user=request.user)
            cart_items = cart.items.all().select_related('product')
            
            if not cart_items.exists():
                return JsonResponse({'error': 'Cart is empty'}, status=400)
            
            # Get form data
            shipping_address = request.POST.get('shipping_address', '').strip()
            billing_address = request.POST.get('billing_address', '').strip()
            phone_number = request.POST.get('phone_number', '').strip()
            special_instructions = request.POST.get('special_instructions', '').strip()
            
            # Validate required fields
            if not shipping_address:
                return JsonResponse({'error': 'Shipping address is required'}, status=400)
            
            # Calculate order total
            subtotal = sum(item.get_total_price() for item in cart_items)
            tax_rate = Decimal('0.08')  # 8% tax
            tax_amount = subtotal * tax_rate
            total = subtotal + tax_amount
            
            # Convert to paise (Razorpay works in smallest currency unit)
            amount_in_paise = int(total * 100)
            
            # Create Razorpay order
            order_data = {
                'amount': amount_in_paise,
                'currency': 'INR',
                'payment_capture': '0',  # Manual capture - capture after stock validation
                'notes': {
                    'user_id': str(request.user.id),
                    'cart_items_count': cart_items.count()
                }
            }
            
            razorpay_order = razorpay_client.order.create(data=order_data)
            
            # Store order details in session for verification
            request.session['pending_order'] = {
                'razorpay_order_id': razorpay_order['id'],
                'amount': amount_in_paise,
                'cart_items': [{'product_id': item.product.id, 'quantity': item.quantity} for item in cart_items],
                'shipping_address': shipping_address,
                'billing_address': billing_address or shipping_address,
                'phone_number': phone_number,
                'special_instructions': special_instructions
            }
            
            return JsonResponse({
                'order_id': razorpay_order['id'],
                'amount': amount_in_paise,
                'currency': 'INR',
                'key_id': settings.RAZORPAY_API_KEY,
                'name': 'Ornaments Store',
                'description': f'Payment for {cart_items.count()} item(s)',
                'prefill': {
                    'name': request.user.get_full_name() or request.user.username,
                    'email': request.user.email,
                    'contact': phone_number
                },
                'theme': {
                    'color': '#D4AF37'  # Gold theme
                }
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class RazorpayPaymentHandlerView(View):
    """Handle Razorpay payment callback"""
    def post(self, request):
        try:
            # Get payment details from Razorpay
            payment_id = request.POST.get('razorpay_payment_id', '')
            order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            
            if not all([payment_id, order_id, signature]):
                return JsonResponse({'error': 'Missing payment details'}, status=400)
            
            # Check for idempotency - prevent duplicate orders
            existing_order = Order.objects.filter(
                razorpay_payment_id=payment_id
            ).first()
            if existing_order:
                return JsonResponse({
                    'success': True,
                    'order_id': existing_order.id,
                    'payment_id': payment_id,
                    'redirect_url': f'/orders/confirmation/{existing_order.id}/',
                    'message': 'Order already processed'
                })
            
            # Verify signature for security
            params_dict = {
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            
            result = razorpay_client.utility.verify_payment_signature(params_dict)
            
            if result is None:  # Signature verified successfully
                # Fetch payment details from Razorpay for reconciliation
                payment_details = razorpay_client.payment.fetch(payment_id)
                paid_amount_paise = payment_details.get('amount', 0)
                paid_amount = Decimal(str(paid_amount_paise / 100))  # Convert from paise to INR
                # Get pending order from session
                pending_order = request.session.get('pending_order')
                if not pending_order or pending_order['razorpay_order_id'] != order_id:
                    return JsonResponse({'error': 'Invalid order session'}, status=400)
                
                # Get user from request (ensure they're logged in)
                if not request.user.is_authenticated:
                    return JsonResponse({'error': 'User not authenticated'}, status=401)
                
                # Create the actual order in database
                with transaction.atomic():
                    cart, created = Cart.objects.get_or_create(user=request.user)
                    
                    # Calculate totals and validate products
                    subtotal = Decimal('0')
                    cart_items = []
                    
                    for item_data in pending_order['cart_items']:
                        try:
                            product = Product.objects.select_for_update().get(id=item_data['product_id'])
                            quantity = item_data['quantity']
                            
                            if not product.in_stock or quantity > product.stock_quantity:
                                return JsonResponse({'error': f'{product.name} is out of stock'}, status=400)
                            
                            cart_items.append({
                                'product': product,
                                'quantity': quantity,
                                'price': product.discounted_price
                            })
                            
                            subtotal += product.discounted_price * quantity
                            
                        except Product.DoesNotExist:
                            return JsonResponse({'error': f'Product not found'}, status=400)
                    
                    tax_rate = Decimal('0.08')
                    tax_amount = subtotal * tax_rate
                    total = subtotal + tax_amount
                    
                    # Payment reconciliation - verify amounts match
                    expected_amount_paise = int(total * 100)
                    if paid_amount_paise != expected_amount_paise:
                        return JsonResponse({
                            'error': f'Payment amount mismatch. Expected: ₹{total}, Paid: ₹{paid_amount}'
                        }, status=400)
                    
                    # Manually capture the payment after stock validation
                    try:
                        capture_result = razorpay_client.payment.capture(
                            payment_id, 
                            paid_amount_paise
                        )
                        if capture_result.get('status') != 'captured':
                            return JsonResponse({'error': 'Payment capture failed'}, status=400)
                    except Exception as capture_error:
                        return JsonResponse({
                            'error': f'Payment capture failed: {str(capture_error)}'
                        }, status=400)
                    
                    # Create order with Razorpay payment details
                    order = Order.objects.create(
                        user=request.user,
                        total_amount=total,
                        tax_amount=tax_amount,
                        payment_method=payment_details.get('method', 'card'),
                        payment_status='paid',
                        status='processing',
                        shipping_address=pending_order.get('shipping_address', ''),
                        billing_address=pending_order.get('billing_address', ''),
                        phone_number=pending_order.get('phone_number', ''),
                        special_instructions=pending_order.get('special_instructions', ''),
                        # Razorpay audit trail
                        razorpay_order_id=order_id,
                        razorpay_payment_id=payment_id,
                        razorpay_signature=signature,
                        razorpay_amount_paid=paid_amount
                    )
                    
                    # Create order items and update stock
                    for item in cart_items:
                        OrderItem.objects.create(
                            order=order,
                            product=item['product'],
                            quantity=item['quantity'],
                            price=item['price']
                        )
                        
                        # Update product stock
                        item['product'].stock_quantity -= item['quantity']
                        item['product'].save()
                    
                    # Clear cart
                    cart.items.all().delete()
                    
                    # Clear session
                    if 'pending_order' in request.session:
                        del request.session['pending_order']
                    
                    return JsonResponse({
                        'success': True,
                        'order_id': order.id,
                        'payment_id': payment_id,
                        'redirect_url': f'/orders/confirmation/{order.id}/'
                    })
                    
            else:
                return JsonResponse({'error': 'Payment verification failed'}, status=400)
                
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Payment processing failed: {str(e)}'}, status=500)
    


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

