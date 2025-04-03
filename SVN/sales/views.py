from django.shortcuts import render, redirect
from sales.models import *
from .forms import *
from django.contrib import messages

def homepage(request):
    return render(request, 'homepage.html')

def login(request):
    return render(request, 'login.html')

def customersignup(request):
    pass
    # if request.method == 'POST':
    #     form = CustomerRegistrationForm(request.POST)
    #     if form.is_valid():
    #         user = form.save()
    #         user.is_active = True  # Ensure the user is active upon registration
    #         user.save()

    #         messages.success(request, 'Registration successful. You can now log in.')
    #         return redirect('login')  # Redirect to login page
    #     else:
    #         messages.error(request, 'There was an error in the form. Please try again.')
    # else:
    #     form = CustomerRegistrationForm()

    return render(request, 'customer_signup.html')

def shopsignup(request):
    pass
    # if request.method == 'POST':
    #     form = ShopRegistrationForm(request.POST)
    #     if form.is_valid():
    #         user = form.save(commit=False)
    #         user.set_password(form.cleaned_data['password1'])  # Hash the password
    #         user.save()

    #         # Option 1: Add a custom field (is_shop) to indicate this is a shop owner
    #         user.profile.is_shop = True  # Assuming using Profile model for roles
    #         user.profile.save()

    #         messages.success(request, 'Shop registration successful. You can now log in.')
    #         return redirect('login')  # Redirect to login page
    #     else:
    #         messages.error(request, 'There was an error in the form. Please try again.')
    # else:
    #     form = ShopRegistrationForm()

    return render(request, 'shop_signup.html')

def logout(request):
    pass