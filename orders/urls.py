from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('success/<str:order_number>/', views.OrderSuccessView.as_view(), name='success'),
    path('history/', views.OrderHistoryView.as_view(), name='history'),
    path('detail/<str:order_number>/', views.OrderDetailView.as_view(), name='detail'),
]