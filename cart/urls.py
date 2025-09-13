from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.CartView.as_view(), name='view'),
    path('add/<int:product_id>/', views.AddToCartView.as_view(), name='add'),
    path('remove/<int:item_id>/', views.RemoveFromCartView.as_view(), name='remove'),
    path('update/<int:item_id>/', views.UpdateCartView.as_view(), name='update'),
    path('clear/', views.ClearCartView.as_view(), name='clear'),
]