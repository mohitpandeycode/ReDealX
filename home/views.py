from django.shortcuts import render
from django.http import HttpResponse
from .models import *
# Create your views here.

def index(request):
    products = Product.objects.order_by('?')[:8]
    context = {'products': products}
    print(products[0].created_at)
    return render (request, 'index.html', context)