from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import (
    customUserModel, 
    ShopProfile, 
    Product, 
    ProductCategory,
    CartItem,
    Order
)
from django.core.validators import MinValueValidator

# Base Form (Password Validation)
class BaseRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Create password',
            'class': 'form-control'
        })
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Repeat password',
            'class': 'form-control'
        })
    )

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match!")
        return password2

    class Meta:
        model = customUserModel
        fields = []

# Customer Registration
class CustomerRegistrationForm(BaseRegistrationForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Your email',
            'class': 'form-control'
        })
    )
    name = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Your full name',
            'class': 'form-control'
        })
    )
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Phone number (optional)',
            'class': 'form-control'
        })
    )

    class Meta(BaseRegistrationForm.Meta):
        fields = ['email', 'name', 'phone']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'customer'
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user

# Shop Owner Registration
class ShopOwnerRegistrationForm(BaseRegistrationForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Shop contact email',
            'class': 'form-control'
        })
    )
    shop_name = forms.CharField(
        label="Shop Name",
        widget=forms.TextInput(attrs={
            'placeholder': 'Your shop name',
            'class': 'form-control'
        })
    )
    shop_location = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Shop location',
            'class': 'form-control'
        })
    )
    contact_number = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Contact number',
            'class': 'form-control'
        })
    )

    class Meta(BaseRegistrationForm.Meta):
        fields = ['email']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'shop_owner'
        user.name = self.cleaned_data['shop_name']
        user.set_password(self.cleaned_data['password1'])
        
        if commit:
            user.save()
            ShopProfile.objects.create(
                owner=user,
                name=self.cleaned_data['shop_name'],
                location=self.cleaned_data['shop_location'],
                contact_number=self.cleaned_data['contact_number']
            )
        return user

# Login Form
class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'placeholder': 'Your email',
            'class': 'form-control',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password',
            'class': 'form-control'
        })
    )

# Product Form
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'category', 'price', 'discount_price', 
            'stock', 'description', 'image', 'is_featured', 'is_active'
        ]
        widgets = {
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'discount_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
        }

# Category Form
class ProductCategoryForm(forms.ModelForm):
    class Meta:
        model = ProductCategory
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }

# Add to Cart Form
class AddToCartForm(forms.ModelForm):
    quantity = forms.IntegerField(
        initial=1,
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'style': 'width: 80px;'
        })
    )

    class Meta:
        model = CartItem
        fields = ['quantity']

# Checkout Form
class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'shipping_address', 
            'billing_address', 
            'phone', 
            'payment_method',
            'notes'
        ]
        widgets = {
            'shipping_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Your complete shipping address'
            }),
            'billing_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Leave blank if same as shipping address'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone number for delivery updates'
            }),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Any special instructions?'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['payment_method'].choices = [
            ('cash_on_delivery', 'Cash on Delivery'),
            ('credit_card', 'Credit Card'),
            ('paypal', 'PayPal'),
        ]