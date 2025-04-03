from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('login/', views.login, name = 'login'),
    path('customersignup/', views.customersignup, name = 'customer_signup'),
    path('shopsignup/', views.shopsignup, name = 'shop_signup'),
    path('logout/', views.logout, name='logout'),
]
