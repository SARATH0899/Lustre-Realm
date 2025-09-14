from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from products.models import Product
from .models import Cart, CartItem
import json


class CartView(View):
    def get(self, request):
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
            cart_items = cart.items.all().select_related('product', 'product__category').prefetch_related('product__images')
        else:
            # Handle session-based cart for anonymous users
            cart_items = self._get_session_cart_items(request)
            
        context = {
            'cart_items': cart_items,
            'cart_total': sum(item.total_price for item in cart_items) if cart_items else 0
        }
        return render(request, 'cart/cart.html', context)
    
    def _get_session_cart_items(self, request):
        cart_data = request.session.get('cart', {})
        cart_items = []
        
        for product_id, quantity in cart_data.items():
            try:
                product = Product.objects.get(id=int(product_id), is_active=True)
                # Create a mock cart item object for session-based cart
                class SessionCartItem:
                    def __init__(self, product, quantity):
                        self.product = product
                        self.quantity = quantity
                    
                    @property
                    def total_price(self):
                        return self.product.discounted_price * self.quantity
                
                cart_items.append(SessionCartItem(product, quantity))
            except Product.DoesNotExist:
                pass
                
        return cart_items


class AddToCartView(View):
    def post(self, request, product_id):
        try:
            quantity = int(request.POST.get('quantity', 1))
            
            product = get_object_or_404(Product, id=product_id, is_active=True)
            
            if not product.in_stock:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'message': 'Product is out of stock'})
                messages.error(request, 'Product is out of stock')
                return redirect('products:detail', pk=product_id)
            
            if quantity > product.stock_quantity:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'message': f'Only {product.stock_quantity} items available'})
                messages.error(request, f'Only {product.stock_quantity} items available')
                return redirect('products:detail', pk=product_id)
            
            if request.user.is_authenticated:
                cart, created = Cart.objects.get_or_create(user=request.user)
                cart_item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    product=product,
                    defaults={'quantity': quantity}
                )
                
                if not created:
                    new_quantity = cart_item.quantity + quantity
                    if new_quantity > product.stock_quantity:
                        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                            return JsonResponse({'success': False, 'message': f'Cannot add more. Only {product.stock_quantity} items available'})
                        messages.error(request, f'Cannot add more. Only {product.stock_quantity} items available')
                        return redirect('products:detail', pk=product_id)
                    cart_item.quantity = new_quantity
                    cart_item.save()
                
                cart_count = cart.items.count()
            else:
                # Handle session-based cart for anonymous users
                cart = request.session.get('cart', {})
                product_id_str = str(product_id)
                
                if product_id_str in cart:
                    new_quantity = cart[product_id_str] + quantity
                    if new_quantity > product.stock_quantity:
                        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                            return JsonResponse({'success': False, 'message': f'Cannot add more. Only {product.stock_quantity} items available'})
                        messages.error(request, f'Cannot add more. Only {product.stock_quantity} items available')
                        return redirect('products:detail', pk=product_id)
                    cart[product_id_str] = new_quantity
                else:
                    cart[product_id_str] = quantity
                
                request.session['cart'] = cart
                cart_count = len(cart)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True, 
                    'message': f'{product.name} added to cart successfully!',
                    'cart_count': cart_count
                })
            
            messages.success(request, f'{product.name} added to cart successfully!')
            return redirect('products:detail', pk=product_id)
            
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'An error occurred while adding to cart'})
            messages.error(request, 'An error occurred while adding to cart')
            return redirect('products:detail', pk=product_id)


class RemoveFromCartView(View):
    def post(self, request, item_id):
        try:
            if request.user.is_authenticated:
                cart = get_object_or_404(Cart, user=request.user)
                cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
                cart_item.delete()
                
                cart_count = cart.items.count()
                cart_total = sum(item.get_total_price() for item in cart.items.all())
            else:
                # Handle session-based cart for anonymous users
                cart = request.session.get('cart', {})
                product_id_str = str(item_id)
                
                if product_id_str in cart:
                    del cart[product_id_str]
                    request.session['cart'] = cart
                
                cart_count = len(cart)
                cart_total = sum(Product.objects.get(id=int(pid)).discounted_price * qty 
                               for pid, qty in cart.items()) if cart else 0
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'cart_count': cart_count,
                    'cart_total': float(cart_total)
                })
            
            messages.success(request, 'Item removed from cart')
            return redirect('cart:view')
            
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'An error occurred while removing from cart'})
            messages.error(request, 'An error occurred while removing from cart')
            return redirect('cart:view')


class UpdateCartView(View):
    def post(self, request, item_id):
        try:
            quantity = int(request.POST.get('quantity', 1))
            
            if request.user.is_authenticated:
                cart = get_object_or_404(Cart, user=request.user)
                cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
                
                if quantity > cart_item.product.stock_quantity:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'message': f'Only {cart_item.product.stock_quantity} items available'})
                    messages.error(request, f'Only {cart_item.product.stock_quantity} items available')
                    return redirect('cart:view')
                
                cart_item.quantity = quantity
                cart_item.save()
                
                item_total = cart_item.get_total_price()
                cart_total = sum(item.get_total_price() for item in cart.items.all())
            else:
                # Handle session-based cart for anonymous users
                cart = request.session.get('cart', {})
                product_id_str = str(item_id)
                
                if product_id_str in cart:
                    product = Product.objects.get(id=int(product_id_str))
                    if quantity > product.stock_quantity:
                        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                            return JsonResponse({'success': False, 'message': f'Only {product.stock_quantity} items available'})
                        messages.error(request, f'Only {product.stock_quantity} items available')
                        return redirect('cart:view')
                    
                    cart[product_id_str] = quantity
                    request.session['cart'] = cart
                    
                    item_total = product.discounted_price * quantity
                    cart_total = sum(Product.objects.get(id=int(pid)).discounted_price * qty 
                                   for pid, qty in cart.items())
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'item_total': float(item_total),
                    'cart_total': float(cart_total)
                })
            
            messages.success(request, 'Cart updated successfully')
            return redirect('cart:view')
            
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'An error occurred while updating cart'})
            messages.error(request, 'An error occurred while updating cart')
            return redirect('cart:view')


class ClearCartView(View):
    def post(self, request):
        try:
            if request.user.is_authenticated:
                cart = get_object_or_404(Cart, user=request.user)
                cart.items.all().delete()
            else:
                # Clear session-based cart
                request.session['cart'] = {}
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Cart cleared successfully'})
            
            messages.success(request, 'Cart cleared successfully')
            return redirect('cart:view')
            
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'An error occurred while clearing cart'})
            messages.error(request, 'An error occurred while clearing cart')
            return redirect('cart:view')
