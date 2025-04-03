from django.shortcuts import render

def homepage(request):
    return render(request, 'homepage.html')

def login(request):
    return render(request, 'login.html')

def customersignup(request):
    return render(request, 'customer_signup.html')

def shopsignup(request):
    return render(request, 'shop_signup.html')

def logout(request):
    pass