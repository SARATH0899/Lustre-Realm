from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('success/<str:order_number>/', views.OrderSuccessView.as_view(), name='success'),
    path('history/', views.OrderHistoryView.as_view(), name='history'),
    path('detail/<str:order_number>/', views.OrderDetailView.as_view(), name='detail'),
    
    # Razorpay Payment URLs
    path('create-razorpay-order/', views.CreateRazorpayOrderView.as_view(), name='create_razorpay_order'),
    path('razorpay-payment-handler/', views.RazorpayPaymentHandlerView.as_view(), name='razorpay_payment_handler'),
    path('confirmation/<int:order_id>/', views.OrderSuccessView.as_view(), name='confirmation'),
]