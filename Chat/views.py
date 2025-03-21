
from Chat.models import *
from home.models import *
from home.views import *
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Chat, Message
from home.models import Product, CustomUser
from django.http import JsonResponse,HttpResponseNotFound
import json




# Create your views here.
# chats page
@login_required
def chatsPage(request):
    # Handle search and authentication if needed
    if 'address' in request.GET or 'prod' in request.GET:
        search_results = search_products(request)
        return render(request, "allProducts.html", {'products': search_results} if search_results.exists() else {})

    auth_response = handle_user_auth(request)
    if auth_response:
        return auth_response

    # Fetch chats where the user is either the buyer or seller
    user_chats = Chat.objects.filter(
        Q(buyer=request.user) | Q(seller=request.user)
    ).prefetch_related("messages").order_by('-created_at')

    # Fetch unread notifications
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')

    # Fetch user wishlist items
    user_wishlist = WishlistItem.objects.filter(user=request.user).values_list('product_id', flat=True)

    context = {
        'chats': user_chats,
        'notifications': notifications,
        'user_wishlist': list(user_wishlist)
    }
    return render(request, 'chatPage.html', context)




@login_required
def sentOffer(request):
    """Handles new chat creation when a buyer contacts a seller for a product."""
    if request.method == "POST":
        product = get_object_or_404(Product, slug=request.POST.get('prodslug'))
        seller = product.seller
        buyer = request.user
        message_text = request.POST.get('firstchat')

        # Ensure buyer is not the seller
        if buyer == seller:
            return redirect('home')  # Prevent user from messaging themselves

        # Get or create chat between buyer & seller for this product
        chat, created = Chat.objects.get_or_create(product=product, buyer=buyer, seller=seller)

        # Only create message if chat is new
        if created and message_text:
            Message.objects.create(chat=chat, sender=buyer, text=message_text)

        return redirect('chats')  # Redirect to the chats page (Ensure this URL name is correct)
    
    return redirect('home')  # Redirect in case of GET request



@login_required
def get_messages(request, chat_id):
    print(f"🔍 Fetching messages for chat ID: {chat_id}")

    chat = Chat.objects.filter(id=chat_id).first()
    
    if not chat:
        print(f"❌ Chat with ID {chat_id} not found!")  # Debugging
        return HttpResponseNotFound('<h1>Chat Not Found</h1>')  # Ensures no HTML is returned

    messages = chat.messages.all().order_by('timestamp')

    return JsonResponse({
        'messages': [{'sender_id': msg.sender.id, 'text': msg.text} for msg in messages]
    })


@csrf_exempt
@login_required
def send_message(request, chat_id):
    if request.method == "POST":
        chat = get_object_or_404(Chat, id=chat_id)
        
        # Ensure user is part of this chat
        if request.user != chat.buyer and request.user != chat.seller:
            return JsonResponse({'error': 'Unauthorized'}, status=403)

        data = json.loads(request.body)
        message_text = data.get("text", "").strip()

        if message_text:
            Message.objects.create(chat=chat, sender=request.user, text=message_text)
            return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})
