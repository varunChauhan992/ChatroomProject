from .models import Room
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username']




class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['name']

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if Room.objects.filter(name__iexact=name).exists():
            raise forms.ValidationError("A chatroom with this name already exists.")
        return name