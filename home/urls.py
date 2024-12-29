from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="home"),
    path('allproducts/', views.allproducts, name="allprod"),
    path('logout/', views.handle_logout, name="logout"),

]
 