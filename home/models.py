
from django.db import models
from django.contrib.auth.models import AbstractUser

# Custom User Model
class CustomUser(AbstractUser):
    about_me = models.TextField(default='', null=True, blank=True)
    phone_number = models.IntegerField(unique=True, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='user_profiles/', blank=True, null=True)
    email = models.EmailField(default='', max_length=254, null=True, blank=True)
    is_verified = models.BooleanField(default=False)


    def __str__(self):
        return self.username


# Category Model
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    catagory_icon_FS = models.CharField(max_length=100, blank=True, null=True, default='')

    def __str__(self):
        return self.name


# Product Model
class Product(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='product_images/')
    location = models.TextField(default='',null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    seller = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # Link to user model
    category = models.ForeignKey(Category, related_name='products', on_delete=models.SET_NULL, null=True, blank=True)
    condition_choices = [
        ('new', 'New'),
        ('used', 'Used'),
        ('refurbished', 'Refurbished'),
    ]
    condition = models.CharField(max_length=20, choices=condition_choices, default='used')

    def __str__(self):
        return self.title
