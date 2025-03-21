from django.db import models
from home.models import *

# Create your models here

# chat Models

class Chat(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="chat_product")
    buyer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="buyer_chats")
    seller = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="seller_chats")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'buyer', 'seller')  # Ensure one chat per product between buyer & seller

    def __str__(self):
        return f"Chat on {self.product.title} - {self.buyer.username} & {self.seller.username}"

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.username}"