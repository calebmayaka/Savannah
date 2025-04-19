from django.urls import path
from . import views

urlpatterns = [
    path('customer/signup/', views.customer_signup, name='customer_signup'),
    path('customer/login/', views.customer_login, name='customer_login'),
    path('customer/profile/', views.customer_profile, name='profile'),
    path('customer/profile/update/', views.update_customer_profile, name='update_profile'),
    
    path('shop/signup/', views.shop_signup, name='shop_signup'),
    path('shop/login/', views.shop_login, name='shop_login'),
    path('shop/profile/', views.shop_profile, name='shop_profile'),
    path('shop/profile/update/', views.update_shop_profile, name='update_shop_profile'),
    
    # Product management
    path('shop/product/add/', views.add_product, name='add_product'),
    path('shop/product/<int:product_id>/', views.update_product, name='get_product'),
    path('shop/product/<int:product_id>/update/', views.update_product, name='update_product'),
    path('shop/product/<int:product_id>/delete/', views.delete_product, name='delete_product'),
    
    # Cart management
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    
    path('logout/', views.logout_view, name='logout'),
] 