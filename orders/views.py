from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponse


class CheckoutView(TemplateView):
    def get(self, request):
        return HttpResponse('<h1>Checkout</h1><p>Coming soon</p>')


class OrderSuccessView(TemplateView):
    def get(self, request, order_number):
        return HttpResponse(f'<h1>Order Success - {order_number}</h1><p>Coming soon</p>')


class OrderHistoryView(TemplateView):
    def get(self, request):
        return HttpResponse('<h1>Order History</h1><p>Coming soon</p>')


class OrderDetailView(TemplateView):
    def get(self, request, order_number):
        return HttpResponse(f'<h1>Order Detail - {order_number}</h1><p>Coming soon</p>')
