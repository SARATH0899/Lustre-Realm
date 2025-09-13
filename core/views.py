from django.shortcuts import render
from django.views.generic import TemplateView, CreateView
from django.contrib import messages
from django.urls import reverse_lazy
from .models import Contact
from .forms import ContactForm


class HomeView(TemplateView):
    template_name = 'core/home.html'


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
