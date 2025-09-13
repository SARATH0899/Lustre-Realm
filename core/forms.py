from django import forms
from .models import Contact


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ('name', 'email', 'phone', 'subject', 'message')
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        # Add placeholder text
        self.fields['name'].widget.attrs['placeholder'] = 'Your full name'
        self.fields['email'].widget.attrs['placeholder'] = 'your.email@example.com'
        self.fields['phone'].widget.attrs['placeholder'] = 'Your phone number (optional)'
        self.fields['subject'].widget.attrs['placeholder'] = 'What is this regarding?'
        self.fields['message'].widget.attrs['placeholder'] = 'Tell us more about your inquiry...'