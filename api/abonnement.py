from django.utils import timezone
from dateutil.relativedelta import relativedelta
from rest_framework import status
from rest_framework.response import Response
from .models import Offre, Abonnement,YEAR
import paydunya
from paydunya import Store
from backend.settings import API_URL
from api.serializers import  AbonnementSerializer
import decimal
from api.models import CORPORATE,CARTE_BANCAIRE,MONTH
from icecream import ic

def create_abonnement(request,item):
    try:
        offre = Offre.objects.get(pk=request.data['offre'])
        date_debut = timezone.now()
        if offre.frequence == 'MONTH':
            date_fin = date_debut + relativedelta(months=offre.duration)
        elif offre.frequence == 'YEAR':
            date_fin = date_debut + relativedelta(years=offre.duration)
        else:
            date_fin = date_debut + relativedelta(days=offre.duration)
        price = offre.price
        if offre.frequence == YEAR:
            price = price - (price * decimal.Decimal(0.1))
        abonnement = Abonnement(
            user=item,
            date_debut=date_debut,
            date_fin=date_fin,
            offre=offre,
            moyen_paiement=request.data['moyen_paiement'],
            price=price
        )
        abonnement.save()
        return Response(AbonnementSerializer(abonnement).data,status=201)
    except Offre.DoesNotExist:
        return Response({"message": "L'offre sélectionné n'existe pas"}, status=status.HTTP_400_BAD_REQUEST)


def create_corporate_abonnement(item):
    # try:
    offre, created = Offre.objects.get_or_create(
    title='Offre Corporatif',
    defaults={
        'description': "Offre corporative",
        'profil': CORPORATE,
        'active': False
    }
    )
    date_debut = timezone.now()
    if offre.frequence == MONTH:
        date_fin = date_debut + relativedelta(months=offre.duration)
    elif offre.frequence == YEAR:
        date_fin = date_debut + relativedelta(years=offre.duration)
    else:
        date_fin = date_debut + relativedelta(days=offre.duration)
    price = offre.price
    if offre.frequence == YEAR:
        price = price - (price * decimal.Decimal(0.1))
    ab = Abonnement.objects.create(
        user=item,
        date_debut=date_debut,
        date_fin=date_fin,
        offre=offre,
        moyen_paiement=CARTE_BANCAIRE,
        price=price,
        paid=True
    )

