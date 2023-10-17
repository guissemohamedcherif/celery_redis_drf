import uuid
from django.db import models
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
# from django.contrib.postgres.fields import JSONField
from django.db.models import JSONField
from django_resized import ResizedImageField
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


ADMIN = 'admin'
PATIENT = 'patient'
MEDECIN = 'medecin'
SUPERADMIN = 'superadmin'
PENDING = 'pending'
OTHERS = 'others'
DELETED = 'deleted'
CABINET = 'cabinet'
CORPORATE = 'corporate'

USER_TYPES = (
    (ADMIN, ADMIN),
    (MEDECIN, MEDECIN),
    (PATIENT, PATIENT),
    (SUPERADMIN, SUPERADMIN),
    (PENDING, PENDING),
)
PROFILS_OFFRES = (
    (MEDECIN, MEDECIN),
    (CABINET, CABINET),
)


HOMME = 'homme'
FEMME = 'femme'
USER_SEXE = (
    (HOMME, HOMME),
    (FEMME, FEMME),
    (CABINET, CABINET),
)


EPOUX = "époux(se)"
ENFANT = "enfant"
PARENT = "parent"
AYANT_DROIT_STATUS = (
    (EPOUX, EPOUX),
    (ENFANT, ENFANT),
    (PARENT, PARENT),
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
PPD = 'PPD'
RR ="RR"
PMC = 'PMC'
ML = 'ML'

CONDITION_TYPE = (
    (CGU, CGU),
    (PPD, PPD),
    (RR, RR),
    (PMC, PMC),
    (ML, ML),
)


XOF = 'XOF'
EUR = 'EUR'
USD = 'USD'
CURRENCY = (
    (EUR, EUR),
    (USD, USD),
    (XOF, XOF)
)

DAY = 'DAY'
MONTH = 'MONTH'
YEAR = 'YEAR'
ILLIMITE = 'ILLIMITE'
FREQUENCY = (
    (DAY, DAY),
    (MONTH, MONTH),
    (YEAR, YEAR),
    (ILLIMITE, ILLIMITE),
)


KIVU_TOP = 'KIVU_TOP'
KC1 = 'KC1'
KC_BUSINESS = 'KC_BUSINESS'
KC_GOLD = 'KC_GOLD'
KC_PREMIUM = 'KC_PREMIUM'
OPTIONS = (
    (KIVU_TOP, KIVU_TOP),
    (KC1, KC1),
    (KC_BUSINESS, KC_BUSINESS),
    (KC_GOLD, KC_GOLD),
    (KC_PREMIUM, KC_PREMIUM),
)

ESPECE = 'espece'
PAYTECH = 'paytech'
PAYPAL = 'paypal'
STRIPE = 'stripe'
PAYDUNYA = 'paydunya'
WAVE = 'wave'
SHARE_GROUPE = 'share_group'
KIVU = 'kivu'
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

MISE_EN_RELATION = 'mise_en_relation'
PLAINTE = 'plainte'
CONTACT_TYPE = (
    (MISE_EN_RELATION, MISE_EN_RELATION),
    (PLAINTE, PLAINTE),
)

NOUVEAU = 'nouveau'
ACCEPTE = 'accepte'
REJETE = 'refuse'
EN_COURS = 'en_cours'
EN_PAUSE = 'en_pause'
CLOTURER = 'cloturer'
VALIDER = 'valider'
ANNULER = 'annuler'
ETAT_RDV = (
    (NOUVEAU, NOUVEAU),
    (ACCEPTE, ACCEPTE),
    (REJETE, REJETE),
    (ANNULER, ANNULER),
)

EN_ATTENTE = 'en_attente'
ACCEPTEE = 'acceptee'
REFUSEE = 'refusee'
STATUS_CANDIDATURE = (
    (EN_ATTENTE, EN_ATTENTE),
    (ACCEPTEE, ACCEPTEE),
    (REFUSEE, REFUSEE),
)

NOUVEAU = 'nouveau'
EN_COURS = 'en_cours'
TERMINER = 'terminer'
STATUS_RDV = (
    (NOUVEAU, NOUVEAU),
    (EN_COURS, EN_COURS),
    (TERMINER, TERMINER),
)

ABONNEMENT = 'abonnement'
RDV = 'rdv'
CANDIDATURE = 'candidature'
DOSSIER = 'dossier'
MESSAGERIE = 'messagerie'
COMPTE_SECRETAIRE = 'compte_secretaire'
REABONNEMENT = 'réabonnement'

NOTIF_TYPE = (
    (ABONNEMENT, ABONNEMENT),
    (RDV, RDV),
    (CANDIDATURE, CANDIDATURE),
    (DOSSIER, DOSSIER),
    (COMPTE_SECRETAIRE, COMPTE_SECRETAIRE),
    (REABONNEMENT, REABONNEMENT),
    (CABINET, CABINET),
)
CARTE_BANCAIRE= "BANK_CARD_API_CASH_OUT"
MOYEN_PAIEMENT = (
    ('ORANGE_SN_API_CASH_OUT', 'ORANGE_MONEY'),
    ('WAVE_SN_API_CASH_OUT', 'WAVE'),
    ('FREE_SN_WALLET_CASH_OUT', 'FREE_MONEY'),
    ('EXPRESSO_SN_WALLET_CASH_OUT', 'E_MONEY'),
    ('BANK_TRANSFER_SN_API_CASH_OUT', 'VIREMENT_BANCAIRE'),
    ('BANK_CARD_API_CASH_OUT', 'CARTE_BANCAIRE'),
)

LETTRE_LIAISON="Lettre de liaison"
BILAN_CONSULTATION="Bilan de consultation"
CERTIFICAT="certificat"
MEDICAL="Médical"
DECES="Décès"
COMPTE_RENDU="Compte rendu"
HOSPITALISATION="Hospitalisation"
OPERATOIRE="Opératoire"
PREOPERATOIRE="Préopératoire"
COURRIER="Courrier"
TYPES_DE_COURRIER = (
    (LETTRE_LIAISON, LETTRE_LIAISON),
    (BILAN_CONSULTATION, BILAN_CONSULTATION),
    (CERTIFICAT, CERTIFICAT),
    (MEDICAL, MEDICAL),
    (DECES, DECES),
    (COMPTE_RENDU, COMPTE_RENDU),
    (HOSPITALISATION, HOSPITALISATION),
    (OPERATOIRE, OPERATOIRE),
    (PREOPERATOIRE, PREOPERATOIRE),
    (COURRIER, COURRIER),
)

MARI = 'MARI'
EPOUSE = 'EPOUSE'
PERE = 'PERE'
MERE = 'MERE'
COUSIN = 'COUSIN'
COUSINE = 'COUSINE'
GRAND_PERE = 'GRAND_PERE'
GRAND_MERE = 'GRAND_MERE'
TANTE = 'TANTE'
ONCLE = 'ONCLE'
AUTRE = 'AUTRE'

LIENS_PARENTS = (
    (MARI, 'Mari'),
    (EPOUSE, 'Épouse'),
    (PERE, 'Père'),
    (MERE, 'Mère'),
    (COUSIN, 'Cousin'),
    (COUSINE, 'COUSINE'),
    (GRAND_PERE, 'Grand-père'),
    (GRAND_MERE, 'Grand-mère'),
    (TANTE, 'Tante'),
    (ONCLE, 'Oncle'),
    (AUTRE, 'AUTRE'),

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
    nom = models.CharField(max_length=255)
    prenom = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=255,validators=[isnumbervalidator],unique=True)
    civilite = models.CharField(max_length=50, choices=USER_SEXE,default=HOMME)
    adresse = models.CharField(max_length=1000, null=True,blank=True)
    longitude = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.CharField(max_length=255, null=True, blank=True)
    boite_postal = models.CharField(max_length=1000, null=True,blank=True)
    is_active = models.BooleanField(('active'), default=True)
    is_staff = models.BooleanField(default=False)
    is_archive = models.BooleanField(default=False)
    is_suspended = models.BooleanField(default=False)  
    user_type = models.CharField(max_length=50, choices=USER_TYPES,default=PENDING)
    avatar = ResizedImageField(default="avatars/default.png", upload_to='avatars/', null=True, blank=True)
    password_reset_count = models.IntegerField(null=True, blank=True, default=0)
    first_connexion = models.BooleanField(default=False)
    deletion_id = models.CharField(max_length=1000, blank=True, null=True)
    deletion_type = models.CharField(max_length=50,choices=USER_TYPES,blank=True,null=True)
    date_de_naissance = models.DateField(null=True)
    nationnalite = models.CharField(max_length=500)
    cni = models.CharField(max_length=500, null=True)
    ordre_des_medecins = models.CharField(max_length=255,null=True)
    pays_ordre_des_medecins = models.CharField(max_length=255,null=True)
    date_inscription_ordre = models.DateField(null=True)
    cv = models.FileField(null=True)
    taux_horaire = models.IntegerField(default=0)
    specialite = models.ForeignKey("Specialite",on_delete=models.CASCADE,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey("User", on_delete=models.CASCADE,related_name="parent_user",null=True)
    objects = UserManager()

    USERNAME_FIELD = 'email'
    # these field are required on registering
    REQUIRED_FIELDS = ['nom', 'prenom', 'telephone']
    
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
    patients = models.BooleanField(default=True)
    praticiens = models.BooleanField(default=True)
    rdvs = models.BooleanField(default=True)
    types_consultation = models.BooleanField(default=True)
    paiements = models.BooleanField(default=True)
    messages = models.BooleanField(default=True)
    parametres = models.BooleanField(default=True)
    def __str__(self):
        return f'<AdminUser: {self.pk},email: {self.email}>'
    
class Specialite(models.Model):
    slug = models.SlugField(default=uuid.uuid1)
    nom = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Offre(models.Model):
    slug = models.SlugField(default=uuid.uuid1, max_length=1000)
    title = models.CharField(max_length=500)
    price = models.DecimalField(decimal_places=2, max_digits=50, default=0.0)
    description = models.TextField()
    duration = models.IntegerField(default=1)
    devise = models.CharField(max_length=20, choices=CURRENCY, default=XOF)
    frequence = models.CharField(max_length=20, choices=FREQUENCY,default=MONTH)
    profil = models.CharField(max_length=50, choices=PROFILS_OFFRES,default=MEDECIN)
    reduction =  models.DecimalField(decimal_places=2, max_digits=5, default=10.0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'<Offre: {self.pk},title: {self.title},\
            duration: {self.duration},devise: {self.devise}>\
                frequence:{self.frequence}'

    def save(self, *args, **kwargs):
        super(Offre, self).save(*args, **kwargs)


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


class Abonnement(SafeDeleteModel):
    slug = models.SlugField(default=uuid.uuid1)
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name="user_abonnement")
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    offre = models.ForeignKey(Offre, on_delete=models.CASCADE,related_name="offer_abonnement")
    paid = models.BooleanField(default=False)
    moyen_paiement = models.CharField(max_length=100, choices=MOYEN_PAIEMENT)
    nb_renew = models.IntegerField(default=0)
    price = models.DecimalField(decimal_places=2, max_digits=50, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f'<Abonnement: {self.pk},user: {self.user},\
            offre: {self.offre},date_debut: {self.date_debut}>\
                date_fin:{self.date_fin}'

    def save(self, *args, **kwargs):
        super(Abonnement, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']


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


class Messagerie(SafeDeleteModel):
    slug = models.SlugField(default=uuid.uuid1)
    subject = models.CharField(max_length=1000,null=True)
    sender = models.ForeignKey(User,on_delete=models.CASCADE,related_name="message_receiver")
    receivers = models.ManyToManyField(User,blank=True,default=[])
    content = models.TextField()
    media = models.FileField(null=True, blank=True)
    message = models.ForeignKey('Messagerie',on_delete=models.CASCADE,null=True,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'<Chat: {self.pk},sender: {self.sender},content: {self.content}>'
    # class Meta:
    #     unique_together = ('sender','receiver')

class UserReadMessagerie(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    messagerie = models.ForeignKey(Messagerie, on_delete=models.CASCADE,related_name="userreadmessagerie")

    class Meta:
        unique_together = ('user', 'messagerie',)

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
    contact_type = models.CharField(max_length=50, choices=CONTACT_TYPE, blank=True)
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
    text_fr = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=50,
                            choices=CONDITION_TYPE, default=CGU)
    created_at = models.DateTimeField(auto_now_add=True)


class Faq(models.Model):
    slug = models.SlugField(default=uuid.uuid1)
    titre = models.CharField(max_length=1000)
    description = models.TextField(blank=True, null=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True)
    nb_consultation = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'<Faq: {self.pk},titre: {self.titre},\
            nb_consultation: {self.nb_consultation}>'


class ReponseFaq(models.Model):
    slug = models.SlugField(default=uuid.uuid1)
    faq = models.ForeignKey(
        Faq, on_delete=models.CASCADE, blank=False, null=False)
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'<Faq: {self.pk},faq: {self.faq}>'


class SpecialiteExcelFile(models.Model):
    fichier = models.FileField(upload_to="excel", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)



class Medicament(models.Model):
    slug = models.SlugField(default=uuid.uuid1)
    nom = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


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
    """
    Table Forum
    """

    slug = models.SlugField(default=uuid.uuid1)
    content = models.TextField()
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE, related_name="comment_forum")
    created_by = models.ForeignKey(User,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class BlockedUser(models.Model):
    slug = models.SlugField(default=uuid.uuid1)
    blocking_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocking_users')
    blocked_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_users')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['blocking_user', 'blocked_user']


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
