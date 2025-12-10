from django import forms
from .models import ContactMessage

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg bg-background/50 border border-secondary/20 focus:border-accent focus:outline-none transition-colors',
                'placeholder': 'Your Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg bg-background/50 border border-secondary/20 focus:border-accent focus:outline-none transition-colors',
                'placeholder': 'your.email@example.com'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg bg-background/50 border border-secondary/20 focus:border-accent focus:outline-none transition-colors',
                'placeholder': 'Project Inquiry'
            }),
            'message': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-lg bg-background/50 border border-secondary/20 focus:border-accent focus:outline-none transition-colors',
                'rows': 6,
                'placeholder': 'Tell me about your project...'
            }),
        }