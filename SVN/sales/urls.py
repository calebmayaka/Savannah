from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Core URLs
    path('', views.homepage, name='homepage'),
    
    # Authentication URLs
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('signup/customer/', views.customersignup, name='customer_signup'),
    path('signup/shop/', views.shopsignup, name='shop_signup'),
    
    # Shop Owner URLs
    path('shop/dashboard/', views.shop_dashboard, name='shop_dashboard'),
    path('shop/products/add/', views.add_product, name='add_product'),
    
    # Product URLs
    path('products/', views.product_list, name='product_list'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    
    # Cart URLs
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    
    # Order URLs
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.order_history, name='order_history'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)