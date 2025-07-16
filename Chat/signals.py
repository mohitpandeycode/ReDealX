from django.db.models.signals import post_save
from django.dispatch import receiver
from home.models import CustomUser, Product
from Chat.models import Chat, Message

@receiver(post_save, sender=CustomUser)
def create_welcome_chat(sender, instance, created, **kwargs):
    if not created:
        return

    # Get admin user (assumes at least one superuser exists)
    try:
        admin_user = CustomUser.objects.filter(is_superuser=True).first()
        if not admin_user or admin_user == instance:
            return  # Don't create chat with self or if no admin
    except CustomUser.DoesNotExist:
        return

    # Choose a product to attach the chat to — customize as needed
    welcome_product = Product.objects.first()
    if not welcome_product:
        return  # Can't create chat without a product

    # Avoid duplicate chats
    chat, created_chat = Chat.objects.get_or_create(
        product=welcome_product,
        buyer=instance,
        seller=admin_user
    )

    # Send a welcome message if new chat created
    if created_chat:
        Message.objects.create(
            chat=chat,
            sender=admin_user,
            text = f"Hi {instance.first_name or instance.username} 👋, welcome to 🎉 ReDealX! 🎉 We're glad to have you here. Feel free to ask us anything — we're here to help! 😊"
        )
