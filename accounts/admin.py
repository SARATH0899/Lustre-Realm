from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Address


class AddressInline(admin.StackedInline):
    model = Address
    extra = 0


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('phone_number', 'date_of_birth', 'profile_picture')
        }),
    )
    inlines = [AddressInline]
    list_display = ['username', 'email', 'first_name', 'last_name', 'phone_number', 'is_active']
    list_filter = ['is_active', 'is_staff', 'date_joined']


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'street_address', 'city', 'state', 'zip_code', 'is_default']
    list_filter = ['city', 'state', 'is_default']
    search_fields = ['user__username', 'city', 'state']
