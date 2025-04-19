from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from .models import Customer, Shop, Product, Cart, CartItem
from django.db import transaction
from django.http import JsonResponse
from .backends import ShopAuthenticationBackend, CustomerAuthenticationBackend
import logging

# Set up logging
logger = logging.getLogger(__name__)

def customer_signup(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                name = request.POST.get('name')
                email = request.POST.get('email')
                password = request.POST.get('password')
                confirm_password = request.POST.get('confirm_password')
                
                # Validate required fields
                if not all([name, email, password, confirm_password]):
                    raise ValidationError('All fields are required')
                
                if password != confirm_password:
                    raise ValidationError('Passwords do not match')
                
                try:
                    validate_password(password)
                except ValidationError as e:
                    raise ValidationError(str(e))
                
                if Customer.objects.filter(email=email).exists():
                    raise ValidationError('Email already exists')
                
                try:
                    user = Customer.objects.create_user(
                        username=email,
                        email=email,
                        password=password,
                        name=name
                    )
                except Exception as e:
                    logger.error(f"Error creating customer user: {str(e)}")
                    raise ValidationError('Error creating user account')
                
                try:
                    # Explicitly specify the authentication backend
                    login(request, user, backend='accounts.backends.CustomerAuthenticationBackend')
                except Exception as e:
                    logger.error(f"Error logging in customer: {str(e)}")
                    raise ValidationError('Error logging in after registration')
                
                messages.success(request, 'Account created successfully')
                return redirect('profile')
                
        except ValidationError as e:
            messages.error(request, str(e))
        except Exception as e:
            logger.error(f"Unexpected error during customer registration: {str(e)}")
            messages.error(request, f'An error occurred during registration: {str(e)}')
            
    return render(request, 'accounts/customer_signup.html')

def shop_signup(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                name = request.POST.get('name')
                owner_name = request.POST.get('owner_name')
                email = request.POST.get('email')
                password = request.POST.get('password')
                confirm_password = request.POST.get('confirm_password')
                location = request.POST.get('location')
                
                # Validate required fields
                if not all([name, owner_name, email, password, confirm_password, location]):
                    raise ValidationError('All fields are required')
                
                if password != confirm_password:
                    raise ValidationError('Passwords do not match')
                
                # Use our custom password validation
                from .models import validate_password_strength
                try:
                    validate_password_strength(password)
                except ValidationError as e:
                    raise ValidationError(str(e))
                
                if Shop.objects.filter(email=email).exists():
                    raise ValidationError('Email already exists')
                
                try:
                    # Create the shop user
                    shop = Shop.objects.create_user(
                        username=email,
                        email=email,
                        password=password,
                        name=name,
                        owner_name=owner_name,
                        location=location
                    )
                except Exception as e:
                    logger.error(f"Error creating shop user: {str(e)}")
                    raise ValidationError('Error creating shop account')
                
                # Verify the password was set correctly
                if not shop.check_password(password):
                    raise ValidationError('Error setting password')
                
                messages.success(request, 'Shop registered successfully')
                return redirect('shop_login')
                
        except ValidationError as e:
            messages.error(request, str(e))
        except Exception as e:
            logger.error(f"Unexpected error during shop registration: {str(e)}")
            messages.error(request, f'An error occurred during registration: {str(e)}')
            
    return render(request, 'accounts/shop_signup.html')

def customer_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')
        
        try:
            # Use our custom authentication backend
            backend = CustomerAuthenticationBackend()
            user = backend.authenticate(request, username=email, password=password)
            
            if user is not None and isinstance(user, Customer):
                # Explicitly specify the backend when logging in
                login(request, user, backend='accounts.backends.CustomerAuthenticationBackend')
                if not remember_me:
                    request.session.set_expiry(0)  # Session expires when browser closes
                messages.success(request, 'Logged in successfully')
                return redirect('profile')
            else:
                messages.error(request, 'Invalid email or password')
        except Exception as e:
            messages.error(request, f'An error occurred during login: {str(e)}')
    
    return render(request, 'accounts/customer_login.html')

def shop_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')
        
        try:
            # Use standard Django authentication
            user = authenticate(request, username=email, password=password)
            
            if user is not None and isinstance(user, Shop):
                login(request, user)
                if not remember_me:
                    request.session.set_expiry(0)  # Session expires when browser closes
                messages.success(request, 'Logged in successfully')
                return redirect('shop_profile')
            else:
                messages.error(request, 'Invalid email or password')
        except Exception as e:
            messages.error(request, f'An error occurred during login: {str(e)}')
    
    return render(request, 'accounts/shop_login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully')
    return redirect('customer_login')

@login_required
def customer_profile(request):
    # Check if the user is a Customer
    if not isinstance(request.user, Customer):
        messages.error(request, 'Access denied. This page is for customers only.')
        return redirect('shop_profile')
    
    products = Product.objects.filter(is_active=True).select_related('shop')
    cart_items_count = 0
    
    # Get or create a cart for the user
    cart, created = Cart.objects.get_or_create(customer=request.user)
    cart_items_count = cart.items.count()
    
    return render(request, 'accounts/customer_profile.html', {
        'products': products,
        'cart_items_count': cart_items_count
    })

@login_required
def shop_profile(request):
    if not isinstance(request.user, Shop):
        messages.error(request, 'Access denied')
        return redirect('shop_login')
    products = request.user.products.all()
    return render(request, 'accounts/shop_profile.html', {'shop': request.user, 'products': products})

@login_required
def update_customer_profile(request):
    # Check if the user is a Customer
    if not isinstance(request.user, Customer):
        messages.error(request, 'Access denied. This page is for customers only.')
        return redirect('shop_profile')
    
    if request.method == 'POST':
        try:
            user = request.user
            user.name = request.POST.get('name', user.name)
            user.phone = request.POST.get('phone', user.phone)
            user.address = request.POST.get('address', user.address)
            user.full_clean()
            user.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('profile')
        except ValidationError as e:
            messages.error(request, str(e))
    
    return render(request, 'accounts/update_customer_profile.html')

@login_required
def update_shop_profile(request):
    if not isinstance(request.user, Shop):
        messages.error(request, 'Access denied')
        return redirect('shop_login')
    
    if request.method == 'POST':
        try:
            shop = request.user
            shop.name = request.POST.get('name', shop.name)
            shop.owner_name = request.POST.get('owner_name', shop.owner_name)
            shop.location = request.POST.get('location', shop.location)
            shop.phone = request.POST.get('phone', shop.phone)
            shop.description = request.POST.get('description', shop.description)
            shop.full_clean()
            shop.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('shop_profile')
        except ValidationError as e:
            messages.error(request, str(e))
    
    return render(request, 'accounts/update_shop_profile.html', {'shop': request.user})

@login_required
def add_product(request):
    if not isinstance(request.user, Shop):
        messages.error(request, 'Access denied')
        return redirect('shop_login')
    
    if request.method == 'POST':
        try:
            product = Product(
                shop=request.user,
                title=request.POST['title'],
                description=request.POST['description'],
                price=request.POST['price'],
                stock=request.POST['stock']
            )
            if 'image' in request.FILES:
                product.image = request.FILES['image']
            product.full_clean()
            product.save()
            messages.success(request, 'Product added successfully')
            return redirect('shop_profile')
        except ValidationError as e:
            messages.error(request, str(e))
    
    return redirect('shop_profile')

@login_required
def update_product(request, product_id):
    if not isinstance(request.user, Shop):
        messages.error(request, 'Access denied')
        return redirect('shop_login')
    
    try:
        product = request.user.products.get(id=product_id)
        if request.method == 'POST':
            product.title = request.POST['title']
            product.description = request.POST['description']
            product.price = request.POST['price']
            product.stock = request.POST['stock']
            if 'image' in request.FILES:
                product.image = request.FILES['image']
            product.full_clean()
            product.save()
            messages.success(request, 'Product updated successfully')
            return redirect('shop_profile')
        return JsonResponse({
            'title': product.title,
            'description': product.description,
            'price': str(product.price),
            'stock': product.stock
        })
    except Product.DoesNotExist:
        messages.error(request, 'Product not found')
        return redirect('shop_profile')

@login_required
def delete_product(request, product_id):
    if not isinstance(request.user, Shop):
        messages.error(request, 'Access denied')
        return redirect('shop_login')
    
    try:
        product = request.user.products.get(id=product_id)
        product.delete()
        messages.success(request, 'Product deleted successfully')
    except Product.DoesNotExist:
        messages.error(request, 'Product not found')
    
    return redirect('shop_profile')

@login_required
def add_to_cart(request, product_id):
    if not isinstance(request.user, Customer):
        messages.error(request, 'Access denied')
        return redirect('customer_login')
    
    try:
        product = Product.objects.get(id=product_id, is_active=True)
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity > product.stock:
            messages.error(request, 'Not enough stock available')
            return redirect('profile')
        
        cart, created = Cart.objects.get_or_create(customer=request.user)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            if cart_item.quantity > product.stock:
                messages.error(request, 'Not enough stock available')
                return redirect('profile')
            cart_item.save()
        
        messages.success(request, 'Product added to cart')
    except Product.DoesNotExist:
        messages.error(request, 'Product not found')
    except ValueError:
        messages.error(request, 'Invalid quantity')
    
    return redirect('profile')

@login_required
def cart(request):
    if not isinstance(request.user, Customer):
        messages.error(request, 'Access denied')
        return redirect('customer_login')
    
    cart, created = Cart.objects.get_or_create(customer=request.user)
    return render(request, 'accounts/cart.html', {'cart': cart})

@login_required
def update_cart_item(request, item_id):
    if not isinstance(request.user, Customer):
        messages.error(request, 'Access denied')
        return redirect('customer_login')
    
    try:
        # Get the cart first, then access its items
        cart = Cart.objects.get(customer=request.user)
        cart_item = cart.items.get(id=item_id)
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity > cart_item.product.stock:
            messages.error(request, 'Not enough stock available')
            return redirect('cart')
        
        if quantity <= 0:
            cart_item.delete()
        else:
            cart_item.quantity = quantity
            cart_item.save()
        
        messages.success(request, 'Cart updated successfully')
    except Cart.DoesNotExist:
        messages.error(request, 'Cart not found')
    except CartItem.DoesNotExist:
        messages.error(request, 'Item not found in cart')
    except ValueError:
        messages.error(request, 'Invalid quantity')
    
    return redirect('cart')

@login_required
def remove_from_cart(request, item_id):
    if not isinstance(request.user, Customer):
        messages.error(request, 'Access denied')
        return redirect('customer_login')
    
    try:
        # Get the cart first, then access its items
        cart = Cart.objects.get(customer=request.user)
        cart_item = cart.items.get(id=item_id)
        cart_item.delete()
        messages.success(request, 'Item removed from cart')
    except Cart.DoesNotExist:
        messages.error(request, 'Cart not found')
    except CartItem.DoesNotExist:
        messages.error(request, 'Item not found in cart')
    
    return redirect('cart')
