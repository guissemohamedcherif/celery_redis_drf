# Generated by Django 3.1.14 on 2024-01-29 17:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20240124_1146'),
    ]

    operations = [
        migrations.CreateModel(
            name='Categorie',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(default=uuid.uuid1, editable=False)),
                ('nom', models.CharField(max_length=200)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(default=uuid.uuid1, editable=False)),
                ('picture', models.ImageField(upload_to='')),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='points',
            field=models.IntegerField(default=0),
        ),
        migrations.CreateModel(
            name='Voucher',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(default=uuid.uuid1, editable=False)),
                ('prix', models.DecimalField(decimal_places=2, default=0.0, max_digits=50)),
                ('points', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Produit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(default=uuid.uuid1, editable=False)),
                ('nom', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('prix', models.DecimalField(decimal_places=2, default=0.0, max_digits=50)),
                ('quantite', models.IntegerField(default=0)),
                ('points', models.IntegerField(default=0)),
                ('discount', models.DecimalField(decimal_places=2, default=0.0, max_digits=50)),
                ('couverture', models.ImageField(blank=True, null=True, upload_to='')),
                ('tags', models.JSONField(blank=True, default=dict, null=True)),
                ('status', models.CharField(choices=[('drafted', 'drafted'), ('drafted', 'drafted')], default='published', max_length=50)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('categorie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.categorie')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('images', models.ManyToManyField(blank=True, default=[], to='api.Image')),
            ],
        ),
        migrations.AddField(
            model_name='categorie',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
