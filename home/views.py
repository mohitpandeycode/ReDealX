from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import *
from django.contrib.auth import authenticate, login, logout  
from django.contrib.auth.models import User  
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
# Create your views here.

def index(request):
    products = Product.objects.order_by('?')[:8]
    for product in products:
        # Fetch the associated images for each product
        product.images = ProductImages.objects.filter(product=product)
    categories = Category.objects.order_by('?')[:5]
    auth_response = handle_user_auth(request)
    if auth_response:
        return auth_response  # Redirect if authentication actions occurred
    context = {'products': products,'categories':categories}
    return render (request, 'index.html', context)



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
                messages.error(request, "Username already taken.")
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


def handle_logout(request):
    logout(request)
    messages.success(request, "You're logged out")
    return redirect("/")


def allproducts(request):
    products = Product.objects.all()  # Fetch all products
    for product in products:
        # Fetch the associated images for each product
        product.images = ProductImages.objects.filter(product=product)
    
    context = {'products': products}
    auth_response = handle_user_auth(request)
    if auth_response:
        return auth_response  # Redirect if authentication actions occurred
    return render(request, 'allProducts.html', context)




def sellItem(request):
    auth_response = handle_user_auth(request)
    if auth_response:
        return auth_response  # Redirect if authentication actions occurred

    condition_choices = Product.condition_choices
    category = Category.objects.all()

    if request.method == "POST":
        cate_name = request.POST.get('category')  # Get the category name from the form
        category_instance = Category.objects.filter(name=cate_name).first()  # Get the Category instance

        # Handle other form fields
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

        # Check if the category instance exists
        if category_instance:
            product = Product.objects.create(
                category=category_instance,  # Assign the Category instance
                brand=brand,
                title=title,
                description=description,
                price=price,
                location=location,
                condition=condition,
                seller=request.user
            )

            # Create ProductImages
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
            return redirect('sell_item')  # Redirect back to the form

    context = {'condition_choices': condition_choices, 'categories': category}
    return render(request, 'sellitem.html', context)



