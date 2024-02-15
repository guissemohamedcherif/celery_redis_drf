from rest_framework import status
from rest_framework.response import Response
from .models import Cart, User, Order, Produit
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


def add_item_to_order(user, list_item):
    cart, created = Cart.objects.get_or_create(user=user)
    cart.clear_cart()
    for el in list_item:
        produit = Produit.objects.get(id=el.get('produit'))
        if produit.quantite >= int(el.get('quantite')):
            total = produit.prix_afficher * int(el.get('quantite'))
            points = produit.points * int(el.get('quantite'))
            cartItemSerializer = CartItemSerializer(
                data={
                    "quantite": el.get('quantite'),
                    "prix": produit.prix_afficher,
                    "produit": produit.id,
                    "cart": cart.id,
                    })
            if cartItemSerializer.is_valid():
                cartItemSerializer.save()
                cart.total += total
                cart.total_points += points
                cart.save()
                cart.items.add(cartItemSerializer.data['id'])
    if cart:
        return cart
