from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from accounts.models import Customer, Shop

def landing_page(request):
    # If user is logged in, redirect to their profile page
    if request.user.is_authenticated:
        if isinstance(request.user, Customer):
            return redirect('profile')
        elif isinstance(request.user, Shop):
            return redirect('shop_profile')
    
    # Otherwise, show the landing page
    return render(request, 'main/landing.html') 

def landing(request):
    pass
