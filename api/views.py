from rest_framework.response import Response
from api.serializers import *
from api.models import *
from rest_framework import generics
from api.notifications import Notif as notify
from django.utils import timezone
from django.contrib.auth import authenticate
from rest_framework_jwt.settings import api_settings
from rest_framework import status
from backend.settings import APP_NAME
import time
import re
REGEX = os.environ.get("regex")

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


class UserRegisterAPIView(generics.CreateAPIView):
    permission_classes = ()
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer

    REGEX_PATTERN = REGEX

    def post(self, request, *args, **kwargs):
        """
        Handle POST request for user registration.
        """
        pattern = re.compile(self.REGEX_PATTERN)
        if ('password' in request.data and request.data['password']
           and not pattern.match(request.data['password'])):
            return Response({
                "message": "Le mot de passe doit avoir au moins au minimum 8 caractères,1 caractère en majuscule, 1 caractère en minuscule, 1 nombre et 1 caractère spéciale"
                }, status=400)

        email = request.data.get("email")
        if User.objects.filter(email=email).first():
            return Response({"message":"Cet utilisateur existe déja dans la base de donnée"},status=400)
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            item = serializer.save()
            return Response(UserSerializer(item).data, status=201)
        return Response(serializer.errors, status=400)


class LoginView(generics.CreateAPIView):    
    permission_classes = ()
    queryset = User.objects.all()
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        if 'email' in request.data and request.data['email']:
            if 'password' in request.data and request.data['password']:
                try:
                    email = request.data['email']
                    search_item = User.objects.filter(email__iexact=email)
                    if search_item.exists():
                        item = search_item.last()
                        if item and item.email != email:
                            email = item.email
                            request.data['email'] = email
                    user = authenticate(request, email=email, password=request.data['password'])
                    if user:
                        token = jwt_encode_handler(jwt_payload_handler(user))
                        item = User.objects.get(pk=user.id)
                        if not item.is_active:
                            return Response({
                                "status": "failure",
                                "message": "Your account is not activated."
                                }, status=status.HTTP_401_UNAUTHORIZED)
                        return Response({
                            'token': token,
                            'data': UserSerializer(item).data
                        }, status=status.HTTP_200_OK)
                    else:
                        return Response({"message": "Incorrect credentials"}, status=status.HTTP_404_NOT_FOUND)
                except User.DoesNotExist:
                    return Response({"status": "failure", "message": "This account does not exist. Please register"}, status=400)
            return Response({"message": "Password required"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({"message": "Email required"}, status=status.HTTP_401_UNAUTHORIZED)


class UserDetailAPIView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get(self, request, slug, format=None):
        try:
            item = User.objects.get(slug=slug)
            serializer = UserSerializer(item)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class ProductAPIView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get(self, request, slug, format=None):
        try:
            item = Product.objects.get(slug=slug)
            serializer = ProductSerializer(item)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, slug, format=None):
        try:
            item = Product.objects.get(slug=slug)
        except Product.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = ProductSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slug, format=None):
        try:
            item = Product.objects.get(slug=slug)
        except Product.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductAPIListView(generics.CreateAPIView):
    permission_classes = ()
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get(self, request, format=None):
        items = Product.objects.order_by('-pk')
        return Response(ProductSerializer(items, many=True).data)         

    def post(self, request, format=None):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)