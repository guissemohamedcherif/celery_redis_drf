from http.client import HTTPResponse
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from api.serializers import *
from api.models import *
from rest_framework import generics
from django.db.models import Q,OuterRef,Subquery
from easy_password_generator import PassGen
from api.notifications import Notif as notify
from backend import settings
from django.utils import timezone
from django.contrib.auth import authenticate
from django.template.loader import render_to_string
from rest_framework_tracking.mixins import LoggingMixin
from rest_framework_jwt.settings import api_settings
from dateutil.relativedelta import relativedelta
from django.shortcuts import redirect, render
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from api.utils import REGEX, Utils as my_utils
from safedelete.models import HARD_DELETE
from backend.settings import API_URL, API_KEY,APP_NAME
from icecream import ic
import json
from ast import literal_eval
import hashlib
from api.pagination import KgPagination
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, Http404
from rest_framework import status
import locale,re
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from backend.settings import APP_NAME
from api.order import add_to_cart
from api.images import get_images
from functools import reduce
from operator import or_,and_

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

class TranslatedErrorResponse(Response):
    def __init__(self, serializer_errors, status=None, template_name=None, headers=None, content_type=None):
        translated_errors = Utils.translate_errors_array(serializer_errors)
        super().__init__(translated_errors, status=status, template_name=template_name, headers=headers, content_type=content_type)


class UserRegisterAPIView(LoggingMixin, generics.CreateAPIView):
    permission_classes = ()
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer

    REGEX_PATTERN = REGEX

    def do_after(self, item):
        """
        Perform actions after user registration.
        """
        contenu = f"Félicitations! Votre compte {item.user_type.upper()} sur {APP_NAME} vient d’être créé ! 🎉🎉"
        subject = f"Bienvenu(e)🎉 sur  {APP_NAME}"
        to = item.email
        template_src = 'mail_notification.html'
        context = {
            'user_type': item.user_type.upper(),
            'email': item.email,
            "nom":item.nom,
            "prenom":item.prenom,
            'settings': settings,
            "id":"false",
            "contenu":contenu,
            "year":timezone.now().year
        }
        notify.send_email(subject, to, template_src, context)

    def post(self, request, *args, **kwargs):
        """
        Handle POST request for user registration.
        """
        pattern = re.compile(self.REGEX_PATTERN)
        if ('password' in request.data and request.data['password']
           and not pattern.match(request.data['password'])):
            return Response({ "message": "Le mot de passe doit avoir au moins au minimum 8 caractères,1 caractère en majuscule, 1 caractère en minuscule, 1 nombre et 1 caractère spéciale"
                    }, status=400)
        
        email = request.data.get("email")
        if User.objects.filter(email=email).first():
            return Response({"message":"Cet utilisateur existe déja dans la base de donnée"},status=400)
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            item = serializer.save()
            response = Response(UserGetSerializer(item).data, status=201)
            response._resource_closers.append(self.do_after(item))
            return response
        return TranslatedErrorResponse(serializer.errors, status=400)


class LoginView(LoggingMixin, generics.CreateAPIView):    
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
                        if item.bloquer == True:
                            return Response({"message": f"Votre compte a été bloqué. Pour plus d'informations, veuillez contacter l'équipe de {APP_NAME}."}, status=400)
                        if item and item.email != email:
                            email = item.email
                            request.data['email'] = email
                    
                    user = authenticate(request, email=email, password=request.data['password'])
                    if user:
                        token = jwt_encode_handler(jwt_payload_handler(user))
                        item = User.objects.get(pk=user.id)
                        if item.user_type == DELETED:
                            return Response({"message": f"Votre compte a été supprimé. Pour plus d'informations, veuillez contacter l'équipe de {APP_NAME}."}, status=400)
                        if item.is_archive:
                            return Response({"message": f"Votre compte a été archivé. Pour plus d'informations, veuillez contacter l'équipe de {APP_NAME}."}, status=400)
                        if not item.is_active:
                            return Response({
                                "status": "failure",
                                "message": "Ton compte n'a pas encore activé par l'admin."},
                                status=401)
                        return Response({
                            'token': token,
                            'data': UserSerializer(item).data
                        }, status=200)
                    else:
                        return Response({"message": "Vos identifiants sont incorrects"}, status=400)
                except User.DoesNotExist:
                    return Response({"status": "failure", "message": "Ce compte n'existe pas. Veuillez-vous enregistrer"}, status=400)
            return Response({"message": "Votre mot de passe est requis"}, status=401)
        return Response({"message": "Votre email est requis"}, status=401)


class UserDeletedAPIListView(LoggingMixin, generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserGetSerializer

    def get(self, request, format=None):
        if (request.user.user_type == ADMIN or request.user.is_superuser or request.user.user_type == SUPERADMIN):
            items = User.objects.filter(user_type=DELETED).order_by('-pk')
            limit = self.request.query_params.get('limit')
            word = self.request.query_params.get('q')
            if word:
                items = items.filter(Q(prenom__icontains=word) | Q(nom__icontains=word))
            return KgPagination.get_response(limit,items,request,UserGetSerializer)
        return Response({"message": "Unauthorized action"}, status=403)

class UserAPIListView(LoggingMixin, generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserGetSerializer

    def get(self, request, format=None):
        if (request.user.user_type == ADMIN or request.user.is_superuser or request.user.user_type == SUPERADMIN):
            items = User.objects.exclude(Q(user_type=DELETED) | Q(user_type=SUPERADMIN)).order_by('-pk')
            limit = self.request.query_params.get('limit')
            word = self.request.query_params.get('q')
            if word:
                items = items.filter(Q(prenom__icontains=word)| Q(nom__icontains=word) ) 
            return KgPagination.get_response(limit,items,request,UserGetSerializer)
        return Response({"message": "Unauthorized action"}, status=403)

class UserAPIView(LoggingMixin, generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get(self, request, slug, format=None):
        try:
            item = User.objects.get(slug=slug)
            if (request.user.id == item.id or request.user.is_superuser or
               request.user.user_type == ADMIN):
                serializer = UserGetSerializer(item)
                if item.user_type == ADMIN:
                    admin = AdminUser.objects.get(pk=item)
                    serializer = AdminUserGetSerializer(admin)
                return Response(serializer.data)
            else:
                return Response({"message": "Accès interdit"}, status=401)
        except User.DoesNotExist:
            return Response(status=404)

    def put(self, request, slug, format=None):
        try:
            item = User.objects.get(slug=slug)
            if (request.user.id == item.id or request.user.is_superuser
               or request.user.user_type == ADMIN):
                self.data = request.data.copy()
                if 'password' in request.data:
                    item.set_password(request.data['password'])
                    self.data['password'] = item.password
                serializer = UserSerializer(item, data=self.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    item.save()
                    return Response(UserGetSerializer(item).data)
                return TranslatedErrorResponse(serializer.errors, status=400)
            return Response({"message": "Accès interdit"}, status=401)
        except User.DoesNotExist:
            return Response(status=404)

    def delete(self, request, slug, format=None):
        try:
            item = User.objects.get(slug=slug)
            if request.user.is_superuser or request.user.user_type == ADMIN:
                self.handle_user_deletion(item)
                # item.delete(force_policy=HARD_DELETE)
                return Response(status=204)
            return Response({"message": "Accès interdit"}, status=401)
        except User.DoesNotExist:
            return Response(status=404)
    
    def handle_user_deletion(self, item):
        randomstring = my_utils.random_string_generator(12,"userdeletion")
        email = item.email
        user_type = item.user_type
        item.email = f"{randomstring}{item.email}"
        item.deletion_id = email
        item.user_type = DELETED
        item.deletion_type = user_type
        item.save()

class UserDetailAPIView(LoggingMixin, generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get(self, request, slug, format=None):
        try:
            item = User.objects.get(slug=slug)
            serializer = UserGetSerializer(item)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(status=404)

class UserReactivationAPIView(LoggingMixin, generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SuppressionCompteSerializer

    def get(self, request,email, format=None):
        try:
            item = User.objects.get(email=email)  
            if  not User.objects.filter(email=item.deletion_id).exists():        
                item.email = item.deletion_id
                item.deletion_id = email
                item.user_type = item.deletion_type
                item.is_active = True
                item.is_archive = False
                item.save()
                subject = "COMPTE RÉACTIVÉ", 
                to = item.email
                template_src = 'mail_notification_user.html',
                contexte= {
                       'item': item,
                         'settings':settings
                }
                notify.send_email(subject, to,template_src , contexte)
                return Response({"status": "success", "message": "user successfully reactived "},status=200)
            return  Response({"message":"Un autre compte avec cet email existe déja.Voulez-vous changer le modifier. "},status=400)
        except User.DoesNotExist:
            return  Response({"message":"Un autre compte associé à cet email existe déja.Voulez-vous changer le modifier. "},status=400)  
    
    def put(self, request, email, format=None):
        try:
            item = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(status=404)
        if "email" in request.data and request.data["email"]:
            if email != request.data["email"] and not User.objects.filter(email=request.data["email"]).exists():
                serializer = UserSerializer(item, data=request.data,partial=True)
                if serializer.is_valid():
                    item.user_type = item.deletion_type
                    item.is_active = True
                    item.is_archive = False
                    item.save()
                    subject, to = "COMPTE RÉACTIVÉ", item.email
                    notify.send_email(subject, to, 'mail_reactivation_user.html',{'item': item, 'settings':settings})
                    serializer.save()
                    return Response(serializer.data)
                return TranslatedErrorResponse(serializer.errors, status=400)
            return Response({"message":"Un autre compte à associé cet email existe déja"},status=400)
        return Response({"message":"L'email est obligatoire"},status=400)

class AccountActivationAPIView(LoggingMixin, generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = AccountActivationSerializer

    def get(self, request, slug, format=None):
        try:
            item = AccountActivation.objects.get(slug=slug)
            serializer = AccountActivationSerializer(item)
            return Response(serializer.data)
        except AccountActivation.DoesNotExist:
            return Response(status=404)

    def put(self, request, slug, format=None):
        try:
            item = AccountActivation.objects.get(slug=slug)
        except AccountActivation.DoesNotExist:
            return Response(status=404)
        serializer = AccountActivationSerializer(item, data=request.data,
                                                 partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return TranslatedErrorResponse(serializer.errors, status=400)

    def delete(self, request, slug, format=None):
        try:
            item = AccountActivation.objects.get(slug=slug)
        except AccountActivation.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)

class AccountActivationAPIListView(LoggingMixin, generics.CreateAPIView):
    queryset = AccountActivation.objects.all()
    serializer_class = AccountActivationSerializer

    def get(self, request, format=None):
        items = AccountActivation.objects.order_by('-pk')
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(items, request)
        serializer = AccountActivationSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, format=None):
        serializer = AccountActivationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return TranslatedErrorResponse(serializer.errors, status=400)

class PasswordResetAPIView(LoggingMixin, generics.CreateAPIView):
    queryset = AccountActivation.objects.all()
    serializer_class = AccountActivationSerializer

    def get(self, request, slug, format=None):
        try:
            item = PasswordReset.objects.get(slug=slug)
            serializer = PasswordResetSerializer(item)
            return Response(serializer.data)
        except PasswordReset.DoesNotExist:
            return Response(status=404)

    def put(self, request, slug, format=None):
        try:
            item = PasswordReset.objects.get(slug=slug)
        except PasswordReset.DoesNotExist:
            return Response(status=404)
        serializer = PasswordResetSerializer(item, data=request.data,
                                             partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return TranslatedErrorResponse(serializer.errors, status=400)

    def delete(self, request, slug, format=None):
        try:
            item = PasswordReset.objects.get(slug=slug)
        except PasswordReset.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)

class PasswordResetAPIListView(LoggingMixin, generics.CreateAPIView):
    queryset = AccountActivation.objects.all()
    serializer_class = AccountActivationSerializer

    def get(self, request, format=None):
        items = PasswordReset.objects.order_by('-pk')
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(items, request)
        serializer = PasswordResetSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, format=None):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return TranslatedErrorResponse(serializer.errors, status=400)


class VendeurRegisterAPIView(LoggingMixin, generics.CreateAPIView):
    permission_classes = ()
    queryset = User.objects.all()
    serializer_class = VendeurRegisterSerializer

    REGEX_PATTERN = REGEX

    def do_after(self, item):
        """
        Perform actions after user registration.
        """
        contenu = f"Félicitations! Votre compte {item.user_type.upper()} sur {APP_NAME} vient d’être créé ! 🎉🎉"
        subject = f"Bienvenu(e)🎉 sur  {APP_NAME}"
        to = item.email
        template_src = 'mail_notification.html'
        name = item.prenom if item.prenom else ""
        name = name + " " + item.nom if item.nom else name
        context = {
            'user_type': item.user_type.upper(),
            'email': item.email,
            "name":name,
            'settings': settings,
            "id":"false",
            "contenu":contenu,
            "year":timezone.now().year
        }
        notify.send_email(subject, to, template_src, context)

    def post(self, request, *args, **kwargs):
        """
        Handle POST request for user registration.
        """
        pattern = re.compile(self.REGEX_PATTERN)
        if ('password' in request.data and request.data['password']
           and not pattern.match(request.data['password'])):
            return Response({ "message": "Le mot de passe doit avoir au moins au minimum 8 caractères,1 caractère en majuscule, 1 caractère en minuscule, 1 nombre et 1 caractère spéciale"
                    }, status=400)
        
        email = request.data.get("email")
        if User.objects.filter(email=email).first():
            return Response({"message":"Cet utilisateur existe déja dans la base de donnée"},status=400)
        serializer = VendeurRegisterSerializer(data=request.data)
        if serializer.is_valid():
            item = serializer.save()
            response = Response(UserGetSerializer(item).data, status=201)
            response._resource_closers.append(self.do_after(item))
            return response
        return TranslatedErrorResponse(serializer.errors, status=400)


class VisiteurRegisterAPIView(LoggingMixin, generics.CreateAPIView):
    permission_classes = ()
    queryset = User.objects.all()
    serializer_class = VisiteurRegisterSerializer

    REGEX_PATTERN = REGEX

    def do_after(self, item):
        """
        Perform actions after user registration.
        """
        contenu = f"Félicitations! Votre compte {item.user_type.upper()} sur {APP_NAME} vient d’être créé ! 🎉🎉"
        subject = f"Bienvenu(e)🎉 sur  {APP_NAME}"
        to = item.email
        template_src = 'mail_notification.html'
        name = item.prenom if item.prenom else ""
        name = name + " " + item.nom if item.nom else name
        context = {
            'user_type': item.user_type.upper(),
            'email': item.email,
            "name":name,
            'settings': settings,
            "id":"false",
            "contenu":contenu,
            "year":timezone.now().year
        }
        notify.send_email(subject, to, template_src, context)

    def post(self, request, *args, **kwargs):
        """
        Handle POST request for user registration.
        """
        pattern = re.compile(self.REGEX_PATTERN)
        if ('password' in request.data and request.data['password']
           and not pattern.match(request.data['password'])):
            return Response({ "message": "Le mot de passe doit avoir au moins au minimum 8 caractères,1 caractère en majuscule, 1 caractère en minuscule, 1 nombre et 1 caractère spéciale"
                    }, status=400)
        
        email = request.data.get("email")
        if User.objects.filter(email=email).first():
            return Response({"message":"Cet utilisateur existe déja dans la base de donnée"},status=400)
        serializer = VisiteurRegisterSerializer(data=request.data)
        if serializer.is_valid():
            item = serializer.save()
            response = Response(UserGetSerializer(item).data, status=201)
            response._resource_closers.append(self.do_after(item))
            return response
        return TranslatedErrorResponse(serializer.errors, status=400)


class VisiteurCreateAPIView(LoggingMixin, generics.CreateAPIView):
    permission_classes = ()
    queryset = User.objects.all()
    serializer_class = VisiteurRegisterSerializer

    REGEX_PATTERN = REGEX

    def do_after(self, item, password):
        """
        Perform actions after user registration.
        """
        contenu = f"Félicitations! Votre compte {item.user_type.upper()} sur {APP_NAME} vient d’être créé ! 🎉🎉"
        subject = f"Bienvenu(e)🎉 sur  {APP_NAME}"
        to = item.email
        template_src = 'mail_notification.html'
        name = item.prenom if item.prenom else ""
        name = name + " " + item.nom if item.nom else name
        context = {
            'user_type': item.user_type.upper(),
            'email': item.email,
            "name":name,
            'settings': settings,
            "password": password,
            "id":"true",
            "contenu":contenu,
            "year":timezone.now().year
        }
        notify.send_email(subject, to, template_src, context)

    def post(self, request, *args, **kwargs):
        """
        Handle POST request for user registration.
        """
        pattern = re.compile(self.REGEX_PATTERN)
        self.data = request.data.copy()
        pwo = PassGen(minlen=8, minuc=1, minlc=1, minnum=1, minsc=1)
        password = pwo.generate()
        self.data['password'] = password
        
        email = request.data.get("email")
        if User.objects.filter(email=email).first():
            return Response({"message":"Cet utilisateur existe déja dans la base de donnée"},status=400)
        serializer = VisiteurRegisterSerializer(data=self.data)
        if serializer.is_valid():
            item = serializer.save()
            response = Response(UserGetSerializer(item).data, status=201)
            response._resource_closers.append(self.do_after(item, password))
            return response
        return TranslatedErrorResponse(serializer.errors, status=400)


class VendeurAPIListView(LoggingMixin, generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get(self, request, format=None):
        items = User.objects.filter(user_type=VENDEUR).order_by('-pk')
        limit = self.request.query_params.get('limit')
        search = self.request.query_params.get('q')
        if search:
            search_terms = search.split()
            nom_conditions = [Q(Q(nom__icontains=term)|Q(prenom__icontains=term)) for term in search_terms]
            phone_conditions = [Q(phone__icontains=term) for term in search_terms]
            email_conditions = [Q(email__icontains=term) for term in search_terms]
            nom_filter = reduce(and_, nom_conditions)
            phone_filter = reduce(and_, phone_conditions)
            email_filter = reduce(and_, email_conditions)
            items = items.filter(
                nom_filter |
                phone_filter |
                email_filter 
            )
        return KgPagination.get_response(limit,items,request,UserGetSerializer)


class VendeurBlockedAPIListView(LoggingMixin, generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get(self, request, format=None):
        items = User.objects.filter(user_type=VENDEUR, bloquer=True)
        limit = self.request.query_params.get('limit')
        return KgPagination.get_response(limit,items,request,UserGetSerializer)


class VendeurBlockedMobileAPIListView(LoggingMixin, generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get(self, request, format=None):
        items = User.objects.filter(user_type=VENDEUR, bloquer=True)
        return Response(UserGetSerializer(items, many=True).data)


class VendeurMobileAPIListView(LoggingMixin, generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get(self, request, format=None):
        items = User.objects.filter(user_type=VENDEUR, bloquer=False)
        return Response(UserGetSerializer(items, many=True).data)


class VisiteurMobileAPIListView(LoggingMixin, generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get(self, request, format=None):
        items = User.objects.filter(user_type=USER, bloquer=False)
        return Response(UserGetSerializer(items, many=True).data)


class VisiteurAPIListView(LoggingMixin, generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get(self, request, format=None):
        items = User.objects.filter(user_type=USER).order_by('-pk')  
        limit = self.request.query_params.get('limit')
        search = self.request.query_params.get('q')
        if search:
            search_terms = search.split()
            nom_conditions = [Q(Q(nom__icontains=term)|Q(prenom__icontains=term)) for term in search_terms]
            phone_conditions = [Q(phone__icontains=term) for term in search_terms]
            email_conditions = [Q(email__icontains=term) for term in search_terms]
            nom_filter = reduce(and_, nom_conditions)
            phone_filter = reduce(and_, phone_conditions)
            email_filter = reduce(and_, email_conditions)
            items = items.filter(
                nom_filter |
                phone_filter |
                email_filter 
            )
        return KgPagination.get_response(limit,items,request,UserGetSerializer)


class VisiteurBlockedAPIListView(LoggingMixin, generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get(self, request, format=None):
        items = User.objects.filter(user_type=USER, bloquer=True)
        limit = self.request.query_params.get('limit')
        return KgPagination.get_response(limit,items,request,UserGetSerializer)


class VisiteurBlockedMobileAPIListView(LoggingMixin, generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get(self, request, format=None):
        items = User.objects.filter(user_type=USER, bloquer=True)
        return Response(UserGetSerializer(items, many=True).data)


class BlockUserAPIView(LoggingMixin, generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = BlockUserSerializer
    
    def do_after(self, item, causes):
        """
        Perform actions after user registration.
        """
        contenu = f"Votre compte {item.user_type.upper()} sur {APP_NAME} vient d’être bloqué. \n"
        if causes != "":
           contenu = contenu + f"CAUSES: {causes}" 
        subject = f"Compte bloqué sur  {APP_NAME}"
        to = item.email
        template_src = 'mail_notification.html'
        name = item.prenom if item.prenom else ""
        name = name + " " + item.nom if item.nom else name
        context = {
            'user_type': item.user_type.upper(),
            'email': item.email,
            "name":name,
            'settings': settings,
            "id":"false",
            "contenu":contenu,
            "year":timezone.now().year
        }
        notify.send_email(subject, to, template_src, context)

    def get(self, request, slug, format=None):
        try:
            item = User.objects.get(slug=slug)
            causes = request.GET.get('causes')
            if not causes:
                causes = ""
            item.is_active = False
            item.bloquer = True
            item.save()
            serializer = UserGetSerializer(item)
            response = Response({
                "message": "Utilisateur bloqué avec succés.",
                "data": serializer.data
                })
            response._resource_closers.append(self.do_after(item, causes))
            return response
        except User.DoesNotExist:
            return Response(status=404)


class UnBlockUserAPIView(LoggingMixin, generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def do_after(self, item):
        """
        Perform actions after user registration.
        """
        contenu = f"Votre compte {item.user_type.upper()} sur {APP_NAME} vient d’être bloqué."
        subject = f"Compte débloqué sur  {APP_NAME}"
        to = item.email
        template_src = 'mail_notification.html'
        name = item.prenom if item.prenom else ""
        name = name + " " + item.nom if item.nom else name
        context = {
            'user_type': item.user_type.upper(),
            'email': item.email,
            "name":name,
            'settings': settings,
            "id":"false",
            "contenu":contenu,
            "year":timezone.now().year
        }
        notify.send_email(subject, to, template_src, context)

    def get(self, request, slug, format=None):
        try:
            item = User.objects.get(slug=slug)
            item.is_active = True
            item.bloquer = False
            item.save()
            serializer = UserGetSerializer(item)
            response = Response({
                "message": "Utilisateur débloqué avec succés.",
                "data": serializer.data
                })
            response._resource_closers.append(self.do_after(item))
            return response
        except User.DoesNotExist:
            return Response(status=404)


class VendeurCreateAPIView(LoggingMixin, generics.CreateAPIView):
    permission_classes = ()
    queryset = User.objects.all()
    serializer_class = VendeurRegisterSerializer

    REGEX_PATTERN = REGEX

    def do_after(self, item, password):
        """
        Perform actions after user registration.
        """
        contenu = f"Félicitations! Votre compte {item.user_type.upper()} sur {APP_NAME} vient d’être créé ! 🎉🎉"
        subject = f"Bienvenu(e)🎉 sur  {APP_NAME}"
        to = item.email
        template_src = 'mail_notification.html'
        name = item.prenom if item.prenom else ""
        name = name + " " + item.nom if item.nom else name
        context = {
            'user_type': item.user_type.upper(),
            'email': item.email,
            "name":name,
            'settings': settings,
            "password": password,
            "id":"true",
            "contenu":contenu,
            "year":timezone.now().year
        }
        notify.send_email(subject, to, template_src, context)

    def post(self, request, *args, **kwargs):
        """
        Handle POST request for user registration.
        """
        pattern = re.compile(self.REGEX_PATTERN)
        self.data = request.data.copy()
        pwo = PassGen(minlen=8, minuc=1, minlc=1, minnum=1, minsc=1)
        password = pwo.generate()
        self.data['password'] = password
        
        email = request.data.get("email")
        if User.objects.filter(email=email).first():
            return Response({"message":"Cet utilisateur existe déja dans la base de donnée"},status=400)
        serializer = VendeurRegisterSerializer(data=self.data)
        if serializer.is_valid():
            item = serializer.save()
            response = Response(UserGetSerializer(item).data, status=201)
            response._resource_closers.append(self.do_after(item, password))
            return response
        return TranslatedErrorResponse(serializer.errors, status=400)


class AccountActivationUserView(LoggingMixin, generics.CreateAPIView):
    permission_classes = (
    )
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        if 'code' not in kwargs or kwargs['code'] is None:
            return Response(status=404)
        code = kwargs['code']
        try:
            activation = AccountActivation.objects.get(code=code,used=False)
            user = activation.user
            user.is_active = True
            user.save()

            activation.used = True
            activation.date_used = timezone.now()
            activation.save()
        except Exception:
            return Response(status=404)
        html = render_to_string('compte_user_active.html')
        return HTTPResponse(html)

class PasswordResetView(generics.CreateAPIView):
    permission_classes = (
    )
    """ use postman to test give 4 fields new_password  new_password_confirm \
        email code post methode"""
    queryset = PasswordReset.objects.all()
    serializer_class = PasswordResetSerializer

# envoie de mail de succés de modification de mot de passe
    def do_after(self, item):
        """
        Perform actions after user registration.
        """
        contenu = f"Nous sommes heureux de vous informer que votre demande de changement de mot de passe a été traitée avec succès. Votre compte est désormais sécurisé."
        subject = "Changement de mot de passe réussi 🤩🤩"
        to = item.email 
        template_src = 'mail_notification.html'
        context = {
            
            'email': item.email,
            "nom":item.nom,
            "prenom":item.prenom,
            'settings': settings,
            "id":"false",
            "contenu":contenu,
            "year":timezone.now().year
        }
        notify.send_email(subject, to, template_src, context)

    def post(self, request, *args, **kwargs):

        if request.data.get('code') is None:
            return Response({"message": "Veuillez entrez votre code"}, status=400)
        if request.data.get('email') is None:
            return Response({"message": "Veuillez entrez votre email"}, status=400)
        if (request.data.get('new_password') is None or
           request.data.get('new_password_confirm') is None) or (
           request.data.get('new_password') != request.data.get('new_password_confirm')
           ):
            return Response({
                "message": "Les mots de passe correspondent pas"}, status=400)
        try:
            user_ = get_object_or_404(User, email=request.data.get('email'))
            code_ = request.data.get('code')
            passReset = PasswordReset.objects.filter(user=user_, code=code_,
                                                     used=False).order_by(
                                                    '-date_created').first()
            if passReset is None:
                return Response({
                    "message": "Code invalide. Veuillez entrer un code valide."
                    }, status=400)
            user_.set_password(request.data.get('new_password'))
            user_.save()
            passReset.used = True
            passReset.date_used = timezone.now()
            passReset.save()
            response = Response(UserGetSerializer(user_).data, status=200)
            response._resource_closers.append(self.do_after(user_))
            return response
        except Http404:
            return Response({ "message": "L'utilisateur avec cet email n'existe pas"},status=400) 
    

class PasswordResetRequestView(LoggingMixin, generics.CreateAPIView):
    """ use postman to test give field email post methode"""
    permission_classes = (

    )
    queryset = User.objects.all()
    serializer_class = RequestPasswordSerializer

    # fonction qui envoie le mail de reinitialisation de mot de passe
    def do_after(self, item, code):

        """
        Perform actions after user registration.
        """
        contenu = f"Avez-vous oublié votre mot de passe ? Pas de panique! Vous pouvez le réinitialiser en utilisant le code suivant: {code} et en indiquant votre nouveau mot de passe."
        subject = "MOT DE PASSE OUBLIÉ 🧐"
        to = item.email 
        template_src = 'mail_notification.html'
        context = {
            
            'code': code,
            "nom":item.nom,
            "prenom":item.prenom,
            "contenu":contenu,
            "id":"false",
            "sujet":subject,
            "year":timezone.now().year
        }
        notify.send_email(subject, to, template_src, context)

    def post(self, request, *args, **kwargs):
        try:
            user_ = get_object_or_404(User, email=request.data.get('email'))
            code_ = my_utils.get_code()
            PasswordReset.objects.create(user=user_, code=code_)
            response = Response(UserGetSerializer(user_).data, status=200)
            response._resource_closers.append(self.do_after(user_, code_))
            return response 
        except Http404:
            return Response({ "message": "L'utilisateur avec cet email n'existe pas"},status=400)

class ChangePasswordView(LoggingMixin, generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    model = User

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=400)
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.password_reset_count = 1
            self.object.save()
            return Response(status=200)
        return TranslatedErrorResponse(serializer.errors, status=400)

class UserRetrieveView(LoggingMixin, generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        user = User.objects.get(email=request.user.email)
        if not user:
            return Response({
                "status": "failure",
                "message": "no such item",
            }, status=400)
        serializer = UserGetSerializer(user)
        return Response(serializer.data)
    

class SuppressionAPIListView(LoggingMixin, generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SuppressionCompteSerializer

    def post(self, request, format=None):
        if 'password' in request.data and request.data['password']:
            item = User.objects.get(pk=request.user.id)
            password = request.data['password']
            user = authenticate(request, email=item.email, password=password)
            if user:
                email = item.email
                user_type=item.user_type
                nom = item.prenom
                prenom = item.nom
                randomstring = my_utils.random_string_generator(
                    12, "userdeletion")
                item.email = randomstring+""+item.email
                item.deletion_id = email
                item.deletion_type = user_type
                item.user_type = DELETED
                item.is_active = False
                item.is_archive = True
                item.save()
                subject, to = "SUPPRESSION DE VOTRE COMPTE", email
                notify.send_email(subject, to, 'mail_suppression_user.html',
                                  {'nom': nom, 'prenom': prenom})
                return Response({"status": "success",
                                 "message": "user successfully deleted "},
                                status=200)
            return Response({"Le mot de passe est incorrect."}, status=400)
        return Response(
            {"Le mot de passe est requis pour supprimer votre compte"},
            status=401)

class SuppressionCompteByAdminAPIView(LoggingMixin, generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SuppressionCompteSerializer
    
    def post(self, request, slug, format=None):
        if 'password' in request.data and request.data['password']:
            admin = User.objects.get(pk=request.user.id)
            password = request.data['password']
            user = authenticate(request, email=admin.email, password=password)
            if user:
                try:
                    item = User.objects.get(slug=slug)
                    email = item.email
                    user_type=item.user_type
                    nom = item.prenom
                    prenom = item.nom
                    randomstring = my_utils.random_string_generator(
                        12, "userdeletion")
                    item.email = randomstring+""+item.email
                    item.deletion_id = email
                    item.deletion_type = user_type
                    item.user_type = DELETED
                    item.is_active = False
                    item.is_archive = True
                    item.save()
                    subject, to = "SUPPRESSION DE COMPTE", email
                    notify.send_email(
                        subject, to,
                        'mail_suppression_user.html',
                        {'nom': nom, 'prenom': prenom})
                    return Response({"status": "success",
                                     "message": "user successfully deleted "},
                                    status=200)
                except User.DoesNotExist:
                    return Response(status=404)
            return Response({"Le mot de passe est incorrect."}, status=400) 
        return Response(
            {"Le mot de passe est requis pour la suppression d'un compte"},
            status=401)

class AdminRetrieveView(LoggingMixin, generics.RetrieveAPIView):
    queryset = AdminUser.objects.all()
    serializer_class = AdminUserSerializer

    def get(self, request, *args, **kwargs):
        if (request.user.user_type == ADMIN
           or request.user.user_type == SUPERADMIN
           or request.user.is_superuser):
            try:
                user = AdminUser.objects.get(email=request.user.email)
                return Response(AdminUserSerializer(user).data, status=200)
            except AdminUser.DoesNotExist:
                if request.user.is_superuser:
                    return Response(UserSerializer(request.user).data)
                return Response({"message": "Vous n'etes pas un admin"}, 403)
        else:
            return Response({"message": "Unauthorized action"}, status=403)

class AdminUserAPIListView(LoggingMixin, generics.CreateAPIView):
    queryset = AdminUser.objects.all()
    serializer_class = AdminUserSerializer

    def get(self, request, format=None):
        if (request.user.user_type == ADMIN or request.user.is_superuser or
           request.user.user_type == SUPERADMIN):
            items = User.objects.filter(user_type=ADMIN).order_by('-pk')
            limit = self.request.query_params.get('limit')
            search = self.request.query_params.get('q')
            if search:
                items = items.filter(Q(nom__icontains=search)
                                    |Q(prenom__icontains=search)
                                    |Q(email__icontains=search)
                                    |Q(telephone__icontains=search)
                                    )
            return KgPagination.get_response(limit,items,request,AdminUserSerializer)
        else:
            return Response({"message": "Unauthorized action"}, status=403)

    def post(self, request, format=None):
        if (request.user.user_type == ADMIN or request.user.is_superuser or
            request.user.user_type == SUPERADMIN):
            self.data = request.data.copy()
            pwo = PassGen(minlen=8, minuc=1, minlc=1, minnum=1, minsc=1)
            password = pwo.generate()
            self.data['parent'] = request.user.id
            self.data['password'] = password
            serializer = AdminUserSerializer(data=self.data)
            if serializer.is_valid():
                serializer.save()
                user = User.objects.get(id=serializer.data['id'])
                user_type = user.user_type.upper()
                contenu = f"Nous vous informons qu'un compte {user_type} vient juste d'être crée pour vous sur la plateforme {APP_NAME}."
                subject = f"Création d'un compte {user_type}"
                to = user.email
                template_src = 'mail_notification.html'
                context =  {
                    'password': password,
                    'settings': settings,
                    "nom": user.nom,
                    "prenom": user.prenom,
                    "contenu": contenu,
                    "email": user.email,
                    "password": password,
                    "id":"true",
                    "sujet":subject,
                    "year":timezone.now().year
                }
                notify.send_email(subject, to, template_src, context)
                return Response(serializer.data, status=201)
            return TranslatedErrorResponse(serializer.errors, status=400)
        else:
            return Response({"message": "Unauthorized action"}, status=403)

class AdminUserAPIView(LoggingMixin, generics.RetrieveAPIView):
    queryset = AdminUser.objects.all()
    serializer_class = AdminUserSerializer

    def get(self, request, slug, format=None):
        if (request.user.user_type == ADMIN or request.user.is_superuser or
           request.user.user_type == SUPERADMIN):
            try:
                item = AdminUser.objects.get(slug=slug)
                serializer = AdminUserSerializer(item)
                return Response(serializer.data)
            except AdminUser.DoesNotExist:
                return Response(status=404)
        else:
            return Response({"message": "Unauthorized action"}, status=403)

    def put(self, request, slug, format=None):
        try:
            item = AdminUser.objects.get(slug=slug)
        except AdminUser.DoesNotExist:
            return Response(status=404)
        serializer = AdminUserSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return TranslatedErrorResponse(serializer.errors, status=400)

    def delete(self, request, slug, format=None):
        try:
            item = AdminUser.objects.get(slug=slug)
        except AdminUser.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)


class ConditionAPIView(LoggingMixin, generics.CreateAPIView):
    queryset = Condition.objects.all()
    serializer_class = ConditionSerializer

    def get(self, request, slug, format=None):
        try:
            item = Condition.objects.get(slug=slug)
            serializer = ConditionSerializer(item)
            return Response(serializer.data)
        except Condition.DoesNotExist:
            return Response(status=404)

    def put(self, request, slug, format=None):
        try:
            item = Condition.objects.get(slug=slug)
        except Condition.DoesNotExist:
            return Response(status=404)
        serializer = ConditionSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return TranslatedErrorResponse(serializer.errors, status=400)

    def delete(self, request, slug, format=None):
        try:
            item = Condition.objects.get(slug=slug)
        except Condition.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)

class ConditionAPIListView(LoggingMixin, generics.CreateAPIView):
    queryset = Condition.objects.all()
    serializer_class = ConditionSerializer

    def get(self, request, format=None):
        items = Condition.objects.order_by('-pk')
        limit = self.request.query_params.get('limit')
        return KgPagination.get_response(limit,items,request,ConditionSerializer)

    def post(self, request, format=None):
        serializer = ConditionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return TranslatedErrorResponse(serializer.errors, status=400)
    

class CGUAPIListView(LoggingMixin, generics.RetrieveAPIView):
    permission_classes =(

    )
    queryset = Condition.objects.all()
    serializer_class = ConditionSerializer

    def get(self, request, format=None):
        items = Condition.objects.filter(type=CGU)
        serializer = ConditionSerializer(items,many=True)
        return Response(serializer.data)
    

class ThemeAPIView(LoggingMixin, generics.CreateAPIView):
    queryset = Theme.objects.all()
    serializer_class = ThemeSerializer

    def get(self, request, slug, format=None):
        try:
            item = Theme.objects.get(slug=slug)
            serializer = ThemeSerializer(item)
            return Response(serializer.data)
        except Theme.DoesNotExist:
            return Response(status=404)

    def put(self, request, slug, format=None):
        try:
            item = Theme.objects.get(slug=slug)
        except Theme.DoesNotExist:
            return Response(status=404)
        serializer = ThemeSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return TranslatedErrorResponse(serializer.errors, status=400)

    def delete(self, request, slug, format=None):
        try:
            item = Theme.objects.get(slug=slug)
        except Theme.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)

class ThemeAPIListView(LoggingMixin, generics.CreateAPIView):
    queryset = Theme.objects.all()
    serializer_class = ThemeSerializer

    def get(self, request, format=None):
        items = Theme.objects.order_by('-pk')
        limit = self.request.query_params.get('limit')
        return KgPagination.get_response(limit,items,request,ThemeSerializer)
    

    def post(self, request, format=None):
        serializer = ThemeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return TranslatedErrorResponse(serializer.errors, status=400)

class ThemeByVisitorAPIListView(generics.RetrieveAPIView):
    permission_classes = (

    )
    queryset = Theme.objects.all()
    serializer_class = ThemeSerializer

    def get(self, request, format=None):
        items = Theme.objects.order_by('-pk')
        serializer = ThemeSerializer(items, many=True)
        return Response(serializer.data)

class ForumAPIListView (generics.CreateAPIView):
    queryset = Forum.objects.all()
    serializer_class = ForumSerializer

    def get(self, request, format=None):
        items = Forum.objects.order_by('-pk')
        limit = self.request.query_params.get('limit')
        search = self.request.query_params.get('q')
        if search:
            items = items.filter(Q(Theme__icontains=search)
                                 |Q(author__nom__icontains=search)
                                 |Q(author__prenom__icontains=search)
                                 |Q(content__icontains=search)
                                 )
        return KgPagination.get_response(limit,items,request,ForumGetSerializer)

    def post(self, request, format=None):
        serializer = ForumSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            item = Forum.objects.get(pk=serializer.data.get("id"))

            def notif_users():
                content = f"L'utilisateur {item.author.prenom} {item.author.nom} vient d'ajouter un nouveau sujet dans le Forum."
                data = ForumSerializer(item).data
                admins = User.objects.filter(user_type=ADMIN)
                users = User.objects.filter(~Q(user_type=ADMIN))

                # for user in users:
                #     #Notiffication in app
                #     notif = Notification.objects.create(
                #         content=content,
                #         data=data,
                #         notif_type=FORUM
                #     )
                #     notify.push_notif(to=user.token,body=content,data=data)

            response = Response(serializer.data, status=201)
            response._resource_closers.append(notif_users)
            return response
        return TranslatedErrorResponse(serializer.errors, status=400)



class ForumAPIView(generics.RetrieveAPIView):
    queryset = Forum.objects.all()
    serializer_class = ForumSerializer

    def get(self, request, slug, format=None):
        try:
            item = Forum.objects.get(slug=slug)
            item.view +=1
            item.save()
            serializer = ForumGetSerializer(item)
            return Response(serializer.data)
        except Forum.DoesNotExist:
            return Response(status=404)

    def put(self, request, slug, format=None):
        try:
            item = Forum.objects.get(slug=slug)
            self.data = request.data.copy()
            serializer = ForumSerializer(item, data=self.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return TranslatedErrorResponse(serializer.errors, status=400)
        except Forum.DoesNotExist:
            return Response(status=404)

    def delete(self, request, slug, format=None):
        try:
            item = Forum.objects.get(slug=slug)
            item.delete()
            return Response(status=204)
        except Forum.DoesNotExist:
            return Response(status=404)


class ForumByUserAPIListView(generics.RetrieveAPIView):
    queryset = Forum.objects.all()
    serializer_class = ForumSerializer

    def get(self, request, slug, format=None):
        items = Forum.objects.filter(author__slug=slug).order_by('-pk')
        limit = self.request.query_params.get('limit')
        return KgPagination.get_response(limit,items,request,ForumGetSerializer)


class ForumByVisitorAPIListView (generics.RetrieveAPIView):
    permission_classes = ()
    queryset = Forum.objects.all()
    serializer_class = ForumSerializer()

    def get(self, request, format=None):
        items = Forum.objects.order_by('-pk')
        limit = self.request.query_params.get('limit')
        return KgPagination.get_response(limit,items,request,ForumGetSerializer)



class ForumByVisitorAPIView(generics.RetrieveAPIView):
    permission_classes = (

    )
    queryset = Forum.objects.all()
    serializer_class = ForumSerializer

    def get(self, request, slug, format=None):
        try:
            item = Forum.objects.get(slug=slug)
            serializer = ForumGetSerializer(item)
            return Response(serializer.data)
        except Forum.DoesNotExist:
            return Response(status=404)


class CommentForumAPIListView (generics.CreateAPIView):
    queryset = CommentForum.objects.all()
    serializer_class = CommentForumSerializer

    def get(self, request, format=None):
        items = CommentForum.objects.order_by('-pk')
        limit = self.request.query_params.get('limit')
        return KgPagination.get_response(limit,items,request,CommentForumGetSerializer)


    def post(self, request, format=None):
        serializer = CommentForumSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return TranslatedErrorResponse(serializer.errors, status=400)


class CommentForumAPIView(generics.RetrieveAPIView):
    queryset = CommentForum.objects.all()
    serializer_class = CommentForumSerializer

    def get(self, request, slug, format=None):
        try:
            item = CommentForum.objects.get(slug=slug)
            serializer = CommentForumGetSerializer(item)
            return Response(serializer.data)
        except CommentForum.DoesNotExist:
            return Response(status=404)

    def put(self, request, slug, format=None):
        try:
            item = CommentForum.objects.get(slug=slug)
            self.data = request.data.copy()
            serializer = CommentForumSerializer(item, data=self.data,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return TranslatedErrorResponse(serializer.errors, status=400)
        except CommentForum.DoesNotExist:
            return Response(status=404)

    def delete(self, request, slug, format=None):
        try:
            item = CommentForum.objects.get(slug=slug)
            item.delete()
            return Response(status=204)
        except CommentForum.DoesNotExist:
            return Response(status=404)


class CommentForumByUserAPIListView(generics.RetrieveAPIView):
    queryset = CommentForum.objects.all()
    serializer_class = CommentForumSerializer

    def get(self, request, slug, format=None):
        items = CommentForum.objects.filter(created_by__slug=slug).order_by('-pk')
        limit = self.request.query_params.get('limit')
        return KgPagination.get_response(limit,items,request,CommentForumGetSerializer)


class CommentByForumAPIListView(generics.RetrieveAPIView):
    queryset = CommentForum.objects.all()
    serializer_class = CommentForumSerializer

    def get(self, request, slug, format=None):
        items = CommentForum.objects.filter(forum__slug=slug).order_by('-pk')
        limit = self.request.query_params.get('limit')
        search = self.request.query_params.get('q')
        if search:
            items = items.filter(Q(created_by__nom__icontains=search)
                                 |Q(created_by__prenom__icontains=search))
        return KgPagination.get_response(limit,items,request,CommentForumGetSerializer)


class SignalementAPIView(LoggingMixin, generics.CreateAPIView):
    queryset = Signalement.objects.all()
    serializer_class = SignalementSerializer

    def get(self, request, slug, format=None):
        try:
            item = Signalement.objects.get(slug=slug)
            serializer = SignalementSerializer(item)
            return Response(serializer.data)
        except Signalement.DoesNotExist:
            return Response(status=404)

    def put(self, request, slug, format=None):
        try:
            item = Signalement.objects.get(slug=slug)
        except Signalement.DoesNotExist:
            return Response(status=404)
        serializer = SignalementSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return TranslatedErrorResponse(serializer.errors, status=400)

    def delete(self, request, slug, format=None):
        try:
            item = Signalement.objects.get(slug=slug)
        except Signalement.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)


class SignalementAPIListView(LoggingMixin, generics.CreateAPIView):
    queryset = Signalement.objects.all()
    serializer_class = SignalementSerializer

    def get(self, request, format=None):
        items = Signalement.objects.order_by('-pk')
        search = request.GET.get('q')
        if search:
            items = items.filter(motif__icontains=search)
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(items, request)
        serializer = SignalementGetSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, format=None):
        serializer = SignalementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            item = Signalement.objects.get(pk=serializer.data.get("id"))
            contenu = f"Le {item.user.user_type} {item.user.prenom} {item.user.nom} vient d'être signalé par {item.author.nom} {item.author.prenom} pour la raison suivante: {item.motif}."
            def notification():
                #Notifié les admins
                subject ="Nouveau signalement"
                year = timezone.now().year
                admins = AdminUser.objects.filter(signalements=True)
                notify.notify_admins(
                    admins,
                    subject,
                    template='mail_notification.html',
                    context_dict = {
                        'item':item,
                        "settings":settings,
                        'item':item.user,
                        'contenu': contenu,
                        "year":timezone.now().year,
                        "sujet": subject,
                        "id":"false",
                        "nom":"administrateur"
                    }
                )
                for admin in admins:
                    #IN APP
                    notif = Notification.objects.create(
                        content=subject,
                        data=serializer.data,
                        receiver=admin
                    )
                    notif.save()
                
                #Notifier l'utilisateur signalé
                content = "Votre compte vient d'être signalé."
                data = UserGetSerializer(item.user).data
                #Notiffication in app
                notif = Notification.objects.create(
                    content=content,
                    data=data,
                    receiver=item.user
                )
                notif.save()
                #Push notifications
                notify.push_notif(to=item.user.token,body=content,data=data) 
            response = Response(serializer.data, status=201)
            response._resource_closers.append(notification)
            return response
        return TranslatedErrorResponse(serializer.errors, status=400)

    
class ContactAPIListView(LoggingMixin, generics.CreateAPIView):
    permission_classes = ()
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

    def get(self, request, format=None):
        items = Contact.objects.order_by('-pk')
        status = self.request.query_params.get('status')
        search = self.request.query_params.get('q')
        if status:
            items = items.filter(status=status)
        if search:
            items = items.filter(Q(user__nom__icontains=search)
                | Q(user__prenom__icontains=search)
                | Q(subject__icontains=search)
                | Q(name__icontains=search)
                )   
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(items, request)
        serializer = ContactGetSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)  
    def post(self, request, format=None):
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            def notif_admins():
                item = Contact.objects.get(id=serializer.data['id'])
                subject = (str(item.subject) if item.subject else "Message de contact")
                admins = User.objects.filter(Q(user_type=ADMIN)|Q(user_type=SUPERADMIN))
                email = item.user.email if item.user else item.email
                content = "vous venez de recevoir un nouveau message contact"
                notification = Notification(content=content, notif_type='message_contact',
                                            data=serializer.data)
                notification.save()
                notification.admins.set(admins)
                template_src = 'mail_notification.html'
                admins_emails = admins.values_list('email')
                context = {
                    #'admins_emails' : admins_email,
                    "user": email,
                    'contenu': content,
                    "message": item.message,
                    'sujet': subject,
                    'settings': settings,
                    "id":"false",
                    "sujet":subject,
                    "year":timezone.now().year 
                }
                notify.notify_admins(admins,subject,template_src,context)
            response = Response(serializer.data, status=201)
            response._resource_closers.append(notif_admins)
            return response
        return TranslatedErrorResponse(serializer.errors, status=400)


class ContactAPIView(LoggingMixin, generics.CreateAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

    def get(self, request, slug, format=None):
        try:
            item = Contact.objects.get(slug=slug)
            serializer = ContactSerializer(item)
            return Response(serializer.data)
        except Contact.DoesNotExist:
            return Response(status=404)

    def put(self, request, slug, format=None):
        try:
            item = Contact.objects.get(slug=slug)
        except Contact.DoesNotExist:
            return Response(status=404)
        serializer = ContactSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return TranslatedErrorResponse(serializer.errors, status=400)

    def delete(self, request, slug, format=None):
        try:
            item = Contact.objects.get(slug=slug)
        except Contact.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)


class ContactAddAPIListView(LoggingMixin, generics.CreateAPIView):
    permission_classes = ()
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

    def post(self, request, format=None):
        admins = User.objects.filter(user_type='admin')
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            contact = Contact.objects.get(pk=serializer.data.get("id"))
            message = contact.message.capitalize()
           # subject = "Accusé de réception",
            # template_src ="mail_notification.html",
            email = contact.user.email if contact.user else contact.email
            to= email,
            notify.send_email("Accusé de réception",email,to, "mail_notification.html",context= {
                "contact":contact,
                "settings":settings,
                "email":email,
                "message":message,
                "contact":contact,
                "id":"false",
                "sujet":subject,
                "year":timezone.now().year        
                })
            subject = str(contact.subject.upper()) if contact.subject else "Message de contact".upper()
            template_src = 'mail_notification.html'
            context_dict={"email":email,"message":message,"contact":contact,"sujet":subject, "settings":settings}
            response = Response(serializer.data, status=201)
            response._resource_closers.append(notify.notify_admins(admins,subject,template_src,context_dict))
            return response
        return TranslatedErrorResponse(serializer.errors, status=400) 


class ResponseContactAPIView(LoggingMixin, generics.CreateAPIView):
    queryset = ResponseContact.objects.all()
    serializer_class = ResponseContactSerializer

    def get(self, request, slug, format=None):
        try:
            item = ResponseContact.objects.get(slug=slug)
            serializer = ResponseContactSerializer(item)
            return Response(serializer.data)
        except ResponseContact.DoesNotExist:
            return Response(status=404)

    def put(self, request, slug, format=None):
        try:
            item = ResponseContact.objects.get(slug=slug)
        except ResponseContact.DoesNotExist:
            return Response(status=404)
        serializer = ResponseContactSerializer(item, data=request.data,
                                               partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return TranslatedErrorResponse(serializer.errors, status=400)

    def delete(self, request, slug, format=None):
        try:
            item = ResponseContact.objects.get(slug=slug)
        except ResponseContact.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)


class ResponseContactAPIListView(LoggingMixin, generics.CreateAPIView):
    queryset = ResponseContact.objects.all()
    serializer_class = ResponseContactSerializer

    def get(self, request, format=None):
        items = ResponseContact.objects.order_by('-pk')
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(items, request)
        serializer = ResponseContactGetSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, format=None):
        serializer = ResponseContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            contact = Contact.objects.get(id=request.data['message'])
            response = ResponseContact.objects.get(pk=serializer.data['id'])
            if contact.email:
                objet = "Réponse à votre message"
                subject= ''+objet,
                to =  contact.email, 
                response_message = BeautifulSoup(response.response, "html.parser").text
                message = BeautifulSoup(contact.message, "html.parser").text
                template_src='mail_notification.html',
                context_dict={'response':response_message,
                              'objet':objet,
                              'sujet': subject,
                              "contact":contact,
                              "message":message,      
                               'settings': settings,
                                "id":"false",
                                "sujet":subject,
                                 "year":timezone.now().year }
                notify.send_email(subject,to,template_src,context_dict)
            return Response(serializer.data, status=201)
        return TranslatedErrorResponse(serializer.errors, status=400)


class NotificationAPIView(LoggingMixin, generics.CreateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def get(self, request, slug, format=None):
        try:
            item = Notification.objects.get(slug=slug)
            serializer = NotificationGetSerializer(item)
            return Response(serializer.data)
        except Notification.DoesNotExist:
            return Response(status=404)

    def put(self, request, slug, format=None):
        try:
            item = Notification.objects.get(slug=slug)
        except Notification.DoesNotExist:
            return Response(status=404)
        serializer = NotificationSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return TranslatedErrorResponse(serializer.errors, status=400)

    def delete(self, request, slug, format=None):
        try:
            item = Notification.objects.get(slug=slug)
        except Notification.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)


class NotificationAPIListView(LoggingMixin, generics.CreateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def get(self, request, format=None):
        items = Notification.objects.order_by('-pk')
        limit = self.request.query_params.get('limit')
        return KgPagination.get_response(limit,items,request,NotificationGetSerializer)
    

    def post(self, request, format=None):
        serializer = NotificationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return TranslatedErrorResponse(serializer.errors, status=400)


class NotificationByUserAPIListView(LoggingMixin, generics.CreateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def get(self, request,slug, format=None):
        items = Notification.objects.filter(read=False,receiver__slug=slug).order_by('-pk')
        limit = self.request.query_params.get('limit')
        return KgPagination.get_response(limit,items,request,NotificationGetSerializer)


class NotificationByUserByMobileAPIListView(LoggingMixin, generics.CreateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def get(self, request,slug, format=None):
        items = Notification.objects.filter(read=False,receiver__slug=slug).order_by('-pk')
        serializer = NotificationGetSerializer(items,many=True)
        return Response(serializer.data)


class MessageAPIView(LoggingMixin, generics.CreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def get(self, request, slug, format=None):
        try:
            item = Message.objects.get(slug=slug)
            serializer = MessageSerializer(item)
            return Response(serializer.data)
        except Message.DoesNotExist:
            return Response(status=404)

    def put(self, request, slug, format=None):
        try:
            item = Message.objects.get(slug=slug)
        except Message.DoesNotExist:
            return Response(status=404)
        serializer = MessageSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return TranslatedErrorResponse(serializer.errors, status=400)

    def delete(self, request, slug, format=None):
        try:
            item = Message.objects.get(slug=slug)
        except Message.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)


class MessageMobileAPIListView(LoggingMixin, generics.CreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def get(self, request, format=None):
        items = Message.objects.order_by('-pk')
        return Response(MessageGetSerializer(items, many=True).data)


class MessageAPIListView(LoggingMixin, generics.CreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def get(self, request, format=None):
        items = Message.objects.order_by('-pk')
        limit = self.request.query_params.get('limit')
        return KgPagination.get_response(limit,items,request,MessageGetSerializer)

    def post(self, request, format=None):
        self.data = request.data.copy()
        try:
            receiver = get_object_or_404(User, id=self.data['receiver'])
            sender = get_object_or_404(User, id=self.data['sender'])
            
            if sender == receiver:
                return Response({"message": "Vous ne pouvez pas vous envoyer de message."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if a conversation already exists with the participants
            conversation = Conversation.objects.filter(participants=sender).filter(participants=receiver).first()
            if not conversation:
                conversation = Conversation.objects.create()
                conversation.participants.add(sender, receiver)
            self.data['conversation']=conversation.id
            serializer = MessageSerializer(data=self.data)
            if serializer.is_valid():
                serializer.save(conversation=conversation, sender=sender, receiver=receiver)
                
                content = "Vous avez un nouveau message"
                Notification.objects.create(
                    receiver=receiver, content=content, notif_type=MESSAGERIE, data=serializer.data)
                item = Message.objects.get(pk=serializer.data.get("id"))
                def send_notification():
                    notify.push_notif(to=receiver.token,title="Notification", body=content, data=serializer.data)
                
                response = Response(MessageGetPostSerializer(item).data, status=status.HTTP_201_CREATED)
                response._resource_closers.append(send_notification)
                return response
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"message": "One or both users do not exist."}, status=status.HTTP_404_NOT_FOUND)
    

class ConversationAPIView(LoggingMixin, generics.CreateAPIView):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer

    def get(self, request, slug, format=None):
        try:
            item = Conversation.objects.get(slug=slug)
            serializer = ConversationSerializer(item)
            return Response(serializer.data)
        except Conversation.DoesNotExist:
            return Response(status=404)

    def put(self, request, slug, format=None):
        try:
            item = Conversation.objects.get(slug=slug)
        except Conversation.DoesNotExist:
            return Response(status=404)
        serializer = ConversationSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return TranslatedErrorResponse(serializer.errors, status=400)

    def delete(self, request, slug, format=None):
        try:
            item = Conversation.objects.get(slug=slug)
        except Conversation.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)


class ConversationAPIListView(LoggingMixin, generics.CreateAPIView):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer

    def get(self, request, format=None):
        items = Conversation.objects.order_by('-pk')
        limit = self.request.query_params.get('limit')
        return KgPagination.get_response(limit,items,request,ConversationGetSerializer)
    

    def post(self, request, format=None):
        serializer = ConversationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return TranslatedErrorResponse(serializer.errors, status=400)


class ConversationByUserByMobileAPIListView(LoggingMixin, generics.RetrieveAPIView):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer

    def get(self, request,slug, format=None):
        latest_message_subquery = Message.objects.filter(conversation=OuterRef('-pk')).order_by('-created_at').values('created_at')[:1]
        items = Conversation.objects.filter(
            participants__slug__in=[slug]).annotate(latest_message_created_at=Subquery(latest_message_subquery)
        ).order_by('-latest_message_created_at')
        serializer = ConversationGetSerializer(items,many=True,context={"sender":slug})
        return Response(serializer.data)


class MessageByUserAPIListView(LoggingMixin, generics.RetrieveAPIView):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer

    def get(self, request,slug, format=None):
        receiver = request.user.slug
        sender = slug
        # ic(receiver,sender)
        items = Message.objects.filter(Q(sender__slug=sender,receiver__slug=receiver)
                                       |Q(sender__slug=receiver,receiver__slug=sender)
                                       ).order_by('-pk')
        serializer = MessageGetSerializer(items,many=True)
        return Response(serializer.data)


class ConversationByUserAPIListView(LoggingMixin, generics.RetrieveAPIView):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer

    def get(self, request,slug, format=None):
        latest_message_subquery = Message.objects.filter(conversation=OuterRef('-pk')).order_by('-created_at').values('created_at')[:1]
        items = Conversation.objects.filter(
            participants__slug__in=[slug]).annotate(latest_message_created_at=Subquery(latest_message_subquery)
        ).order_by('-latest_message_created_at')
        limit = self.request.query_params.get('limit')
        search = self.request.query_params.get('q')
        if search:
            items = items.filter(Q(participants__nom__icontains=search)|
                                 Q(participants__prenom__icontains=search) )
        return KgPagination.get_response(limit,items,request,ConversationGetWebSerializer)

    

class MessagesByConversationAPIListView(LoggingMixin, generics.RetrieveAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def get(self, request,slug, format=None):
        items = Message.objects.filter(conservation__slug=slug).order_by('-pk')
        serializer = MessageGetSerializer(items,many=True)
        return Response(serializer.data)
    

class ScriptMessageAPIListView(LoggingMixin, generics.RetrieveAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def get(self, request, format=None):
        items = Message.objects.order_by('-pk')
        for item in items:
            item.slug = str(item.slug)+str(item.id)
            item.save()
        items_1 = Conversation.objects.order_by('-pk')
        for item in items_1:
            item.slug = str(item.slug)+str(item.id)
            item.save()
        limit = self.request.query_params.get('limit')
        return KgPagination.get_response(limit,items,request,MessageGetSerializer)

    

class CallbackIntechAPIView(LoggingMixin,generics.CreateAPIView):
    permission_classes = (
    )
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def post(self, request, format=None):
        data=request.data
        CallbackPayment.objects.create(data=data)
        status = data.get('status')
        dataHash = data.get('sha256Hash')
        transaction = data.get('transaction')
        transactionId = transaction.get('transactionId')
        externalTransactionId = transaction.get('externalTransactionId')
        apiKey = API_KEY
        key = str(transactionId) + "|" + str(externalTransactionId)+"|"+ str(apiKey)
        if dataHash == hashlib.sha256(key.encode('utf8')).hexdigest():
            pass
        return Response(status=200)


class NewsletterAPIView(LoggingMixin, generics.CreateAPIView):
    queryset = Newsletter.objects.all()
    serializer_class = NewsletterSerializer

    def get(self, request, slug, format=None):
        try:
            item = Newsletter.objects.get(slug=slug)
            serializer = NewsletterSerializer(item)
            return Response(serializer.data)
        except Newsletter.DoesNotExist:
            return Response(status=404)

    def put(self, request, slug, format=None):
        try:
            item = Newsletter.objects.get(slug=slug)
        except Newsletter.DoesNotExist:
            return Response(status=404)
        serializer = NewsletterSerializer(item, data=request.data,
                                          partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return TranslatedErrorResponse(serializer.errors, status=400)

    def delete(self, request, slug, format=None):
        try:
            item = Newsletter.objects.get(slug=slug)
        except Newsletter.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)


class NewsletterAPIListView(LoggingMixin, generics.CreateAPIView):
    queryset = Newsletter.objects.all()
    serializer_class = NewsletterSerializer


    def get(self, request, format=None):
        items = Newsletter.objects.order_by('-pk')
        limit = self.request.query_params.get('limit')
        return KgPagination.get_response(limit,items,request,NewsletterSerializer)

    def post(self, request, format=None):
        serializer = NewsletterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return TranslatedErrorResponse(serializer.errors, status=400)


class NewsletterVisitorAPIListView(LoggingMixin, generics.CreateAPIView):
    permission_classes = (

    )
    queryset = Newsletter.objects.all()
    serializer_class = NewsletterSerializer

    def post(self, request, format=None):
        serializer = NewsletterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            item = Newsletter.objects.get(pk=serializer.data.get("id"))
            subject= "NEWSLETTER"
            notify.send_email(subject, item.email, 'mail_newsletter.html',{'settings': settings})
            return Response(serializer.data, status=201)
        return TranslatedErrorResponse(serializer.errors, status=400)


class CategorieAPIView(LoggingMixin, generics.RetrieveAPIView):
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer

    def get(self, request, slug, format=None):
        try:
            item = Categorie.objects.get(slug=slug)
            serializer = CategorieSerializer(item)
            return Response(serializer.data)
        except Categorie.DoesNotExist:
            return Response(status=404)

    def put(self, request, slug, format=None):
        try:
            item = Categorie.objects.get(slug=slug)
        except Categorie.DoesNotExist:
            return Response(status=404)
        serializer = CategorieSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return TranslatedErrorResponse(serializer.errors, status=400)

    def delete(self, request, slug, format=None):
        try:
            item = Categorie.objects.get(slug=slug)
        except Categorie.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)


class CategorieAPIListView(LoggingMixin, generics.CreateAPIView):
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer

    def get(self, request, format=None):
        items = Categorie.objects.order_by('-pk')
        limit = self.request.query_params.get('limit')
        return KgPagination.get_response(limit,items,request,CategorieSerializer)
    

    def post(self, request, format=None):
        serializer = CategorieSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return TranslatedErrorResponse(serializer.errors, status=400)


class ImageAPIView(LoggingMixin, generics.RetrieveAPIView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer

    def get(self, request, slug, format=None):
        try:
            item = Image.objects.get(slug=slug)
            serializer = ImageSerializer(item)
            return Response(serializer.data)
        except Image.DoesNotExist:
            return Response(status=404)

    def put(self, request, slug, format=None):
        try:
            item = Image.objects.get(slug=slug)
        except Image.DoesNotExist:
            return Response(status=404)
        serializer = ImageSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return TranslatedErrorResponse(serializer.errors, status=400)

    def delete(self, request, slug, format=None):
        try:
            item = Image.objects.get(slug=slug)
        except Image.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)


class ImageAPIListView(LoggingMixin, generics.CreateAPIView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer

    def get(self, request, format=None):
        items = Image.objects.order_by('-pk')
        limit = self.request.query_params.get('limit')
        return KgPagination.get_response(limit,items,request,ImageSerializer)
    

    def post(self, request, format=None):
        serializer = ImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return TranslatedErrorResponse(serializer.errors, status=400)


class ProduitAPIView(LoggingMixin, generics.RetrieveAPIView):
    queryset = Produit.objects.all()
    serializer_class = ProduitSerializer

    def get(self, request, slug, format=None):
        try:
            item = Produit.objects.get(slug=slug)
            serializer = ProduitGetSerializer(item)
            return Response(serializer.data)
        except Produit.DoesNotExist:
            return Response(status=404)

    def put(self, request, slug, format=None):
        images = []
        if 'images' in request.data and request.data['images']:
            images = get_images(request.FILES.getlist('images',[]))
        try:
            item = Produit.objects.get(slug=slug)
            self.data = request.data.copy()
            if "images" in self.data and self.data['images']:
                del self.data['images']
            serializer = ProduitSerializer(item, data=self.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                for i in images:
                    item.images.add(i)
                item.save()
                return Response(serializer.data)
            return TranslatedErrorResponse(serializer.errors, status=400)
        except Produit.DoesNotExist:
            return Response(status=404)

    def delete(self, request, slug, format=None):
        try:
            item = Produit.objects.get(slug=slug)
        except Produit.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)


class ProduitVisiteurAPIListView(LoggingMixin, generics.RetrieveAPIView):
    permission_classes = ()
    queryset = Produit.objects.all()
    serializer_class = ProduitSerializer

    def get(self, request, format=None):
        items = Produit.objects.filter(status=PUBLISHED).order_by('-pk')
        limit = self.request.query_params.get('limit')
        q = self.request.query_params.get('q')
        category_id = self.request.query_params.get('category_id')
        category = self.request.query_params.get('category')
        items = items.filter(nom__icontains=q) if q else items
        items = items.filter(categorie__id=category_id) if category_id else items
        items = items.filter(categorie__nom__icontains=category) if category else items
        return KgPagination.get_response(limit,items,request,ProduitGetSerializer)


class ProduitAPIListView(LoggingMixin, generics.CreateAPIView):
    queryset = Produit.objects.all()
    serializer_class = ProduitSerializer

    def get(self, request, format=None):
        items = Produit.objects.order_by('-pk')
        limit = self.request.query_params.get('limit')
        search = self.request.query_params.get('q')
        if search:
            search_terms = search.split()
            nom_conditions = [Q(nom__icontains=term) for term in search_terms]
            categorie_conditions = [Q(categorie__nom__icontains=term) for term in search_terms]
            nom_filter = reduce(and_, nom_conditions)
            categorie_filter = reduce(and_, categorie_conditions)
            items = items.filter(
                nom_filter |
                categorie_filter 
            )
        return KgPagination.get_response(limit,items,request,ProduitGetSerializer)
    

    def post(self, request, format=None):
        images = []
        if 'images' in request.data and request.data['images']:
            images = get_images(request.FILES.getlist('images',[]))
        self.data = request.data.copy()
        if "images" in self.data and self.data['images']:
            del self.data['images']
        serializer = ProduitSerializer(data=self.data)
        if serializer.is_valid():
            item = serializer.save()
            for i in images:
                item.images.add(i)
            item.save()
            return Response(serializer.data, status=201)
        return TranslatedErrorResponse(serializer.errors, status=400)


class ProduitMobileAPIListView(LoggingMixin, generics.RetrieveAPIView):
    permission_classes = ()
    queryset = Produit.objects.all()
    serializer_class = ProduitSerializer

    def get(self, request, format=None):
        items = Produit.objects.filter(status=PUBLISHED).order_by('-pk')
        limit = self.request.query_params.get('limit')
        search = self.request.query_params.get('q')
        if search:
            search_terms = search.split()
            nom_conditions = [Q(nom__icontains=term) for term in search_terms]
            categorie_conditions = [Q(categorie__nom__icontains=term) for term in search_terms]
            nom_filter = reduce(and_, nom_conditions)
            categorie_filter = reduce(and_, categorie_conditions)
            items = items.filter(
                nom_filter |
                categorie_filter 
            )
        return Response(ProduitGetSerializer(items, many=True).data)


class ProduitByVendeurAPIListView(LoggingMixin, generics.RetrieveAPIView):
    queryset = Produit.objects.all()
    serializer_class = ProduitSerializer

    def get(self, request,slug, format=None):
        items = Produit.objects.filter(vendeur__slug=slug).order_by('-pk')
        limit = self.request.query_params.get('limit')
        return KgPagination.get_response(limit,items,request,ProduitGetSerializer)


class ProduitByVendeurByMobileAPIListView(LoggingMixin, generics.RetrieveAPIView):
    queryset = Produit.objects.all()
    serializer_class = ProduitSerializer

    def get(self, request,slug, format=None):
        items = Produit.objects.filter(vendeur__slug=slug).order_by('-pk')
        serializer = ProduitGetSerializer(items,many=True)
        return Response(serializer.data)
    

class CategorieByMobileAPIListView(LoggingMixin, generics.RetrieveAPIView):
    permission_classes = ()
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer

    def get(self, request, format=None):
        items = Categorie.objects.order_by('-pk')
        serializer = CategorieSerializer(items,many=True)
        return Response(serializer.data)
    


class VoucherAPIView(LoggingMixin, generics.RetrieveAPIView):
    queryset = Voucher.objects.all()
    serializer_class = VoucherSerializer

    def get(self, request, slug, format=None):
        try:
            item = Voucher.objects.get(slug=slug)
            serializer = VoucherSerializer(item)
            return Response(serializer.data)
        except Voucher.DoesNotExist:
            return Response(status=404)

    def put(self, request, slug, format=None):
        try:
            item = Voucher.objects.get(slug=slug)
        except Voucher.DoesNotExist:
            return Response(status=404)
        serializer = VoucherSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return TranslatedErrorResponse(serializer.errors, status=400)

    def delete(self, request, slug, format=None):
        try:
            item = Voucher.objects.get(slug=slug)
        except Voucher.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)


class VoucherMobileAPIListView(LoggingMixin, generics.CreateAPIView):
    permission_classes = ()
    queryset = Voucher.objects.all()
    serializer_class = VoucherSerializer

    def get(self, request, format=None):
        items = Voucher.objects.order_by('-pk')
        return Response(VoucherSerializer(items, many=True).data)


class VoucherAPIListView(LoggingMixin, generics.CreateAPIView):
    queryset = Voucher.objects.all()
    serializer_class = VoucherSerializer

    def get(self, request, format=None):
        items = Voucher.objects.order_by('-pk')
        limit = self.request.query_params.get('limit')
        return KgPagination.get_response(limit,items,request,VoucherSerializer)
    

    def post(self, request, format=None):
        serializer = VoucherSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return TranslatedErrorResponse(serializer.errors, status=400)


class AchatVoucherAPIView(LoggingMixin, generics.RetrieveAPIView):
    queryset = AchatVoucher.objects.all()
    serializer_class = AchatVoucherSerializer

    def get(self, request, slug, format=None):
        try:
            item = AchatVoucher.objects.get(slug=slug)
            serializer = AchatVoucherGetSerializer(item)
            return Response(serializer.data)
        except AchatVoucher.DoesNotExist:
            return Response(status=404)

    def put(self, request, slug, format=None):
        try:
            item = AchatVoucher.objects.get(slug=slug)
        except AchatVoucher.DoesNotExist:
            return Response(status=404)
        serializer = AchatVoucherSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return TranslatedErrorResponse(serializer.errors, status=400)

    def delete(self, request, slug, format=None):
        try:
            item = AchatVoucher.objects.get(slug=slug)
        except AchatVoucher.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)


class AchatVoucherAPIListView(LoggingMixin, generics.CreateAPIView):
    queryset = AchatVoucher.objects.all()
    serializer_class = AchatVoucherSerializer

    def get(self, request, format=None):
        items = AchatVoucher.objects.order_by('-pk')
        limit = self.request.query_params.get('limit')
        return KgPagination.get_response(limit,items,request,AchatVoucherGetSerializer)
    

    def post(self, request, format=None):
        serializer = AchatVoucherSerializer(data=request.data)
        if serializer.is_valid():
            achat = serializer.save()
            achat.user.points += achat.voucher.points
            achat.user.save()
            achat.paid = True
            achat.save()
            content = f"Vos venez de recevoir {achat.voucher.points} point(s) suite à votre achat de Voucher pour {achat.voucher.prix}qar"
            Notification.objects.create(receiver=achat.user, content=content, notif_type=ACHAT_VOUCHER, data=serializer.data)
            return Response(serializer.data, status=201)
        return TranslatedErrorResponse(serializer.errors, status=400)

class AchatVoucherByUserAPIListView(LoggingMixin, generics.RetrieveAPIView):
    queryset = AchatVoucher.objects.all()
    serializer_class = AchatVoucherSerializer

    def get(self, request,slug, format=None):
        items = AchatVoucher.objects.filter(user__slug=slug).order_by('-pk')
        return Response(AchatVoucherGetSerializer(items, many=True).data)
    

 
        
class AchatVoucherMobileAPIListView(LoggingMixin, generics.CreateAPIView):
    queryset = AchatVoucher.objects.all()
    serializer_class = AchatVoucherSerializer

    def get(self, request, format=None):
        items = AchatVoucher.objects.order_by('-pk')
        return Response(AchatVoucherGetSerializer(items, many=True).data)




class CartItemAPIView(LoggingMixin, generics.RetrieveAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

    def get(self, request, slug, format=None):
        try:
            item = CartItem.objects.get(slug=slug)
            serializer = CartItemGetSerializer(item)
            return Response(serializer.data)
        except CartItem.DoesNotExist:
            return Response(status=404)

    def put(self, request, slug, format=None):
        try:
            item = CartItem.objects.get(slug=slug)
        except CartItem.DoesNotExist:
            return Response(status=404)
        serializer = CartItemSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return TranslatedErrorResponse(serializer.errors, status=400)

    def delete(self, request, slug, format=None):
        try:
            item = CartItem.objects.get(slug=slug)
        except CartItem.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)


class CartItemAPIListView(LoggingMixin, generics.CreateAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

    def get(self, request, format=None):
        items = CartItem.objects.order_by('-pk')
        limit = self.request.query_params.get('limit')
        return KgPagination.get_response(limit,items,request,CartItemGetSerializer)

    def post(self, request, format=None):
        serializer = CartItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return TranslatedErrorResponse(serializer.errors, status=400)


class CartAPIView(LoggingMixin, generics.RetrieveAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    def get(self, request, slug, format=None):
        try:
            item = Cart.objects.get(slug=slug)
            serializer = CartGetSerializer(item)
            return Response(serializer.data)
        except Cart.DoesNotExist:
            return Response(status=404)

    def put(self, request, slug, format=None):
        try:
            item = Cart.objects.get(slug=slug)
        except Cart.DoesNotExist:
            return Response(status=404)
        serializer = CartSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return TranslatedErrorResponse(serializer.errors, status=400)

    def delete(self, request, slug, format=None):
        try:
            item = Cart.objects.get(slug=slug)
        except Cart.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)


class CartAddAPIListView(generics.CreateAPIView):
    permission_classes = ()
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    def post(self, request, format=None):
        items = None
        cart = None
        if 'item_list' in request.data and request.data['item_list']:
           items = literal_eval(request.data['item_list'])
        if 'user' in request.data and request.data['user']:
            if Cart.objects.filter(user=request.data['user']).exists():
                cart = Cart.objects.get(user=request.data['user'])
            else:
                serializer = CartSerializer(data=request.data)
                if serializer.is_valid():
                    cart = serializer.save()
            if items:
                return add_to_cart(cart, items)
            else:
                return Response(serializer.data, status=201)
        return TranslatedErrorResponse(serializer.errors, status=400)


class CartByUserAPIView(LoggingMixin, generics.RetrieveAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    def get(self, request, slug, format=None):
        try:
            item = Cart.objects.get(user__slug=slug)
            serializer = CartGetSerializer(item)
            return Response(serializer.data)
        except Cart.DoesNotExist:
            return Response(status=404)


class CartClearAPIView(LoggingMixin, generics.CreateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    def get(self, request, slug, format=None):
        try:
            item = Cart.objects.get(slug=slug)
            item.clear_cart()
            serializer = CartSerializer(item)
            return Response(serializer.data)
        except Cart.DoesNotExist:
            return Response(status=404)


class CartAPIListView(LoggingMixin, generics.CreateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    def get(self, request, format=None):
        items = Cart.objects.order_by('-pk')
        limit = self.request.query_params.get('limit')
        return KgPagination.get_response(limit,items,request,CartGetSerializer)

    def post(self, request, format=None):
        serializer = CartSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return TranslatedErrorResponse(serializer.errors, status=400)


class OrderAPIView(LoggingMixin, generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    
    def notify_user_commande(self, sujet, order):
        contenu = f"Votre commande {order.code_commande} de {order.total}XOF vient d'être {order.statut} sur {APP_NAME}."
        subject = sujet
        to = order.user.email
        template_src = 'mail_notification.html'
        name = f"{order.user.prenom} {order.user.nom}"
        context = {
            'email': to,
            "name": name,
            'settings': settings,
            "id":"false",
            "contenu":contenu,
            "year":timezone.now().year
        }
        notify.send_email(subject, to, template_src, context)
        Notification.objects.create(receiver=order.user, data=OrderSerializer(order).data, 
                                    content=contenu, notif_type=COMMANDE)

    def get(self, request, slug, format=None):
        try:
            item = Order.objects.get(slug=slug)
            serializer = OrderGetSerializer(item)
            return Response(serializer.data)
        except Order.DoesNotExist:
            return Response(status=404)

    def put(self, request, slug, format=None):
        statut = None
        try:
            item = Order.objects.get(slug=slug)
            statut = item.statut
        except Order.DoesNotExist:
            return Response(status=404)
        serializer = OrderSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            order = serializer.save()
            response = Response(serializer.data)
            if order.statut == CONFIRMEE and order.statut != statut:
                sujet = "Confirmation de commande"
                self.notify_user_commande(sujet, order)
                response._resource_closers.append(self.notify_user_commande(sujet, order))
            if order.statut == LIVREE and order.statut != statut:
                sujet = "Livraison de commande"
                response._resource_closers.append(self.notify_user_commande(sujet, order))
            if order.statut == ANNULEE and order.statut != statut:
                sujet = "ANNULATION de commande"
                response._resource_closers.append(self.notify_user_commande(sujet, order))
            return response
        return TranslatedErrorResponse(serializer.errors, status=400)

    def delete(self, request, slug, format=None):
        try:
            item = Order.objects.get(slug=slug)
        except Order.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)


class OrderAPIListView(LoggingMixin, generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get(self, request, format=None):
        items = Order.objects.order_by('-pk')
        limit = self.request.query_params.get('limit')
        return KgPagination.get_response(limit,items,request,OrderGetSerializer)

    def post(self, request, format=None):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return TranslatedErrorResponse(serializer.errors, status=400)


class OrderByUserAPIListView(LoggingMixin, generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get(self, request,slug, format=None):
        items = Order.objects.filter(user__slug=slug, paid=True).order_by('-pk')
        limit = self.request.query_params.get('limit')
        statut = self.request.query_params.get('statut')
        if statut:
            items = items.filter(statut=statut)
        return KgPagination.get_response(limit,items,request,OrderGetSerializer)


class CanceledOrderByUserAPIListView(LoggingMixin, generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get(self, request, slug, format=None):
        items = Order.objects.filter(user__slug=slug, statut=ANNULEE).order_by('-pk')
        limit = self.request.query_params.get('limit')
        return KgPagination.get_response(limit,items,request,OrderGetSerializer)


class OrderByUserMobileAPIListView(LoggingMixin, generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get(self, request,slug, format=None):
        items = Order.objects.filter(user__slug=slug, paid=True).order_by('-pk')
        statut = self.request.query_params.get('statut')
        if statut:
            items = items.filter(statut=statut)
        return Response(OrderGetSerializer(items, many=True).data)


class CanceledOrderByUserMobileAPIListView(LoggingMixin, generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get(self, request, slug, format=None):
        items = Order.objects.filter(user__slug=slug, statut=ANNULEE).order_by('-pk')
        statut = self.request.query_params.get('statut')
        if statut:
            items = items.filter(statut=statut)
        return Response(OrderGetSerializer(items, many=True).data)


class OrderPaymentAPIView(LoggingMixin, generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    
    def notify_user_commande(self, sujet, contenu, order):
        contenu = contenu
        subject = sujet
        to = order.user.email
        template_src = 'mail_notification.html'
        name = f"{order.user.prenom} {order.user.nom}"
        context = {
            'email': to,
            "name": name,
            'settings': settings,
            "id":"false",
            "contenu":contenu,
            "year":timezone.now().year
        }
        notify.send_email(subject, to, template_src, context)
        Notification.objects.create(receiver=order.user, data=OrderSerializer(order).data, 
                                    content=contenu, notif_type=COMMANDE)

    def get(self, request, slug, format=None):
        try:
            order = Order.objects.get(slug=slug)
            saving = 0
            if order.cart.total_points > order.user.points:
                return Response({"message": "Cet utilisateur n'a pas assez de point pour finaliser cette commande"})
            else:
                order.user.points = order.user.points - order.cart.total_points
                order.user.save()
                cart_items_ids = order.cart.items.all().values_list('id', flat=True)
                cart_items = CartItem.objects.filter(pk__in=cart_items_ids)
                for cart in cart_items:
                    saving += cart.produit.discount
            order.paid = True
            order.save()
            Saving.objects.create(order=order, total=saving)
            sujet = "Paiement Commande"
            contenu = f"La paiement de votre commande {order.code_commande} vient d'être effectué avec succes."
            serializer = OrderGetSerializer(order)
            response = Response(serializer.data)
            response._resource_closers.append(self.notify_user_commande(sujet, contenu, order))
            return response
        except Order.DoesNotExist:
            return Response(status=404)


class OrderByVendeurAPIListView(LoggingMixin, generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get(self, request, slug, format=None):
        items = Order.objects.filter(user__slug=slug, paid=True).order_by('-pk')
        limit = self.request.query_params.get('limit')
        statut = self.request.query_params.get('statut')
        if statut:
            items = items.filter(statut=statut)
        return KgPagination.get_response(limit,items,request,OrderDetailSerializer(context={"vendeur":slug}))
        # return Response(OrderDetailSerializer(items, many=True, context={"vendeur":slug}).data)


class OrderByVendeurMobileAPIListView(LoggingMixin, generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get(self, request, slug, format=None):
        items = Order.objects.filter(user__slug=slug, paid=True).order_by('-pk')
        statut = self.request.query_params.get('statut')
        if statut:
            items = items.filter(statut=statut)
        return Response(OrderDetailSerializer(items, many=True, context={"vendeur":slug}).data)


class ConfigPointAPIListView(LoggingMixin, generics.CreateAPIView):
    queryset = ConfigPoint.objects.all()
    serializer_class = ConfigPointSerializer

    def get(self, request, format=None):
        items = ConfigPoint.objects.order_by('-pk')
        return Response(ConfigPointSerializer(items, many=True).data)

    def post(self, request, format=None):
        serializer = ConfigPointSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return TranslatedErrorResponse(serializer.errors, status=400)


class ConfigPointAPIView(LoggingMixin, generics.RetrieveAPIView):
    queryset = ConfigPoint.objects.all()
    serializer_class = ConfigPointSerializer

    def get(self, request, slug, format=None):
        try:
            item = ConfigPoint.objects.get(slug=slug)
            serializer = ConfigPointSerializer(item)
            return Response(serializer.data)
        except ConfigPoint.DoesNotExist:
            return Response(status=404)

    def put(self, request, slug, format=None):
        try:
            item = ConfigPoint.objects.get(slug=slug)
        except ConfigPoint.DoesNotExist:
            return Response(status=404)
        serializer = ConfigPointSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return TranslatedErrorResponse(serializer.errors, status=400)

    def delete(self, request, slug, format=None):
        try:
            item = ConfigPoint.objects.get(slug=slug)
        except ConfigPoint.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)
    

class FavoriAPIView(LoggingMixin, generics.CreateAPIView):
    queryset = Favori.objects.all()
    serializer_class = FavoriSerializer

    def get(self, request, slug, format=None):
        try:
            item = Favori.objects.get(slug=slug)
            serializer = FavoriSerializer(item)
            return Response(serializer.data)
        except Favori.DoesFavorixist:
            return Response(status=404)

    def put(self, request, slug, format=None):
        try:
            item = Favori.objects.get(slug=slug)
        except Favori.DoesFavorixist:
            return Response(status=404)
        serializer = FavoriSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return TranslatedErrorResponse(serializer.errors, status=400)
        

    def delete(self, request, slug, format=None):
        try:
            item = Favori.objects.get(slug=slug)
        except Favori.DoesFavorixist:
            return Response(status=404)
        item.delete()
        return Response(status=204)

class FavoriAPIListView(LoggingMixin, generics.CreateAPIView):
    queryset = Favori.objects.all()
    serializer_class = FavoriSerializer

    def get(self, request, format=None):
        items = Favori.objects.order_by('pk')
        limit = self.request.query_params.get('limit')
        return KgPagination.get_response(limit,items,request,FavoriGetSerializer)
    

    def post(self, request, format=None):
        serializer = FavoriSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class FavoriByUserAPIListView(LoggingMixin, generics.CreateAPIView):
    queryset = Favori.objects.all()
    serializer_class = FavoriSerializer

    def get(self, request,slug, format=None):
        items = Favori.objects.filter(user__slug=slug).order_by('-pk')
        serializer = FavoriGetSerializer(items,many=True)
        return Response(serializer.data)






# import json
# import hashlib
# import base64


# def parse_signed_request(signed_request):
#     encoded_sig, payload = signed_request.split('.', 1)
#     secret = "f624a959f54af2ae56b43c9f7601ba2b"  # Use your app secret here

#     # Decode the data
#     sig = base64_url_decode(encoded_sig)
#     data = json.loads(base64_url_decode(payload).decode('utf-8'))

#     # Confirm the signature
#     expected_sig = hashlib.sha256(payload.encode('utf-8') + secret).digest()
#     if sig != expected_sig:
#         print('Bad Signed JSON signature!')
#         return None

#     return data


# def base64_url_decode(input):
#     input += '=' * ((4 - len(input) % 4) % 4)
#     return base64.urlsafe_b64decode(input.encode('utf-8')).decode('utf-8')


# class TestAPIListView(LoggingMixin, generics.RetrieveAPIView):
#     queryset = ConfigPoint.objects.all()
#     serializer_class = ConfigPointSerializer

#     def get(self, request, format=None):

#         # Mocking the POST request with signed_request
#         signed_request = 'je teste mon app. Par contre il me faudrait les acces.'

#         data = parse_signed_request(signed_request)
#         user_id = data['user_id']

#         # Start data deletion
#         status_url = 'http://127.0.0.1:8000/api/deletion?id=abc123'  # URL to track the deletion
#         confirmation_code = 'abc123'  # unique code for the deletion request

#         response_data = {
#             'url': status_url,
#             'confirmation_code': confirmation_code
#         }

#         print(json.dumps(response_data))
