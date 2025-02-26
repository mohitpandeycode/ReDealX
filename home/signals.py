from django.db.models.signals import post_save, post_delete
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import Notification
from django.contrib.auth.models import User
from home.models import Product
from django.contrib.auth import get_user_model

User = get_user_model()  # Get the custom user model

# Signal for user login
@receiver(user_logged_in)
def user_logged_in_notification(sender, request, user, **kwargs):
    Notification.objects.create(user=user, message="You have successfully logged in.")

@receiver(post_save, sender=User)
def user_created_notification(sender, instance, created, **kwargs):
    if created:
        name = instance.first_name if instance.first_name else instance.username 
        Notification.objects.create(
            user=instance,
            message=f"Welcome to ReDealX <span style='color: blue; font-weight: bold;'>{name}</span>."
        )
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


