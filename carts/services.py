from .models import Cart, CartItem

def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        cart, _ = Cart.objects.get_or_create(session_id=session_key)
    return cart

def merge_carts(user, session_key):
    guest_cart = Cart.objects.filter(session_id=session_key).first()
    user_cart, _ = Cart.objects.get_or_create(user=user)

    if not guest_cart:
        return False #nothing to merge
    
    # If user already has a cart
    if guest_cart.id != user_cart.id:
        for item in guest_cart.items.all():
            user_item, created = CartItem.objects.get_or_create(
                book=item.book,
                cart=user_cart
            )

            if not created:
                user_item.quantity += item.quantity
            else:
                user_item.quantity = item.quantity
            user_item.save()
        guest_cart.delete()
    else:
        # Convert guest cart into user cart
        guest_cart.user = user
        guest_cart.session_id = None
        guest_cart.save()
    return True