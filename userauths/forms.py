from django import forms
from django.contrib.auth.forms import UserCreationForm
from userauths.models import Account


class UserRegistrationForm(UserCreationForm):
    username= forms.CharField(widget=forms.TextInput(attrs={"placeholder":"username"}))
    email= forms.EmailField(widget=forms.EmailInput(attrs={"placeholder":"Email"}))

    password1= forms.CharField(widget=forms.PasswordInput(attrs={"placeholder":"Password"}))
    password2= forms.CharField(widget=forms.PasswordInput(attrs={"placeholder":"confirm Password"}))





    class Meta:
        model=Account
        fields=['username','email']
