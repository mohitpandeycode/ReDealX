from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="home"),
    path('logout/', views.handle_logout, name="logout"),
    path('allproducts/', views.allproducts, name="allprod"),
    path('sell-item/', views.sellItem, name="sellitem"),
   

]
 