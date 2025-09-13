from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponse


class CartView(TemplateView):
    def get(self, request):
        return HttpResponse('<h1>Shopping Cart</h1><p>Coming soon</p>')


class AddToCartView(TemplateView):
    def get(self, request, product_id):
        return HttpResponse(f'<h1>Add to Cart - Product {product_id}</h1><p>Coming soon</p>')


class RemoveFromCartView(TemplateView):
    def get(self, request, item_id):
        return HttpResponse(f'<h1>Remove from Cart - Item {item_id}</h1><p>Coming soon</p>')


class UpdateCartView(TemplateView):
    def get(self, request, item_id):
        return HttpResponse(f'<h1>Update Cart - Item {item_id}</h1><p>Coming soon</p>')


class ClearCartView(TemplateView):
    def get(self, request):
        return HttpResponse('<h1>Clear Cart</h1><p>Coming soon</p>')
