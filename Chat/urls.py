from django.urls import path
from . import views


urlpatterns = [
    path('', views.chatsPage, name="chats"),
    path('sentoffer/', views.sentOffer, name="sentOffer"),
    path('get-messages/<int:chat_id>/', views.get_messages, name='get_messages'),

    path('send-message/<int:chat_id>/', views.send_message, name='send_message'),

   
]
