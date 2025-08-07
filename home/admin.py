from django.contrib import admin
from .models import *
# Register your models here.

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone_number', 'is_verified')
    search_fields = ('username', 'email', 'phone_number')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'category', 'seller', 'condition', 'created_at')
    list_filter = ('category', 'condition')
    search_fields = ('title', 'description')

@admin.register(ProductImages)
class ProductImagesAdmin(admin.ModelAdmin):
    list_display = ('product', 'image1', 'image2', 'image3', 'image4', 'user')
    search_fields = ('product', 'user')

@admin.register(Repoerted_ad)
class Repoerted_adAdmin(admin.ModelAdmin):
    list_display = ('reporter','product','reason','description','created_at')
    search_fields = ('reporter', 'product')


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')
    search_fields = ('user', 'product')


@admin.register(Notification)
class NotificationtemAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'created_at')
    search_fields = ('user', 'message')


@admin.register(SiteVisit)
class SiteVisitAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'page_visited', 'visited_at')
    list_filter = ('visited_at',)
    search_fields = ('ip_address', 'page_visited')