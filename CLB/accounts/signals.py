from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import Customer, Shop
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Customer)
def send_customer_welcome_email(sender, instance, created, **kwargs):
    """
    Send a welcome email to newly created customers.
    """
    if created and instance.email:
        try:
            context = {
                'user': instance,
                'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000',
                'user_type': 'customer'
            }
            
            # Render the email template
            try:
                html_message = render_to_string('accounts/email/welcome_email.html', context)
            except Exception as e:
                logger.error(f"Error rendering welcome email template: {str(e)}")
                # Fallback to a simple text message if template rendering fails
                html_message = f"""
                <html>
                <body>
                    <h1>Welcome to Commerce!</h1>
                    <p>Dear {instance.name},</p>
                    <p>Thank you for joining Commerce! We're excited to have you as part of our community.</p>
                    <p>As a customer, you can now:</p>
                    <ul>
                        <li>Browse products from various shops</li>
                        <li>Add items to your cart</li>
                        <li>Place orders</li>
                        <li>Track your orders</li>
                    </ul>
                    <p>If you have any questions, feel free to contact our support team.</p>
                    <p>Best regards,<br>The Commerce Team</p>
                </body>
                </html>
                """
            
            # Send the email
            send_mail(
                subject='Welcome to Commerce!',
                message='Welcome to Commerce!',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.email],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            logger.error(f"Error sending welcome email to customer: {str(e)}")
            # Don't raise the exception - we don't want to prevent user creation if email fails

@receiver(post_save, sender=Shop)
def send_shop_welcome_email(sender, instance, created, **kwargs):
    """
    Send a welcome email to newly created shops.
    """
    if created and instance.email:
        try:
            context = {
                'user': instance,
                'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000',
                'user_type': 'shop'
            }
            
            # Render the email template
            try:
                html_message = render_to_string('accounts/email/welcome_email.html', context)
            except Exception as e:
                logger.error(f"Error rendering welcome email template: {str(e)}")
                # Fallback to a simple text message if template rendering fails
                html_message = f"""
                <html>
                <body>
                    <h1>Welcome to Commerce!</h1>
                    <p>Dear {instance.name},</p>
                    <p>Thank you for joining Commerce! We're excited to have you as part of our community.</p>
                    <p>As a shop owner, you can now:</p>
                    <ul>
                        <li>Add and manage your products</li>
                        <li>Process customer orders</li>
                        <li>Track your sales</li>
                        <li>Manage your shop profile</li>
                    </ul>
                    <p>If you have any questions, feel free to contact our support team.</p>
                    <p>Best regards,<br>The Commerce Team</p>
                </body>
                </html>
                """
            
            # Send the email
            send_mail(
                subject='Welcome to Commerce!',
                message='Welcome to Commerce!',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.email],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            logger.error(f"Error sending welcome email to shop: {str(e)}")
            # Don't raise the exception - we don't want to prevent user creation if email fails 