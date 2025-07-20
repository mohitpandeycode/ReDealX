from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q, Prefetch
from django.utils.html import escape
import json
from Chat.models import Chat, Message
from home.models import Product, CustomUser, Notification, WishlistItem
from home.views import search_products, handle_user_auth
from django.db.models import Subquery, OuterRef

@login_required
def chatsPage(request):
    # Search redirect
    if 'address' in request.GET or 'prod' in request.GET:
        search_results = search_products(request)
        return render(
            request,
            "allProducts.html",
            {'products': search_results} if search_results.exists() else {}
        )

    auth_response = handle_user_auth(request)
    if auth_response:
        return auth_response

    # Subquery to get the latest message text and timestamp
    latest_messages = Message.objects.filter(
        chat=OuterRef('pk')
    ).order_by('-timestamp')

    user_chats = Chat.objects.filter(
        Q(buyer=request.user) | Q(seller=request.user)
    ).select_related("buyer", "seller", "product") \
     .prefetch_related(
         "product__images"
     ).annotate(
         last_message_text=Subquery(latest_messages.values('text')[:1]),
         last_message_time=Subquery(latest_messages.values('timestamp')[:1])
     ).order_by('-last_message_time')

    notifications = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).order_by('-created_at')

    user_wishlist = WishlistItem.objects.filter(
        user=request.user
    ).values_list('product_id', flat=True)

    return render(request, 'chatPage.html', {
        'chats': user_chats,
        'notifications': notifications,
        'user_wishlist': list(user_wishlist)
    })



@login_required
def get_messages(request, chat_id):
    limit = int(request.GET.get('limit', 40))
    offset = int(request.GET.get('offset', 0))

    # Fetch the chat with messages and their senders
    chat = get_object_or_404(
        Chat.objects.prefetch_related(
            Prefetch(
                'messages',
                queryset=Message.objects.select_related('sender').order_by('-timestamp')
            )
        ),
        id=chat_id
    )

    # Retrieve messages from the chat and slice manually
    full_messages = list(chat.messages.all())
    selected_messages = list(reversed(full_messages[offset:offset + limit]))

    # Mark unread messages (from others) as read
    unread_ids = [
        msg.id for msg in selected_messages
        if not msg.is_read and msg.sender != request.user
    ]
    if unread_ids:
        Message.objects.filter(id__in=unread_ids).update(is_read=True)

    return JsonResponse({
        'messages': [
            {
                'sender_id': msg.sender.id,
                'text': msg.text,
                'timestamp': msg.timestamp.isoformat()
            }
            for msg in selected_messages
        ]
    })


@login_required
def send_message(request, chat_id):
    if request.method != "POST":
        return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)

    chat = get_object_or_404(Chat, id=chat_id)

    # Ensure user is part of the chat
    if request.user != chat.buyer and request.user != chat.seller:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    try:
        data = json.loads(request.body)
        message_text = data.get("text", "").strip()
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

    if message_text:
        safe_text = escape(message_text)
        Message.objects.create(chat=chat, sender=request.user, text=safe_text)
        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Empty message'})


@login_required
def sentOffer(request):
    """
    Handles new chat creation when a buyer contacts a seller for a product.
    """
    if request.method == "POST":
        product_slug = request.POST.get('prodslug')
        message_text = request.POST.get('firstchat', "").strip()

        product = get_object_or_404(Product, slug=product_slug)
        seller = product.seller
        buyer = request.user

        # Prevent user from sending message to themselves
        if buyer == seller:
            return redirect('home')

        # Create or get existing chat
        chat, created = Chat.objects.get_or_create(
            product=product,
            buyer=buyer,
            seller=seller
        )

        # Create initial message if chat is new
        if created and message_text:
            Message.objects.create(chat=chat, sender=buyer, text=escape(message_text))

        return redirect('chats')

    return redirect('home')
