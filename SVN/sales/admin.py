from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import customUserModel, ShopProfile, Product, Order, OrderItem
from django.utils.html import format_html

# Custom User Admin
@admin.register(customUserModel)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'name', 'role', 'phone', 'is_active', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('email', 'name', 'phone')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name', 'role', 'phone', 'address')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_admin', 'groups', 'user_permissions'),
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'role', 'password1', 'password2', 'is_active', 'is_staff', 'is_admin'),
        }),
    )

# Shop Profile Admin
@admin.register(ShopProfile)
class ShopProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner_email', 'location', 'is_active', 'created_at')
    list_select_related = ('owner',)
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'owner__email', 'location')
    raw_id_fields = ('owner',)
    readonly_fields = ('shop_no', 'created_at')
    
    def owner_email(self, obj):
        return obj.owner.email
    owner_email.short_description = 'Owner Email'

# Product Admin
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'shop_link', 'price', 'stock', 'updated_at')
    list_filter = ('shop__name', 'is_active', 'is_featured')
    search_fields = ('name', 'shop__name', 'description')
    raw_id_fields = ('shop',)
    readonly_fields = ('created_at', 'updated_at')
    
    def shop_link(self, obj):
        return format_html('<a href="/admin/sales/shopprofile/{}/change/">{}</a>',
                          obj.shop.shop_no, obj.shop.name)
    shop_link.short_description = 'Shop'
    shop_link.admin_order_field = 'shop__name'

# Order Item Inline
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    raw_id_fields = ('product',)
    readonly_fields = ('price', 'created_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product')

# Order Admin
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer_email', 'shop_name', 'created_at', 'status', 'total_amount')
    list_filter = ('status', 'created_at', 'shop__name')
    search_fields = ('customer__email', 'shop__name', 'order_number')
    raw_id_fields = ('customer', 'shop')
    inlines = [OrderItemInline]
    readonly_fields = ('order_number', 'created_at', 'updated_at')
    
    def customer_email(self, obj):
        return obj.customer.email
    customer_email.short_description = 'Customer'
    customer_email.admin_order_field = 'customer__email'
    
    def shop_name(self, obj):
        return obj.shop.name
    shop_name.short_description = 'Shop'
    shop_name.admin_order_field = 'shop__name'

# OrderItem Admin (separate registration for direct access)
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order_link', 'product_name', 'quantity', 'price', 'total_price')
    list_select_related = ('order', 'product')
    raw_id_fields = ('order', 'product')
    readonly_fields = ('created_at',)
    
    def order_link(self, obj):
        return format_html('<a href="/admin/sales/order/{}/change/">Order #{}</a>',
                          obj.order.id, obj.order.order_number)
    order_link.short_description = 'Order'
    
    def product_name(self, obj):
        return obj.product.name
    product_name.short_description = 'Product'
    
    def total_price(self, obj):
        return obj.price * obj.quantity
    total_price.short_description = 'Total Price'