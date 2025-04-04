from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from .models import (
    Product, 
    ProductCategory,
    Cart,
    CartItem,
    Order,
    OrderItem,
    ShopProfile
)
from .forms import (
    CustomerRegistrationForm,
    ShopOwnerRegistrationForm,
    LoginForm,
    ProductForm,
    AddToCartForm,
    CheckoutForm
)

# Authentication Views
def homepage(request):
    """Homepage for all users with featured products"""
    featured_products = Product.objects.filter(is_featured=True, is_active=True)[:6]
    categories = ProductCategory.objects.all()[:5]
    
    if request.user.is_authenticated:
        return render(request, 'homepageloggedin.html', {
            'featured_products': featured_products,
            'categories': categories,
            'user': request.user
        })
    return render(request, 'homepage.html', {
        'featured_products': featured_products,
        'categories': categories
    })

def customersignup(request):
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            # Create a cart for the new user
            Cart.objects.create(user=user)
            messages.success(request, "Account created successfully!")
            return redirect('homepage')
    else:
        form = CustomerRegistrationForm()
    return render(request, 'customer_signup.html', {'form': form})

def shopsignup(request):
    if request.method == 'POST':
        form = ShopOwnerRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, "Shop account created successfully!")
            return redirect('shop_dashboard')
    else:
        form = ShopOwnerRegistrationForm()
    return render(request, 'shop_signup.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                auth_login(request, user)
                messages.success(request, f"Welcome back, {user.name}!")
                
                # Redirect based on user role
                if user.role == 'shop_owner':
                    return redirect('shop_dashboard')
                return redirect('homepage')
        messages.error(request, "Invalid email or password")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

@login_required
def logout(request):
    auth_logout(request)
    messages.success(request, "You have been logged out successfully")
    return redirect('homepage')

# Shop Owner Views
@login_required
def shop_dashboard(request):
    if request.user.role != 'shop_owner':
        return redirect('homepage')
    
    shop = get_object_or_404(ShopProfile, owner=request.user)
    products = Product.objects.filter(shop=shop)
    orders = Order.objects.filter(shop=shop).order_by('-created_at')[:5]
    
    return render(request, 'shop/dashboard.html', {
        'shop': shop,
        'products': products,
        'orders': orders
    })

@login_required
def add_product(request):
    if request.user.role != 'shop_owner':
        return redirect('homepage')
    
    shop = get_object_or_404(ShopProfile, owner=request.user)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.shop = shop
            product.save()
            messages.success(request, "Product added successfully!")
            return redirect('shop_dashboard')
    else:
        form = ProductForm()
    
    return render(request, 'shop/add_product.html', {'form': form})

# Product Views
def product_list(request):
    products = Product.objects.filter(is_active=True)
    categories = ProductCategory.objects.all()
    
    return render(request, 'products/list.html', {
        'products': products,
        'categories': categories
    })

def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(pk=product_id)[:4]
    
    form = AddToCartForm()
    
    return render(request, 'products/detail.html', {
        'product': product,
        'related_products': related_products,
        'form': form
    })

# Cart Views
@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        if item_id:
            try:
                item = CartItem.objects.get(pk=item_id, cart=cart)
                item.delete()
                messages.success(request, "Item removed from cart")
            except CartItem.DoesNotExist:
                messages.error(request, "Item not found in cart")
        return redirect('view_cart')
    
    return render(request, 'cart/view.html', {'cart': cart})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = AddToCartForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            
            # Check if product is already in cart
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
                
            messages.success(request, f"{product.name} added to cart")
            return redirect('product_detail', product_id=product.id)
    
    return redirect('product_detail', product_id=product.id)

# Checkout Views
@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    
    if cart.items.count() == 0:
        messages.warning(request, "Your cart is empty")
        return redirect('product_list')
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Create order
            order = Order(
                customer=request.user,
                shop=cart.items.first().product.shop,  # Assuming all items from same shop
                shipping_address=form.cleaned_data['shipping_address'],
                billing_address=form.cleaned_data['billing_address'] or form.cleaned_data['shipping_address'],
                phone=form.cleaned_data['phone'],
                payment_method=form.cleaned_data['payment_method'],
                notes=form.cleaned_data['notes'],
                total_amount=cart.subtotal
            )
            order.save()
            
            # Create order items
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.current_price
                )
                # Update product stock
                item.product.stock -= item.quantity
                item.product.save()
            
            # Clear the cart
            cart.items.all().delete()
            
            messages.success(request, "Order placed successfully!")
            return redirect('order_detail', order_id=order.id)
    else:
        initial_data = {
            'shipping_address': request.user.address,
            'phone': request.user.phone
        }
        form = CheckoutForm(initial=initial_data)
    
    return render(request, 'checkout/checkout.html', {
        'cart': cart,
        'form': form
    })

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, pk=order_id, customer=request.user)
    return render(request, 'orders/detail.html', {'order': order})

@login_required
def order_history(request):
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    return render(request, 'orders/history.html', {'orders': orders})