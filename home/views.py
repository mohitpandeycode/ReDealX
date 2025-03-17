from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib import messages, auth
from django.contrib.auth import update_session_auth_hash
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.utils.timezone import now
from datetime import timedelta
import random
from django.core.paginator import Paginator

# Home page
def index(request):
    if 'address' in request.GET or 'prod' in request.GET:
        search_results = search_products(request)
        if search_results.exists():
            return render(request, "allProducts.html", {'products': search_results})
        else:
            return render(request, "allProducts.html")
    
    products = Product.objects.order_by('?').prefetch_related('images')[:16]
    categories = Category.objects.order_by('?')[:5]

    auth_response = handle_user_auth(request)
    if auth_response:
        return auth_response
    
    user_wishlist = []
    notifications = ''
    if request.user.is_authenticated:
        user_wishlist = WishlistItem.objects.filter(user=request.user).values_list('product_id', flat=True)
        notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
    
    context = {
        'products': products,
        'categories': categories,
        'user_wishlist': list(user_wishlist),
        'notifications': notifications
    }
    return render(request, 'index.html', context)

# Authentication handler (unchanged)
def handle_user_auth(request):
    if request.method == "POST":
        form_type = request.POST.get("form_type")
        
        if form_type == "signup":
            first_name = request.POST.get('fname')
            last_name = request.POST.get('lname')
            username = request.POST.get('username')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            password = request.POST.get('password')
            cpassword = request.POST.get('cpassword')
            
            if password != cpassword:
                messages.error(request, "Passwords do not match.")
                return redirect(request.path)
            if CustomUser.objects.filter(username=username).exists():
                messages.warning(request, "Username already taken. Sign in again!!!")
                return redirect(request.path)
            if CustomUser.objects.filter(phone_number=phone).exists():
                messages.warning(request, "User from this number is already signed in.")
                return redirect(request.path)

            user = CustomUser.objects.create_user(username, email, password)
            user.first_name = first_name
            user.last_name = last_name
            user.phone_number = phone
            user.save()
            messages.success(request, "Account created successfully.")
            return redirect(request.path)

        elif form_type == "login":
            username = request.POST.get('lusername')
            password = request.POST.get('lpassword')
            
            if not CustomUser.objects.filter(username=username).exists():
                messages.error(request, 'Invalid Username!')
                return redirect(request.path)

            user = auth.authenticate(request, username=username, password=password)
            if user is None:
                messages.error(request, 'Invalid Password!')
                return redirect(request.path)
            
            auth.login(request, user)
            messages.success(request, "Logged in successfully.")
            return redirect(request.path)

# Logout
@login_required
def handle_logout(request):
    logout(request)
    messages.success(request, "You're logged out")
    return redirect("/")

# All products
def allproducts(request):
    if 'address' in request.GET or 'prod' in request.GET:
        search_results = search_products(request)
        if search_results.exists():
            return render(request, "allProducts.html", {'products': search_results})
        else:
            return render(request, "allProducts.html")

    all_products = Product.objects.all().order_by('-created_at').prefetch_related('images')
    two_months_ago = now() - timedelta(days=60)
    recent_products = list(all_products.filter(created_at__gte=two_months_ago))
    random.shuffle(recent_products)
    first_50_products = recent_products[:50]
    remaining_products = all_products.exclude(id__in=[p.id for p in first_50_products])
    products = first_50_products + list(remaining_products)

    paginator = Paginator(products, 60)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    user_wishlist = []
    notifications = ''
    if request.user.is_authenticated:
        user_wishlist = WishlistItem.objects.filter(user=request.user).values_list('product_id', flat=True)
        notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')

    context = {'products': page_obj, 'allprod': all_products, 'user_wishlist': list(user_wishlist), 'notifications': notifications}
    
    auth_response = handle_user_auth(request)
    if auth_response:
        return auth_response
    
    return render(request, 'allProducts.html', context)

# Sell item
def sellItem(request):
    auth_response = handle_user_auth(request)
    if auth_response:
        return auth_response

    condition_choices = Product.condition_choices
    category = Category.objects.all()

    if request.method == "POST":
        cate_name = request.POST.get('category')
        category_instance = Category.objects.filter(name=cate_name).first()

        brand = request.POST.get('brand')
        title = request.POST.get('title')
        description = request.POST.get('description')
        condition = request.POST.get('condition')
        price = request.POST.get('price')
        location = request.POST.get('location')
        image1 = request.FILES.get('img1')
        image2 = request.FILES.get('img2')
        image3 = request.FILES.get('img3')
        image4 = request.FILES.get('img4')

        if category_instance:
            product = Product.objects.create(
                category=category_instance,
                brand=brand,
                title=title,
                description=description,
                price=price,
                location=location,
                condition=condition,
                seller=request.user
            )
            ProductImages.objects.create(
                product=product,
                image1=image1,
                image2=image2,
                image3=image3,
                image4=image4,
                user=request.user
            )
            messages.success(request, "Product added successfully.")
            return redirect('/allproducts/')
        else:
            messages.error(request, "Category not found.")
            return redirect('sell_item')
    
    user_wishlist = []
    notifications = ''
    if request.user.is_authenticated:
        user_wishlist = WishlistItem.objects.filter(user=request.user).values_list('product_id', flat=True)
        notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')

    context = {'condition_choices': condition_choices, 'categories': category, 'user_wishlist': list(user_wishlist), 'notifications': notifications}
    return render(request, 'sellitem.html', context)

# Search products
def search_products(request):
    address = request.GET.get('address')
    product = request.GET.get('prod')
    products = Product.objects.all().prefetch_related('images')

    if address:
        products = products.filter(location__icontains=address)
    if product:
        products = products.filter(
            Q(brand__icontains=product) |
            Q(title__icontains=product) |
            Q(description__icontains=product) |
            Q(category__name__icontains=product)
        )
    
    user_wishlist = []
    notifications = ''
    if request.user.is_authenticated:
        user_wishlist = WishlistItem.objects.filter(user=request.user).values_list('product_id', flat=True)
        notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')

    return products

# Products by category
def prodbyCategory(request, category):
    if 'address' in request.GET or 'prod' in request.GET:
        search_results = search_products(request)
        if search_results.exists():
            return render(request, "allProducts.html", {'products': search_results})
        else:
            return render(request, "allProducts.html")
    
    products = Product.objects.filter(category__name=category).prefetch_related('images')
    
    user_wishlist = []
    notifications = ''
    if request.user.is_authenticated:
        user_wishlist = WishlistItem.objects.filter(user=request.user).values_list('product_id', flat=True)
        notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
    
    context = {'products': products, 'user_wishlist': list(user_wishlist), 'notifications': notifications}
    return render(request, 'allProducts.html', context)

# Product details
def view_Product(request, slug):
    if 'address' in request.GET or 'prod' in request.GET:
        search_results = search_products(request)
        if search_results.exists():
            return render(request, "allProducts.html", {'products': search_results})
        else:
            return render(request, "allProducts.html")
    
    auth_response = handle_user_auth(request)
    if auth_response:
        return auth_response
        
    product = Product.objects.prefetch_related('images').get(slug=slug)
    product.views += 1
    product.save()
    
    user_wishlist = []
    notifications = ''
    if request.user.is_authenticated:
        user_wishlist = WishlistItem.objects.filter(user=request.user).values_list('product_id', flat=True)
        notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')

    context = {'product': product, 'user_wishlist': list(user_wishlist), 'notifications': notifications}
    return render(request, 'viewProduct.html', context)

# Report ad
@login_required
def reportad(request, slug):
    product = get_object_or_404(Product, slug=slug)

    if request.method == "POST":
        reason = request.POST.get("reason")
        description = request.POST.get("description", "").strip()

        if not reason:
            messages.error(request, "Please select a reason")
            return redirect('viewproduct', slug=slug)

        Repoerted_ad.objects.create(
            product=product,
            reporter=request.user,
            reason=reason,
            description=description[:500]
        )
        messages.success(request, "We'll be taking care of this as soon as possible.")
        return redirect('viewproduct', slug=slug)
    
    context = {'product': product}
    return render(request, 'viewProduct.html', context)

# Profile page
@login_required
def profilePage(request):
    if 'address' in request.GET or 'prod' in request.GET:
        search_results = search_products(request)
        if search_results.exists():
            return render(request, "allProducts.html", {'products': search_results})
        else:
            return render(request, "allProducts.html")
    
    auth_response = handle_user_auth(request)
    if auth_response:
        return auth_response

    product_ads = Product.objects.filter(seller=request.user).prefetch_related('images')
    
    user_wishlist = []
    notifications = ''
    if request.user.is_authenticated:
        user_wishlist = WishlistItem.objects.filter(user=request.user).values_list('product_id', flat=True)
        notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')

    context = {'products': product_ads, 'user_wishlist': list(user_wishlist), 'notifications': notifications}
    return render(request, 'profilePage.html', context)

# Ads page
@login_required
def adsPage(request):
    if 'address' in request.GET or 'prod' in request.GET:
        search_results = search_products(request)
        if search_results.exists():
            return render(request, "allProducts.html", {'products': search_results})
        else:
            return render(request, "allProducts.html")
    
    auth_response = handle_user_auth(request)
    if auth_response:
        return auth_response

    product_ads = Product.objects.filter(seller=request.user).prefetch_related('images')
    
    user_wishlist = []
    notifications = ''
    if request.user.is_authenticated:
        user_wishlist = WishlistItem.objects.filter(user=request.user).values_list('product_id', flat=True)
        notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')

    context = {'products': product_ads, 'user_wishlist': list(user_wishlist), 'notifications': notifications}
    return render(request, 'adsPage.html', context)

# Delete ad
@login_required
def deleteAd(request, slug):
    product = Product.objects.get(slug=slug)
    product.delete()
    messages.success(request, "Product deleted successfully.")
    return redirect('adspage')

# Settings page
@login_required
def settingsPage(request):
    if 'address' in request.GET or 'prod' in request.GET:
        search_results = search_products(request)
        if search_results.exists():
            return render(request, "allProducts.html", {'products': search_results})
        else:
            return render(request, "allProducts.html")
        
    if request.method == "POST":
        form_type = request.POST.get("form_type")
        
        if form_type == "changepass":
            newpass = request.POST.get('newpass')
            cpass = request.POST.get('cpass')
            if newpass != cpass:
                messages.error(request, "Passwords do not match.")
                return redirect('settings')
            elif request.user.check_password(newpass):
                messages.error(request, "Password is same as old password.")
                return redirect('settings')
            else:
                user = request.user
                user.set_password(newpass)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Password changed successfully.")
                return redirect('settings')
            
        elif form_type == "personaldetails":
            fName = request.POST.get('fname')
            lName = request.POST.get('lname')
            phone = request.POST.get('phone')
            address = request.POST.get('address')
            email = request.POST.get('email')
            user = request.user
            user.first_name = fName
            user.last_name = lName
            user.phone_number = phone
            user.email = email
            user.address = address
            user.save()
            messages.success(request, "Your details have been updated successfully!")
            return redirect('settings')
        
    return render(request, 'settings.html')

# Delete account
@login_required
def deleteAccount(request):
    user = request.user
    user.delete()
    messages.success(request, "Account deleted successfully.")
    return redirect('/')

# Seller profile
def viewSeller(request, slug):
    if 'address' in request.GET or 'prod' in request.GET:
        search_results = search_products(request)
        if search_results.exists():
            return render(request, "allProducts.html", {'products': search_results})
        else:
            return render(request, "allProducts.html")
    
    auth_response = handle_user_auth(request)
    if auth_response:
        return auth_response
    
    seller = CustomUser.objects.get(username=slug)
    products = Product.objects.filter(seller=seller).prefetch_related('images')
    
    user_wishlist = []
    notifications = ''
    if request.user.is_authenticated:
        user_wishlist = WishlistItem.objects.filter(user=request.user).values_list('product_id', flat=True)
        notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')

    context = {'seller': seller, 'products': products, 'user_wishlist': list(user_wishlist), 'notifications': notifications}
    return render(request, 'sellerprofile.html', context)

# Wishlist
@login_required
def wishlist(request):
    if 'address' in request.GET or 'prod' in request.GET:
        search_results = search_products(request)
        if search_results.exists():
            return render(request, "allProducts.html", {'products': search_results})
        else:
            return render(request, "allProducts.html")
    
    products = WishlistItem.objects.filter(user=request.user).order_by('-created_at').prefetch_related('product__images')
    
    user_wishlist = []
    notifications = ''
    if request.user.is_authenticated:
        user_wishlist = WishlistItem.objects.filter(user=request.user).values_list('product_id', flat=True)
        notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')

    context = {'products': products, 'user_wishlist': list(user_wishlist), 'notifications': notifications}
    return render(request, 'wishlist.html', context)

# Toggle wishlist
@login_required
def toggle_wishlist(request):
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        product = get_object_or_404(Product, id=product_id)
        wishlist_item, created = WishlistItem.objects.get_or_create(user=request.user, product=product)

        if not created:
            wishlist_item.delete()
            if product.likes > 0:
                product.likes -= 1
                product.save()
            return JsonResponse({"status": "removed", "message": "Removed from Wishlist"})
        else:
            product.likes += 1
            product.save()
            return JsonResponse({"status": "added", "message": "Added to Wishlist"})
    
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

# Mark notification as read
@login_required
@csrf_exempt
def mark_notification_as_read(request):
    if request.method == "POST":
        notification_id = request.POST.get("notification_id")
        try:
            notification = Notification.objects.get(id=notification_id, user=request.user)
            notification.is_read = True
            notification.save()
            return JsonResponse({"status": "success"})
        except Notification.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Notification not found"}, status=404)
    
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)



# chats page
@login_required
def chatsPage(request):
    if 'address' in request.GET or 'prod' in request.GET:
        search_results = search_products(request)
        if search_results.exists():
            return render(request, "allProducts.html", {'products': search_results})
        else:
            return render(request, "allProducts.html")
    
    auth_response = handle_user_auth(request)
    if auth_response:
        return auth_response

    user_wishlist = []
    notifications = ''
    if request.user.is_authenticated:
        user_wishlist = WishlistItem.objects.filter(user=request.user).values_list('product_id', flat=True)
        notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')

    context = {'user_wishlist': list(user_wishlist), 'notifications': notifications}
    return render(request, 'chatPage.html', context)