# Generated by Django 3.1.14 on 2024-01-31 11:30

import api.utils
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_auto_20240130_1450'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(default=uuid.uuid1, editable=False)),
                ('total', models.DecimalField(decimal_places=2, default=0, max_digits=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(default=uuid.uuid1, editable=False)),
                ('statut', models.CharField(choices=[('en_cours', 'en_cours'), ('confirmee', 'confirmee'), ('livree', 'livree'), ('annulee', 'annulee')], default='en_cours', max_length=120)),
                ('total', models.DecimalField(decimal_places=2, max_digits=50)),
                ('code_commande', models.CharField(default=api.utils.Utils.get_order_code, max_length=100)),
                ('moyen_paiement', models.CharField(choices=[('ORANGE_SN_API_CASH_OUT', 'ORANGE_MONEY'), ('WAVE_SN_API_CASH_OUT', 'WAVE'), ('FREE_SN_WALLET_CASH_OUT', 'FREE_MONEY'), ('EXPRESSO_SN_WALLET_CASH_OUT', 'E_MONEY'), ('BANK_TRANSFER_SN_API_CASH_OUT', 'VIREMENT_BANCAIRE'), ('BANK_CARD_API_CASH_OUT', 'CARTE_BANCAIRE')], max_length=50)),
                ('paid', models.BooleanField(default=False)),
                ('transaction_intech_code', models.CharField(blank=True, max_length=200, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('cart', models.ManyToManyField(blank=True, default=[], related_name='orders', to='api.Cart')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(default=uuid.uuid1, editable=False)),
                ('quantite', models.PositiveIntegerField(default=0)),
                ('prix', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.cart')),
                ('produit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.produit')),
            ],
        ),
        migrations.AddField(
            model_name='cart',
            name='items',
            field=models.ManyToManyField(blank=True, default=[], related_name='carts', to='api.CartItem'),
        ),
        migrations.AddField(
            model_name='cart',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='carts', to=settings.AUTH_USER_MODEL),
        ),
    ]
