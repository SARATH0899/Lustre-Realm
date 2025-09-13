from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponse


class HomeView(TemplateView):
    def get(self, request):
        return HttpResponse('<h1>Ornaments Store - Home</h1><p>Django server is running successfully!</p><a href="/admin/">Admin Panel</a>')


class AboutView(TemplateView):
    def get(self, request):
        return HttpResponse('<h1>About Us</h1>')


class ServicesView(TemplateView):
    def get(self, request):
        return HttpResponse('<h1>Services</h1>')


class ContactView(TemplateView):
    def get(self, request):
        return HttpResponse('<h1>Contact</h1>')


class PrivacyPolicyView(TemplateView):
    def get(self, request):
        return HttpResponse('<h1>Privacy Policy</h1>')


class TermsView(TemplateView):
    def get(self, request):
        return HttpResponse('<h1>Terms of Service</h1>')
