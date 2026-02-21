from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Agent,Apartment,ApartmentImage

class AgentRegisterForm(UserCreationForm):
    phone_number = forms.CharField(max_length=15)
    whatsapp_number = forms.CharField(max_length=15)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            Agent.objects.create(
                user=user,
                phone_number=self.cleaned_data['phone_number'],
                whatsapp_number=self.cleaned_data['whatsapp_number']
            )
        return user

class ApartmentForm(forms.ModelForm):
    class Meta:
        model = Apartment
        fields = [
            'title', 'university', 'description', 'price', 'period', 
            'distance', 'address', 'amenities', 
            'state', 'is_available',
        ]
        widgets = {
            'amenities': forms.CheckboxSelectMultiple,
            'apartment_type': forms.CheckboxSelectMultiple,
        }

class ApartmentImageForm(forms.ModelForm):
    class Meta:
        model = ApartmentImage
        fields = ['image']

class ProfileForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    username = forms.CharField(required=True)

    class Meta:
        model = Agent
        fields = ['phone_number', 'whatsapp_number', 'profile_pic'] 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['email'].initial = self.instance.user.email
            self.fields['username'].initial = self.instance.user.username

    def save(self, commit=True):
        agent = super().save(commit=False)
        user = agent.user
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['username']
        if commit:
            user.save()
            agent.save()
        return agent

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'w-full p-3 border rounded-lg',
        'placeholder': 'Your Name'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'w-full p-3 border rounded-lg',
        'placeholder': 'Your Email'
    }))
    subject = forms.CharField(max_length=150, widget=forms.TextInput(attrs={
        'class': 'w-full p-3 border rounded-lg',
        'placeholder': 'Subject'
    }))
    message = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'w-full p-3 border rounded-lg',
        'placeholder': 'Your Message',
        'rows': 5
    }))