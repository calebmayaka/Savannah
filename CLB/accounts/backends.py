from django.contrib.auth.backends import ModelBackend
from .models import Shop, Customer

class ShopAuthenticationBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Try to find the shop by email
            shop = Shop.objects.get(email=username)
            # Check the password
            if shop.check_password(password):
                return shop
        except Shop.DoesNotExist:
            return None
        return None

    def get_user(self, user_id):
        try:
            # Try to get the user as a Shop
            return Shop.objects.get(pk=user_id)
        except Shop.DoesNotExist:
            try:
                # If not a Shop, try to get it as a Customer
                return Customer.objects.get(pk=user_id)
            except Customer.DoesNotExist:
                return None

class CustomerAuthenticationBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Try to find the customer by email
            customer = Customer.objects.get(email=username)
            # Check the password
            if customer.check_password(password):
                return customer
        except Customer.DoesNotExist:
            return None
        return None

    def get_user(self, user_id):
        try:
            # Try to get the user as a Customer
            return Customer.objects.get(pk=user_id)
        except Customer.DoesNotExist:
            try:
                # If not a Customer, try to get it as a Shop
                return Shop.objects.get(pk=user_id)
            except Shop.DoesNotExist:
                return None 