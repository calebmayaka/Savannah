

















































































































# # forms.py
# from django import forms
# from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.models import User


# from django.contrib.auth.forms import authenticate
# from .models import *
# from django.contrib.auth.forms import UserCreationForm, UserChangeForm
# from django.forms import ModelForm


# class CustomerRegistrationForm(UserCreationForm):
#     # 
#     email = forms.EmailField(required=True)
#     phone = forms.CharField(max_length=15, required=True)

#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password1', 'password2', 'phone']


# class ShopRegistrationForm(UserCreationForm):
#     email = forms.EmailField(required=True)
#     phone = forms.CharField(max_length=15, required=True)
#     shop_name = forms.CharField(max_length=100, required=True)
#     confirm_password = forms.CharField(widget=forms.PasswordInput(), required=True)

#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password1', 'password2', 'phone', 'shop_name']

#     def clean(self):
#         cleaned_data = super().clean()
#         password = cleaned_data.get('password1')
#         confirm_password = cleaned_data.get('confirm_password')

#         # Check if passwords match
#         if password != confirm_password:
#             raise forms.ValidationError("Passwords do not match")

#         return cleaned_data
    
