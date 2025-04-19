from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import Customer, Shop, Product, Cart, CartItem
from django.apps import apps
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.urls import path
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse

# Override the default app label for auth models
apps.get_app_config('auth').verbose_name = 'Authentication'

User = get_user_model()

# Custom admin for Customer model
class CustomerAdmin(UserAdmin):
    list_display = ('email', 'name', 'phone', 'address', 'is_active', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'date_joined')
    search_fields = ('email', 'name', 'phone')
    ordering = ('-date_joined',)
    
    # Customize the fieldsets
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name', 'phone', 'address')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2'),
        }),
    )
    
    # Add custom actions
    actions = ['send_welcome_email']
    
    def send_welcome_email(self, request, queryset):
        """Send welcome email to selected customers"""
        success_count = 0
        for customer in queryset:
            if customer.email:
                try:
                    context = {
                        'user': customer,
                        'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000'
                    }
                    
                    # Render the email template
                    html_message = render_to_string('accounts/email/welcome_email.html', context)
                    
                    # Send the email
                    send_mail(
                        subject='Welcome to Commerce!',
                        message='Welcome to Commerce!',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[customer.email],
                        html_message=html_message,
                        fail_silently=False,
                    )
                    success_count += 1
                except Exception as e:
                    self.message_user(request, f"Failed to send email to {customer.email}: {str(e)}", level=messages.ERROR)
        
        if success_count > 0:
            self.message_user(request, f"Successfully sent welcome email to {success_count} customer(s).")
    send_welcome_email.short_description = "Send welcome email to selected customers"

# Custom admin for Shop model (which is our default user model)
class ShopAdmin(UserAdmin):
    list_display = ('email', 'name', 'owner_name', 'location', 'is_active', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'date_joined')
    search_fields = ('email', 'name', 'owner_name', 'location')
    ordering = ('-date_joined',)
    
    # Customize the fieldsets
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Shop info', {'fields': ('name', 'owner_name', 'location', 'phone', 'description')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'owner_name', 'location', 'password1', 'password2'),
        }),
    )
    
    # Add custom actions
    actions = ['send_welcome_email']
    
    def send_welcome_email(self, request, queryset):
        """Send welcome email to selected shops"""
        success_count = 0
        for shop in queryset:
            if shop.email:
                try:
                    context = {
                        'user': shop,
                        'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000'
                    }
                    
                    # Render the email template
                    html_message = render_to_string('accounts/email/welcome_email.html', context)
                    
                    # Send the email
                    send_mail(
                        subject='Welcome to Commerce!',
                        message='Welcome to Commerce!',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[shop.email],
                        html_message=html_message,
                        fail_silently=False,
                    )
                    success_count += 1
                except Exception as e:
                    self.message_user(request, f"Failed to send email to {shop.email}: {str(e)}", level=messages.ERROR)
        
        if success_count > 0:
            self.message_user(request, f"Successfully sent welcome email to {success_count} shop(s).")
    send_welcome_email.short_description = "Send welcome email to selected shops"

# Custom admin for Product model
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'shop', 'price', 'stock', 'is_active', 'created_at', 'image_preview')
    list_filter = ('is_active', 'shop', 'created_at')
    search_fields = ('title', 'description', 'shop__name')
    ordering = ('-created_at',)
    list_editable = ('price', 'stock', 'is_active')
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return "No image"
    image_preview.short_description = 'Image'

# Custom admin for Cart model
class CartAdmin(admin.ModelAdmin):
    list_display = ('customer', 'item_count', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('customer__email', 'customer__name')
    ordering = ('-updated_at',)
    
    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Items'

# Custom admin for CartItem model
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'added_at', 'total_price')
    list_filter = ('added_at', 'product__shop')
    search_fields = ('cart__customer__email', 'product__title')
    ordering = ('-added_at',)
    
    def total_price(self, obj):
        return f"${obj.product.price * obj.quantity:.2f}"
    total_price.short_description = 'Total Price'

# Custom admin site class
class CommerceAdminSite(admin.AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('send-welcome-emails/', self.admin_view(self.send_welcome_emails_view), name='send-welcome-emails'),
        ]
        return custom_urls + urls
    
    def send_welcome_emails_view(self, request):
        if request.method == 'POST':
            user_type = request.POST.get('user_type', 'all')
            success_count = 0
            error_count = 0
            
            if user_type == 'all':
                users = User.objects.all()
            elif user_type == 'customers':
                users = Customer.objects.all()
            elif user_type == 'shops':
                users = Shop.objects.all()
            else:
                users = User.objects.none()
            
            for user in users:
                if user.email:
                    try:
                        context = {
                            'user': user,
                            'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000'
                        }
                        
                        # Render the email template
                        html_message = render_to_string('accounts/email/welcome_email.html', context)
                        
                        # Send the email
                        send_mail(
                            subject='Welcome to Commerce!',
                            message='Welcome to Commerce!',
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[user.email],
                            html_message=html_message,
                            fail_silently=False,
                        )
                        success_count += 1
                    except Exception as e:
                        error_count += 1
            
            messages.success(request, f"Successfully sent welcome email to {success_count} user(s).")
            if error_count > 0:
                messages.error(request, f"Failed to send welcome email to {error_count} user(s).")
            
            return HttpResponseRedirect(reverse('admin:index'))
        
        return render(request, 'admin/send_welcome_emails.html', {
            'title': 'Send Welcome Emails',
            'user_types': [
                {'value': 'all', 'label': 'All Users'},
                {'value': 'customers', 'label': 'Customers Only'},
                {'value': 'shops', 'label': 'Shops Only'},
            ]
        })

# Create a custom admin site instance
commerce_admin_site = CommerceAdminSite(name='commerce_admin')

# Register models with the custom admin site
commerce_admin_site.register(Customer, CustomerAdmin)
commerce_admin_site.register(Product, ProductAdmin)
commerce_admin_site.register(Cart, CartAdmin)
commerce_admin_site.register(CartItem, CartItemAdmin)

# Register Shop model with the default admin site
admin.site.register(Shop, ShopAdmin)

# Customize the admin site
commerce_admin_site.site_header = 'Commerce Admin'
commerce_admin_site.site_title = 'Commerce Admin Portal'
commerce_admin_site.index_title = 'Welcome to Commerce Admin Portal'
