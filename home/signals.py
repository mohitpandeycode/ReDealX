from django.db.models.signals import post_save
from django.db.models.signals import post_delete
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import Notification
from django.contrib.auth.models import User
from home.models import Product  # Import your Product model

# Signal for user login
@receiver(user_logged_in)
def user_logged_in_notification(sender, request, user, **kwargs):
    Notification.objects.create(user=user, message="You have successfully logged in.")

# Signal for product ad posted
@receiver(post_save, sender=Product)
def product_posted_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(user=instance.seller, message=f"Your '{instance.title}' Ad has been posted.")

# Signal for product ad deleted

@receiver(post_delete, sender=Product)
def product_deleted_notification(sender, instance, **kwargs):
    Notification.objects.create(
        user=instance.seller,
        message=f"Your '{instance.title}' Ad has been deleted."
    )

