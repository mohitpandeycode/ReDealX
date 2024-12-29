from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import *
from django.contrib.auth import authenticate, login, logout  
from django.contrib.auth.models import User  
from django.contrib import messages, auth
# Create your views here.

def index(request):
    products = Product.objects.order_by('?')[:8]
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
    products = Product.objects.order_by('?')
    context = {'products': products}
    auth_response = handle_user_auth(request)
    if auth_response:
        return auth_response  # Redirect if authentication actions occurred
    return render(request, 'allProducts.html', context)