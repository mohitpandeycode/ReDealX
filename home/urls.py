from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="home"),
    path('logout/', views.handle_logout, name="logout"),
    path('allproducts/', views.allproducts, name="allprod"),
    path('sell-item/', views.sellItem, name="sellitem"),
    path('product-by-category/<category>/', views.prodbyCategory, name="categoryproduct"),
    path('product-details/<slug>/', views.view_Product, name="viewproduct"),
    path('profile-page-view-details', views.profilePage, name="profilePage"),
   

]
 