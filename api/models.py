import uuid
from django.db import models
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
# from django.contrib.postgres.fields import JSONField
from django.db.models import JSONField
from safedelete.models import SafeDeleteModel
from safedelete.managers import SafeDeleteManager
from safedelete.config import DELETED_INVISIBLE
from backend import settings
from django.utils import timezone
from django.db.models.signals import pre_save
from django.dispatch import receiver
from api.utils import Utils
from django.contrib.auth import get_user_model
import os
from api.validators import *

EN_COURS = 'en_cours'
CONFIRMEE = 'confirmee'
LIVREE = 'livree'
ANNULEE = 'annulee'
ORDER_STATUS = (
    (EN_COURS, EN_COURS),
    (CONFIRMEE, CONFIRMEE),
    (LIVREE, LIVREE),
    (ANNULEE,ANNULEE),
)

ADMIN = 'admin'
SUPERADMIN = 'superadmin'
USER = 'user'
VENDEUR = 'vendeur'
DELETED = 'deleted'

USER_TYPES = (
    (USER, USER),
    (VENDEUR, VENDEUR),
    (ADMIN, ADMIN),
    (SUPERADMIN, SUPERADMIN),
)

HOMME = 'homme'
FEMME = 'femme'
USER_SEXE = (
    (HOMME, HOMME),
    (FEMME, FEMME),
)

M = 'M'
MME = 'Mme'
MLLE = 'Mlle'
CIVILITE = (
    (M, M),
    (MME, MME),
    (MLLE, MLLE),
)

ADMIN_TYPE = (
    (ADMIN, ADMIN),
    (SUPERADMIN, SUPERADMIN)
)

CGU = 'CGU'

CONDITION_TYPE = (
    (CGU, CGU),
)


XOF = 'XOF'
EUR = 'EUR'
USD = 'USD'
CURRENCY = (
    (EUR, EUR),
    (USD, USD),
    (XOF, XOF)
)

ESPECE = 'espece'
PAYTECH = 'paytech'
PAYPAL = 'paypal'
STRIPE = 'stripe'
PAYDUNYA = 'paydunya'
WAVE = 'wave'
PAYMENT_MODE = (
    (PAYDUNYA, PAYDUNYA),
)


NEW = 'new'
TRAITED = 'traited'
IN_PROGRESS = 'in_progress'
CONTACT_STATUT = (
    (NEW, NEW),
    (IN_PROGRESS, IN_PROGRESS),
    (TRAITED, TRAITED)
)

ACHAT_VOUCHER = 'achat_voucher'
COMMANDE = 'commande'
SHARING = 'sharing'
NOTIF_TYPE = (
    (ACHAT_VOUCHER, ACHAT_VOUCHER),
    (COMMANDE, COMMANDE),
    (SHARING, SHARING)
)


MOYEN_PAIEMENT = (
    ('ORANGE_SN_API_CASH_OUT', 'ORANGE_MONEY'),
    ('WAVE_SN_API_CASH_OUT', 'WAVE'),
    ('FREE_SN_WALLET_CASH_OUT', 'FREE_MONEY'),
    ('EXPRESSO_SN_WALLET_CASH_OUT', 'E_MONEY'),
    ('BANK_TRANSFER_SN_API_CASH_OUT', 'VIREMENT_BANCAIRE'),
    ('BANK_CARD_API_CASH_OUT', 'CARTE_BANCAIRE'),
)

PUBLISHED = 'published'
DRAFTED = 'drafted'
STATUS_PRODUIT = (
    (DRAFTED, DRAFTED),
    (PUBLISHED, PUBLISHED),
)

class MyModelManager(SafeDeleteManager):
    _safedelete_visibility = DELETED_INVISIBLE


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('user_type', SUPERADMIN)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin, SafeDeleteModel):
    slug = models.UUIDField(default=uuid.uuid4, editable=False)
    prenom = models.CharField(max_length=500, blank=True, null=True)
    nom = models.CharField(max_length=500, blank=True, null=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20,validators=[isnumbervalidator],null=True,blank=True)
    civilite = models.CharField(max_length=50, choices=USER_SEXE,default=HOMME)
    adress = models.TextField(null=True,blank=True)
    date_de_naissance = models.DateField(null=True)
    longitude = models.CharField(max_length=500, blank=True, null=True)
    latitude = models.CharField(max_length=500, blank=True, null=True)
    num_cr = models.CharField(max_length=500, blank=True, null=True)
    cni = models.CharField(max_length=500, blank=True, null=True)
    ninea = models.CharField(max_length=500, blank=True, null=True)
    user_type = models.CharField(max_length=50, choices=USER_TYPES,default=USER)
    points = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(('active'), default=True)
    condition = models.BooleanField(default=False)
    bloquer = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_archive = models.BooleanField(default=False)
    avatar = models.ImageField(default="avatars/default.png", upload_to='avatars/', null=True, blank=True)
    password_reset_count = models.IntegerField(null=True, blank=True, default=0)
    first_connexion = models.BooleanField(default=False)
    deletion_id = models.CharField(max_length=1000, blank=True, null=True)
    deletion_type = models.CharField(max_length=50,choices=USER_TYPES,blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey("User", on_delete=models.CASCADE, blank=True, null=True)
    objects = UserManager()

    USERNAME_FIELD = 'email'
    # these field are required on registering
    REQUIRED_FIELDS = ['prenom', 'nom', 'phone']
    
    class Meta:
        verbose_name = ('user')
        verbose_name_plural = ('users')
        app_label = "api"

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.lower()
        super(User, self).save(*args, **kwargs)

    def __str__(self):
        return f'<User: {self.pk},email: {self.email}, user_type: {self.user_type}>'


class AdminUser(User):
    parent = models.ForeignKey(User, on_delete=models.CASCADE,related_name="admin_user_struc")
    admin_type = models.CharField(max_length=20, choices=ADMIN_TYPE,default=ADMIN)
    dashboard = models.BooleanField(default=True)
    messages = models.BooleanField(default=True)
    parametres = models.BooleanField(default=True)
    def __str__(self):
        return f'<AdminUser: {self.pk},email: {self.email}>'
    

class ModePaiement(models.Model):
    slug = models.SlugField(default=uuid.uuid1)
    logo = models.ImageField(null=True, blank=True)
    titre = models.CharField(max_length=500, default='Mode de payment')
    nom = models.CharField(max_length=20, choices=PAYMENT_MODE,default=PAYDUNYA)
    active = models.BooleanField(default=False)
    description = models.TextField(default="Empty description.")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'<ModePaiement: {self.pk},nom: {self.nom},\
            active: {self.active}>'


class AccountActivation(models.Model):
    slug = models.SlugField(default=uuid.uuid1)
    code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)
    date_used = models.DateTimeField(null=True)
    pwd = models.CharField(max_length=1000, blank=True, null=True)

    def __str__(self):
        return f'<AccountActivation: {self.pk},user: {self.user},\
            used: {self.used}>'


class PasswordReset(SafeDeleteModel):
    slug = models.SlugField(default=uuid.uuid1)
    code = models.CharField(max_length=7, blank=False, null=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=False,
                             null=False, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)
    date_used = models.DateTimeField(null=True)

    objects = MyModelManager()

    def __str__(self):
        return f'<PasswordReset: {self.pk},user: {self.user},\
            used: {self.used}>'
    
    def set_as_used(self):
        self.used = True
        self.date_used = timezone.now()
        self.save()
    

class CallbackPayment(models.Model):
    data = JSONField()
    created_at = models.DateTimeField(auto_now_add=True)


class Notification(SafeDeleteModel):
    slug = models.SlugField(default=uuid.uuid1)
    receiver = models.ForeignKey(User, related_name="receiver_notif",on_delete=models.CASCADE,
                                 blank=True, null=True)
    content = models.TextField()
    data = JSONField(null=True)
    notif_type = models.CharField(max_length=50, choices=NOTIF_TYPE, blank=True)
    is_archived = models.BooleanField(default=False)
    read = models.BooleanField(default=False)
    admins = models.ManyToManyField(User, default=[], blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    objects = MyModelManager()

    def __str__(self):
        return f'<Notification: {self.pk},receiver: {self.receiver},\
            content: {self.content},notif_type: {self.notif_type}>\
                read:{self.read}'

class Contact(models.Model):
    slug = models.SlugField(default=uuid.uuid1)
    email = models.EmailField(unique=False)
    subject = models.CharField(max_length=1000)
    message = models.TextField()
    phone = models.CharField(max_length=1000, blank=True, null=True)
    status = models.CharField(max_length=20, choices=CONTACT_STATUT,default=NEW)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.message) + ''

    def save(self, *args, **kwargs):
        super(Contact, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']


class ResponseContact(models.Model):
    slug = models.SlugField(default=uuid.uuid1)
    message = models.ForeignKey(Contact, on_delete=models.CASCADE)
    response = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

class Newsletter(models.Model):
    slug = models.SlugField(default=uuid.uuid1)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Condition(models.Model):
    slug = models.SlugField(default=uuid.uuid1)
    text = models.TextField()
    type = models.CharField(max_length=50,
                            choices=CONDITION_TYPE, default=CGU)
    created_at = models.DateTimeField(auto_now_add=True)


class Faq(models.Model):
    slug = models.SlugField(default=uuid.uuid1)
    titre = models.CharField(max_length=1000)
    description = models.TextField(blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    nb_consultation = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'<Faq: {self.pk},titre: {self.titre},\
            nb_consultation: {self.nb_consultation}>'


class ReponseFaq(models.Model):
    slug = models.SlugField(default=uuid.uuid1)
    faq = models.ForeignKey(Faq, on_delete=models.CASCADE, blank=False, null=False)
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'<Faq: {self.pk},faq: {self.faq}>'

class Theme(models.Model):
    slug = models.SlugField(default=uuid.uuid1)
    titre = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)



class Forum(models.Model):
    slug = models.SlugField(default=uuid.uuid1, max_length=1000)
    theme = models.ForeignKey(Theme,on_delete=models.CASCADE,related_name="author_forum")
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE,related_name="author_forum")
    view = models.IntegerField(default=0)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'<Forum: {self.pk},thematique: {self.thematique}>'


class CommentForum(models.Model):
    slug = models.SlugField(default=uuid.uuid1)
    content = models.TextField()
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE, related_name="comment_forum")
    created_by = models.ForeignKey(User,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class Signalement(models.Model):
    slug = models.SlugField(default=uuid.uuid1)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    motif = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE,related_name="author_user")
    forum = models.ForeignKey(Forum,on_delete=models.CASCADE,null=True,blank=True)
    comment = models.ForeignKey(CommentForum,on_delete=models.CASCADE,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Conversation(models.Model):
    slug = models.SlugField(default=uuid.uuid1)
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        participant_names = ', '.join([str(participant) for participant in self.participants.all()])
        return f"Conversation with {participant_names}"


class Message(models.Model):
    slug = models.SlugField(default=uuid.uuid1)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver} in {self.conversation}"


class Image(models.Model):
    slug = models.SlugField(default=uuid.uuid1,editable=False)
    picture = models.ImageField()
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Categorie(models.Model):
    slug = models.SlugField(default=uuid.uuid1,editable=False)
    nom = models.CharField(max_length=200)
    image = models.ImageField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE,
                                   blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'<Categorie: {self.pk},nom: {self.nom}>'


class Produit(models.Model):
    slug = models.SlugField(default=uuid.uuid1,editable=False)
    nom = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    prix = models.DecimalField(decimal_places=2, max_digits=50, default=0.0)
    quantite = models.IntegerField(default=0)
    points = models.IntegerField(default=0)
    discount = models.DecimalField(decimal_places=2, max_digits=50, default=0.0)
    prix_afficher = models.DecimalField(decimal_places=2, max_digits=50, default=0.0)
    categorie = models.ForeignKey(Categorie,on_delete=models.CASCADE)
    couverture = models.ImageField(null=True,blank=True)
    is_archived = models.BooleanField(default=False)
    images = models.ManyToManyField(Image,blank=True,default=[])
    tags = JSONField(default=dict, blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_PRODUIT,
                              default=PUBLISHED)
    vendeur = models.ForeignKey(User, on_delete=models.CASCADE, blank=True,
                                null=True, related_name="produits")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True,
                                   null=True, related_name="creator")
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # def save(self, *args, **kwargs):
    #     cfg = ConfigPoint.objects.filter(is_active=True).last()
    #     if cfg and self.points and self.prix:
    #         self.prix_afficher = (self.points * cfg.prix) / cfg.points
    #         self.discount = self.prix - self.prix_afficher
    #     super(Produit, self).save(*args, **kwargs)
    
    def __str__(self):
        return f'<Produit: {self.pk},nom: {self.nom}>'


class Voucher(models.Model):
    slug = models.SlugField(default=uuid.uuid1,editable=False)
    prix = models.DecimalField(decimal_places=2, max_digits=50, default=0.0)
    points = models.IntegerField(default=0)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE,
                                   blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'<Voucher: {self.pk}, prix: {self.prix}, points: {self.points}>'


class AchatVoucher(models.Model):
    slug = models.SlugField(default=uuid.uuid1, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='achats')
    voucher = models.ForeignKey(Voucher, on_delete=models.CASCADE,
                             related_name='achats')
    paid = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'<Voucher: {self.pk}, prix: {self.prix}, points: {self.points}>'


class CartItem(models.Model):
    slug = models.SlugField(default=uuid.uuid1,editable=False)
    quantite = models.PositiveIntegerField(default=0)
    prix = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE)  # Assuming you have a User model for authentication
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cartitem {self.id} - Produit {self.produit.nom} - Quantite: {self.quantite}"


class Cart(models.Model):
    slug = models.SlugField(default=uuid.uuid1,editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name="carts")  # Assuming you have a User model for authentication
    items = models.ManyToManyField(CartItem, blank=True, default=[],
                                   related_name='carts')
    total = models.DecimalField(max_digits=50,decimal_places=2,default=0)
    total_points = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return f"Cart {self.pk} for {self.user.nom} {self.user.prenom}"
    
    def clear_cart(self):
        self.items.set([])
        self.total=0
        self.total_points=0
        self.save()


class Order(models.Model):
    slug = models.SlugField(default=uuid.uuid1,editable=False)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='orders')
    statut = models.CharField(max_length=120,choices=ORDER_STATUS,default=EN_COURS)    
    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name='orders')
    total = models.DecimalField(max_digits=50,decimal_places=2)
    total_points = models.PositiveIntegerField(default=0)
    code_commande = models.CharField(max_length=100,default=Utils.get_order_code)
    moyen_paiement = models.CharField(max_length=50, choices=MOYEN_PAIEMENT)
    paid = models.BooleanField(default=False)
    transaction_intech_code = models.CharField(max_length=200,blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Saving(models.Model):
    slug = models.SlugField(default=uuid.uuid1,editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='savings')
    total = models.DecimalField(max_digits=50,decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)


class ConfigPoint(models.Model):
    slug = models.SlugField(default=uuid.uuid1,editable=False)
    points = models.PositiveIntegerField(default=0)
    prix = models.DecimalField(max_digits=50,decimal_places=2,default=0)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class Favori(models.Model):
    slug = models.SlugField(default=uuid.uuid1)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit,on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('user', 'produit')
    def __str__(self):
        return f'<Favori: {self.pk},user: {self.user}, produit: {self.produit}>'


class Projet(models.Model):
    slug = models.SlugField(default=uuid.uuid1,editable=False)
    nom = models.CharField(max_length=500)
    description = models.TextField(blank=True, null=True)
    video = models.CharField(max_length=1000, blank=True, null=True)
    file = models.FileField(blank=True, null=True)
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE, related_name='projets')
    montant = models.DecimalField(max_digits=50,decimal_places=2, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'<Projet: {self.nom}, montant: {self.montant}>'


class Sharing(models.Model):
    slug = models.SlugField(default=uuid.uuid1,editable=False)
    points = models.PositiveIntegerField(default=0)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='senders')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receivers')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'<Sharing: {self.pk}, points: {self.points}>'