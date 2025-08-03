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
from django.db.models.functions import Random
from django.db.models import Prefetch, F
from django.views.decorators.cache import cache_page


# Home page
@cache_page(60 * 5)
def index(request):
    # Handle login/signup early
    auth_response = handle_user_auth(request)
    if auth_response:
        return auth_response

    # Handle search
    if 'address' in request.GET or 'prod' in request.GET:
        search_results = search_products(request)
        return render(request, "allProducts.html", {'products': search_results})

    # Random but optimized product/category fetch
    products = Product.objects.annotate(rand=Random()).order_by('rand').prefetch_related('images')[:16]
    categories = Category.objects.annotate(rand=Random()).order_by('rand')[:5]

    # Wishlist + notifications
    user_wishlist = []
    notifications = ''
    if request.user.is_authenticated:
        user_wishlist = WishlistItem.objects.filter(user=request.user).values_list('product_id', flat=True)
        notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')[:10]

    context = {
        'products': products,
        'categories': categories,
        'user_wishlist': list(user_wishlist),
        'notifications': notifications
    }
    return render(request, 'index.html', context)

# Handle user authentication (login/signup)
def handle_user_auth(request):
    if request.method != "POST":
        return None  # Only handle POST here

    form_type = request.POST.get("form_type")

    if form_type == "signup":
        first_name = request.POST.get('fname', '').strip()
        last_name = request.POST.get('lname', '').strip()
        username = request.POST.get('username', '').strip().lower()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '')
        cpassword = request.POST.get('cpassword', '')

        if password != cpassword:
            messages.error(request, "Passwords do not match.")
            return redirect(request.path)

        if CustomUser.objects.filter(username=username).exists():
            messages.warning(request, "Username already taken. Sign in again!")
            return redirect(request.path)

        if CustomUser.objects.filter(phone_number=phone).exists():
            messages.warning(request, "User with this phone number already exists.")
            return redirect(request.path)

        user = CustomUser.objects.create_user(username, email, password)
        user.first_name = first_name
        user.last_name = last_name
        user.phone_number = phone
        user.save()

        messages.success(request, "Account created successfully.")
        return redirect(request.path)

    elif form_type == "login":
        username = request.POST.get('lusername', '').strip().lower()
        password = request.POST.get('lpassword', '')

        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            messages.error(request, 'Invalid Username!')
            return redirect(request.path)

        user = auth.authenticate(request, username=username, password=password)
        if user is None:
            messages.error(request, 'Invalid Password!')
            return redirect(request.path)

        auth.login(request, user)
        messages.success(request, "Logged in successfully.")
        return redirect(request.path)

    return None


# Logout
@login_required
def handle_logout(request):
    logout(request)
    messages.success(request, "You're logged out")
    return redirect("/")


# All products page
@cache_page(60 * 10)
def allproducts(request):
    # Handle authentication (POST)
    auth_response = handle_user_auth(request)
    if auth_response:
        return auth_response

    # Handle search (GET)
    if 'address' in request.GET or 'prod' in request.GET:
        search_results = search_products(request)
        return render(request, "allProducts.html", {'products': search_results}) if search_results.exists() else render(request, "allProducts.html")

    # Fetch all products and sort
    all_products = Product.objects.all().order_by('-created_at').prefetch_related('images')
    two_months_ago = now() - timedelta(days=60)
    
    recent_products = list(all_products.filter(created_at__gte=two_months_ago))
    random.shuffle(recent_products)
    
    first_50 = recent_products[:50]
    remaining = all_products.exclude(id__in=[p.id for p in first_50])
    final_products = first_50 + list(remaining)

    # Paginate the final product list
    paginator = Paginator(final_products, 60)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # User-specific data
    user_wishlist = []
    notifications = ''
    if request.user.is_authenticated:
        user_wishlist = WishlistItem.objects.filter(user=request.user).values_list('product_id', flat=True)
        notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')[:10]

    # Final context
    context = {
        'products': page_obj,
        'allprod': all_products,
        'user_wishlist': list(user_wishlist),
        'notifications': notifications,
    }

    return render(request, 'allProducts.html', context)


# Sell item
def sellItem(request):
    # Check for signup/login handling
    auth_response = handle_user_auth(request)
    if auth_response:
        return auth_response

    # Load choices and categories
    condition_choices = Product.condition_choices
    categories = Category.objects.all()

    if request.method == "POST":
        # Get form inputs
        cate_name = request.POST.get('category')
        category_instance = Category.objects.filter(name=cate_name).first()
        other_category = request.POST.get('otherCategory')
        brand = request.POST.get('brand')
        title = request.POST.get('title')
        description = request.POST.get('description')
        condition = request.POST.get('condition')
        price = request.POST.get('price')
        location = request.POST.get('location')
        images = [request.FILES.get(f'img{i}') for i in range(1, 5)]
        show_number = request.POST.get('show_phone')

        # Validate category
        if not category_instance:
            messages.error(request, "Category not found.")
            return redirect('/sell-item')

        # Create product
        product = Product.objects.create(
            category=category_instance,
            other_category = other_category,
            brand=brand,
            title=title,
            description=description,
            price=price,
            location=location,
            condition=condition,
            seller=request.user,
            showNumber=show_number == 'on'
        )

        # Create associated images
        ProductImages.objects.create(
            product=product,
            image1=images[0],
            image2=images[1],
            image3=images[2],
            image4=images[3],
            user=request.user
        )

        messages.success(request, "Product added successfully.")
        return redirect('/allproducts/')

    # Collect user data for context
    user_wishlist = []
    notifications = ''
    if request.user.is_authenticated:
        user_wishlist = WishlistItem.objects.filter(user=request.user).values_list('product_id', flat=True)
        notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')[:10]

    context = {
        'condition_choices': condition_choices,
        'categories': categories,
        'user_wishlist': list(user_wishlist),
        'notifications': notifications
    }

    return render(request, 'sellitem.html', context)


# Search products
def search_products(request):
    address_query = request.GET.get('address')
    product_query = request.GET.get('prod')

    # Initial queryset with prefetch for related images
    products = Product.objects.all().prefetch_related('images')

    # Apply address filter
    if address_query:
        products = products.filter(location__icontains=address_query)

    # Apply product-related filters
    if product_query:
        products = products.filter(
            Q(brand__icontains=product_query) |
            Q(title__icontains=product_query) |
            Q(description__icontains=product_query) |
            Q(category__name__icontains=product_query)
        )

    # Just return the queryset, caller will handle rendering and context
    return products


# Products by category
@cache_page(60 * 10)
def prodbyCategory(request, category):
     # Check for signup/login handling
    auth_response = handle_user_auth(request)
    if auth_response:
        return auth_response
    
    # Handle search (fallback if user uses search bar)
    if 'address' in request.GET or 'prod' in request.GET:
        search_results = search_products(request)
        return render(request, "allProducts.html", {
            'products': search_results if search_results.exists() else [],
        })

    # Fetch the category object or return 404
    category_obj = get_object_or_404(Category, name__iexact=category)

    # Get all products under the category
    products_qs = Product.objects.filter(category=category_obj)\
        .prefetch_related(Prefetch('images'))\
        .order_by('-created_at')

    # Pagination setup: 60 products per page
    paginator = Paginator(products_qs, 60)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Authenticated user data
    user_wishlist = []
    notifications = []
    if request.user.is_authenticated:
        user_wishlist = WishlistItem.objects.filter(user=request.user)\
            .values_list('product_id', flat=True)
        notifications = Notification.objects.filter(user=request.user, is_read=False)\
            .order_by('-created_at')[:10]

    context = {
        'products': page_obj,  # paginated object
        'user_wishlist': list(user_wishlist),
        'notifications': notifications,
        'selected_category': category_obj.name,
        'paginator': paginator,
        'page_obj': page_obj,
        'products_qs': products_qs
    }

    return render(request, 'allProducts.html', context)



# View product details
def view_Product(request, slug):
    # Handle auth (signup/login)
    auth_response = handle_user_auth(request)
    if auth_response:
        return auth_response
    
    #  Handle search
    if 'address' in request.GET or 'prod' in request.GET:
        search_results = search_products(request)
        return render(request, "allProducts.html", {
            'products': search_results if search_results.exists() else [],
        })



    #  Get the product or return 404 (safer than .get())
    product = get_object_or_404(
        Product.objects.prefetch_related('images'),
        slug=slug
    )

    # Increment view count using F expression (no race condition)
    Product.objects.filter(pk=product.pk).update(views=F('views') + 1)

    #  Authenticated user extras
    user_wishlist = []
    notifications = []
    if request.user.is_authenticated:
        user_wishlist = WishlistItem.objects.filter(user=request.user)\
            .values_list('product_id', flat=True)
        notifications = Notification.objects.filter(user=request.user, is_read=False)\
            .order_by('-created_at')[:10]

    #Context
    context = {
        'product': product,
        'user_wishlist': list(user_wishlist),
        'notifications': notifications,
    }
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
       #  Handle search
    if 'address' in request.GET or 'prod' in request.GET:
        search_results = search_products(request)
        return render(request, "allProducts.html", {
            'products': search_results if search_results.exists() else [],
        })

    product_ads = Product.objects.filter(seller=request.user).prefetch_related('images')
    
    user_wishlist = []
    notifications = ''
    if request.user.is_authenticated:
        user_wishlist = WishlistItem.objects.filter(user=request.user).values_list('product_id', flat=True)
        notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')[:10]

    context = {'products': product_ads, 'user_wishlist': list(user_wishlist), 'notifications': notifications}
    return render(request, 'profilePage.html', context)

# Ads page
@login_required
def adsPage(request):
    #  Handle search
    if 'address' in request.GET or 'prod' in request.GET:
        search_results = search_products(request)
        return render(request, "allProducts.html", {
            'products': search_results if search_results.exists() else [],
        })
    
    auth_response = handle_user_auth(request)
    if auth_response:
        return auth_response

    product_ads = Product.objects.filter(seller=request.user).prefetch_related('images')
    
    user_wishlist = []
    notifications = ''
    if request.user.is_authenticated:
        user_wishlist = WishlistItem.objects.filter(user=request.user).values_list('product_id', flat=True)
        notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')[:10]

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
    # Check for auth redirect (login/signup)
    auth_response = handle_user_auth(request)
    if auth_response:
        return auth_response
    
    # Handle search queries first
    if 'address' in request.GET or 'prod' in request.GET:
        search_results = search_products(request)
        return render(request, "allProducts.html", {
            'products': search_results if search_results.exists() else [],
        })

    # Get seller or 404
    seller = get_object_or_404(CustomUser, username=slug)

    # Fetch seller's products efficiently
    products = Product.objects.filter(seller=seller).prefetch_related('images')

    # Handle user data
    user_wishlist = []
    notifications = []
    if request.user.is_authenticated:
        user_wishlist = WishlistItem.objects.filter(
            user=request.user
        ).values_list('product_id', flat=True)

        notifications = Notification.objects.filter(
            user=request.user, is_read=False
        ).order_by('-created_at')[:10]  # limit notifications

    context = {
        'seller': seller,
        'products': products,
        'user_wishlist': list(user_wishlist),
        'notifications': notifications
    }
    return render(request, 'sellerprofile.html', context)

# Wishlist
@cache_page(60 * 10)
@login_required
def wishlist(request):
    # Handle search queries early
    if 'address' in request.GET or 'prod' in request.GET:
        search_results = search_products(request)
        return render(request, "allProducts.html", {
            'products': search_results if search_results.exists() else [],
        })

    # Fetch wishlist items and prefetch product images
    products = WishlistItem.objects.filter(
        user=request.user
    ).select_related('product').prefetch_related('product__images').order_by('-created_at')

    # Fetch wishlist product IDs and notifications for UI rendering
    user_wishlist = WishlistItem.objects.filter(
        user=request.user
    ).values_list('product_id', flat=True)

    notifications = Notification.objects.filter(
        user=request.user, is_read=False
    ).order_by('-created_at')[:10]

    context = {
        'products': products,
        'user_wishlist': list(user_wishlist),
        'notifications': notifications
    }
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


# Help center Page
def helpCenter(request):
    return render(request, 'helpPage.html')


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
        notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')[:10]

    context = {'user_wishlist': list(user_wishlist), 'notifications': notifications}
    return render(request, 'chatPage.html', context)