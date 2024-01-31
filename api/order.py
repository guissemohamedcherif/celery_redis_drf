from rest_framework import status
from rest_framework.response import Response
from .models import Cart, CartItem, Order
from .serializers import CartItemSerializer

def add_to_cart(cart, list_item):
    cart, created = Cart.objects.get_or_create(id=cart.id)
    for el in list_item:
        cartItemSerializer = CartItemSerializer(
            data={
                "quantite": el.get('quantite'),
                "prix": el.get('prix'),
                "produit": el.get('produit'),
                "cart": cart.id
                })
        if cartItemSerializer.is_valid():
            cartItemSerializer.save()
            cart.items.add(cartItemSerializer.data['id'])
    return Response({"message": "Produit ajouté au panier avec succès", "cart": cart.slug}, status=status.HTTP_200_OK)
