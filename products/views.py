from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponse


class ProductListView(TemplateView):
    def get(self, request):
        return HttpResponse('<h1>Products</h1><p>Coming soon</p>')


class ProductDetailView(TemplateView):
    def get(self, request, pk):
        return HttpResponse(f'<h1>Product Detail {pk}</h1><p>Coming soon</p>')


class ProductByCategoryView(TemplateView):
    def get(self, request, category_id):
        return HttpResponse(f'<h1>Products in Category {category_id}</h1><p>Coming soon</p>')


class ProductSearchView(TemplateView):
    def get(self, request):
        return HttpResponse('<h1>Product Search</h1><p>Coming soon</p>')
