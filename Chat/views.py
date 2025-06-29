
from Chat.models import *
from home.models import *
from home.views import *
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Chat, Message
from home.models import Product, CustomUser
from django.http import JsonResponse,HttpResponseNotFound
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
import json




# Create your views here.
# chats page
@login_required
def chatsPage(request):
    if 'address' in request.GET or 'prod' in request.GET:
        search_results = search_products(request)
        return render(request, "allProducts.html", {'products': search_results} if search_results.exists() else {})

    auth_response = handle_user_auth(request)
    if auth_response:
        return auth_response

    user_chats = Chat.objects.filter(
        Q(buyer=request.user) | Q(seller=request.user)
    ).select_related("buyer", "seller", "product") \
     .prefetch_related("messages", "product__images") \
     .order_by('-created_at')

    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
    user_wishlist = WishlistItem.objects.filter(user=request.user).values_list('product_id', flat=True)

    return render(request, 'chatPage.html', {
        'chats': user_chats,
        'notifications': notifications,
        'user_wishlist': list(user_wishlist)
    })


@login_required
def get_messages(request, chat_id):
    chat = Chat.objects.filter(id=chat_id).first()
    if not chat:
        return HttpResponseNotFound('<h1>Chat Not Found</h1>')

    # Pagination: limit and offset
    limit = int(request.GET.get('limit', 40))
    offset = int(request.GET.get('offset', 0))

    messages = chat.messages.order_by('-timestamp')[offset:offset+limit]
    messages = list(reversed(messages))

    return JsonResponse({
        'messages': [{'sender_id': msg.sender.id, 'text': msg.text, 'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')} for msg in messages]
    })


@login_required
def send_message(request, chat_id):
    if request.method == "POST":
        chat = get_object_or_404(Chat, id=chat_id)

        if request.user != chat.buyer and request.user != chat.seller:
            return JsonResponse({'error': 'Unauthorized'}, status=403)

        data = json.loads(request.body)
        message_text = data.get("text", "").strip()

        if message_text:
            Message.objects.create(chat=chat, sender=request.user, text=message_text)
            return JsonResponse({'success': True})

    return JsonResponse({'success': False})


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

        return redirect('chats') 
    
    return redirect('home')  # Redirect in case of GET request

