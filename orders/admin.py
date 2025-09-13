from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['total_price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'total_amount', 'status', 'order_date']
    list_filter = ['status', 'order_date']
    search_fields = ['order_number', 'user__username', 'user__email']
    readonly_fields = ['order_number', 'order_date']
    inlines = [OrderItemInline]
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'total_amount', 'status')
        }),
        ('Shipping', {
            'fields': ('shipping_address',)
        }),
        ('Dates', {
            'fields': ('order_date', 'delivery_date')
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price', 'total_price']
    list_filter = ['order__status', 'order__order_date']
    search_fields = ['order__order_number', 'product__name']
