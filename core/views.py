from django.shortcuts import render
from django.views.generic import TemplateView, CreateView
from django.contrib import messages
from django.urls import reverse_lazy
from .models import Contact
from .forms import ContactForm


class HomeView(TemplateView):
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Import here to avoid circular imports
        from products.models import Product, Category
        
        # Get featured products for carousel
        context['featured_products'] = Product.objects.filter(
            is_active=True, is_featured=True
        ).select_related('category').prefetch_related('images')[:8]
        
        # Get recent products for carousel
        context['recent_products'] = Product.objects.filter(
            is_active=True
        ).select_related('category').prefetch_related('images').order_by('-created_at')[:8]
        
        # Get categories for display
        context['categories'] = Category.objects.filter(is_active=True)[:6]
        
        return context


class AboutView(TemplateView):
    template_name = 'core/about.html'


class ServicesView(TemplateView):
    template_name = 'core/services.html'


class ContactView(CreateView):
    model = Contact
    form_class = ContactForm
    template_name = 'core/contact.html'
    success_url = reverse_lazy('core:contact')
    
    def form_valid(self, form):
        messages.success(self.request, 'Thank you for your message! We will get back to you soon.')
        return super().form_valid(form)


class PrivacyPolicyView(TemplateView):
    template_name = 'core/privacy.html'


class TermsView(TemplateView):
    template_name = 'core/terms.html'


class ShippingView(TemplateView):
    template_name = 'core/shipping.html'
