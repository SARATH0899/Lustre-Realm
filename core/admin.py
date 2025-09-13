from django.contrib import admin
from .models import Contact


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'date_submitted', 'is_resolved']
    list_filter = ['is_resolved', 'date_submitted']
    search_fields = ['name', 'email', 'subject']
    readonly_fields = ['date_submitted']
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Message', {
            'fields': ('subject', 'message')
        }),
        ('Status', {
            'fields': ('is_resolved', 'date_submitted')
        }),
    )
