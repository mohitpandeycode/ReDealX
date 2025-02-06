from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="home"),
    path('logout/', views.handle_logout, name="logout"),
    path('allproducts/', views.allproducts, name="allprod"),
    path('sell-item/', views.sellItem, name="sellitem"),
    path('product-by-category/<category>/', views.prodbyCategory, name="categoryproduct"),
    path('product-details/<slug>/', views.view_Product, name="viewproduct"),
    path('product-Seller/<slug>/', views.viewSeller, name="viewSeller"),
    path('report-product/<slug>/', views.reportad, name="reportad"),
    path('profile?-page&view-details/', views.profilePage, name="profilePage"),
    path('your-posted?top?ads-view&details/', views.adsPage, name="adspage"),
    path('delete-post?select?ad-view&delete/<slug>/', views.deleteAd, name="deletead"),
    path('settings/privacy/', views.settingsPage, name="settings"),
    path('delete/useraccount/', views.deleteAccount, name="deleteaccount"),
   

]
 