from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from ckeditor.fields import RichTextField
from django.core.validators import MinValueValidator

# Custom User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, name, email, password=None):
        if not email:
            raise ValueError("Email is required")
        if not name:
            raise ValueError("Name is required")

        user = self.model(email=self.normalize_email(email), name=name)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, name, email, password):
        user = self.create_user(name=name, email=email, password=password)
        user.is_admin = True
        user.is_staff = True
        user.save(using=self._db)
        return user

# Custom User Model
class customUserModel(AbstractBaseUser):
    USER_ROLES = (
        ('customer', 'Customer'),
        ('shop_owner', 'Shop Owner'),
    )

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=USER_ROLES, default='customer')
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email

# Shop Profile
class ShopProfile(models.Model):
    shop_no = models.CharField(max_length=255, unique=True, primary_key=True)
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    owner = models.ForeignKey(customUserModel, on_delete=models.CASCADE)  # Shop owner
    created_at = models.DateTimeField(auto_now_add=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

# Product
class Product(models.Model):
    name = models.CharField(max_length=255)
    shop = models.ForeignKey(ShopProfile, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    stock = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    description = RichTextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# Order
class Order(models.Model):
    customer = models.ForeignKey(customUserModel, on_delete=models.CASCADE)  # Link to User
    shop = models.ForeignKey(ShopProfile, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    status = models.CharField(
        max_length=50,
        choices=[('Pending', 'Pending'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')],
        default='Pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} - {self.customer.name} - {self.shop.name}"

# OrderItem
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    original_price = models.DecimalField(max_digits=10, decimal_places=2)  # Store original price

    def __str__(self):
        return f"{self.product.name} - {self.quantity} pcs"
