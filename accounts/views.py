from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponse


class LoginView(TemplateView):
    def get(self, request):
        return HttpResponse('<h1>Login</h1><p>Coming soon</p>')


class LogoutView(TemplateView):
    def get(self, request):
        return HttpResponse('<h1>Logout</h1><p>Coming soon</p>')


class RegisterView(TemplateView):
    def get(self, request):
        return HttpResponse('<h1>Register</h1><p>Coming soon</p>')


class ProfileView(TemplateView):
    def get(self, request):
        return HttpResponse('<h1>Profile</h1><p>Coming soon</p>')


class ProfileEditView(TemplateView):
    def get(self, request):
        return HttpResponse('<h1>Edit Profile</h1><p>Coming soon</p>')
