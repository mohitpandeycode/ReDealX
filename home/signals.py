from django.db.models.signals import post_save, post_delete
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import Notification
from django.contrib.auth.models import User
from home.models import Product
from Chat.models import Message
from django.contrib.auth import get_user_model
from django.db.models.signals import pre_save
from .models import ProductImages
from cloudinary.uploader import upload
from django.core.files.uploadedfile import InMemoryUploadedFile

def compress_and_upload(image):
    result = upload(image, transformation=[
        {"width": 800, "crop": "limit"},
        {"quality": "auto"},
        {"fetch_format": "auto"}
    ])
    return result["public_id"]

@receiver(pre_save, sender=ProductImages)
def compress_images_before_save(sender, instance, **kwargs):
    # Check if image1 is a file, not already a public_id (i.e., not already uploaded)
    if isinstance(instance.image1, InMemoryUploadedFile):
        instance.image1 = compress_and_upload(instance.image1)

    if isinstance(instance.image2, InMemoryUploadedFile):
        instance.image2 = compress_and_upload(instance.image2)

    if isinstance(instance.image3, InMemoryUploadedFile):
        instance.image3 = compress_and_upload(instance.image3)

    if isinstance(instance.image4, InMemoryUploadedFile):
        instance.image4 = compress_and_upload(instance.image4)


User = get_user_model()  # Get the custom user model


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


@receiver(post_save, sender=Message)
def chat_message_notification(sender, instance, created, **kwargs):
    if created:
        # Determine the receiver of the message
        chat = instance.chat
        if instance.sender == chat.buyer:
            receiver = chat.seller  # If sender is buyer, receiver is seller
        else:
            receiver = chat.buyer  # If sender is seller, receiver is buyer

        # Get the product name associated with the chat
        product_name = chat.product.title  # Assuming Chat has a ForeignKey to Product

        # Create a notification for the receiver with product name
        Notification.objects.create(
            user=receiver,
            message=(
                f"You have a new message from <b>{instance.sender.first_name} {instance.sender.last_name}</b> "
                f"about <b>{product_name}</b>: '{instance.text[:30]}...'"
            )
        )