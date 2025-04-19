from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator, MinLengthValidator
from django.core.exceptions import ValidationError
import re

def validate_password_strength(password):
    """
    Validate that the password meets the following criteria:
    - At least 8 characters long
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one number
    - Contains at least one special character
    """
    if len(password) < 8:
        raise ValidationError('Password must be at least 8 characters long.')
    if not re.search(r'[A-Z]', password):
        raise ValidationError('Password must contain at least one uppercase letter.')
    if not re.search(r'[a-z]', password):
        raise ValidationError('Password must contain at least one lowercase letter.')
    if not re.search(r'\d', password):
        raise ValidationError('Password must contain at least one number.')
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError('Password must contain at least one special character.')

class Customer(AbstractUser):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(
        max_length=15, 
        blank=True, 
        null=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ]
    )
    address = models.TextField(blank=True, null=True)
    
    # Add related_name to resolve the clash
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customer_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customer_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'name']

    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'

    def __str__(self):
        return self.email

class Shop(AbstractUser):
    # Override the username field to make it nullable
    username = models.CharField(
        max_length=150, 
        unique=True, 
        null=True, 
        blank=True,
        help_text='Optional. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'
    )
    
    name = models.CharField(max_length=100)
    owner_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    location = models.CharField(max_length=200)
    phone = models.CharField(
        max_length=15, 
        blank=True, 
        null=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ]
    )
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Add related_name to resolve the clash
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='shop_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='shop_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'name', 'owner_name', 'location']

    class Meta:
        verbose_name = 'Shop'
        verbose_name_plural = 'Shops'

    def clean(self):
        super().clean()
        if self.password:
            validate_password_strength(self.password)
        
        # Generate username from email if not provided
        if not self.username and self.email:
            self.username = self.email

    def save(self, *args, **kwargs):
        # Generate username from email if not provided
        if not self.username and self.email:
            self.username = self.email
            
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Product(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='products')
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.customer.name}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"{self.quantity} x {self.product.title}"
