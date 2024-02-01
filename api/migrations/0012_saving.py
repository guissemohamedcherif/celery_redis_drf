# Generated by Django 3.1.14 on 2024-02-01 14:25

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_auto_20240201_1358'),
    ]

    operations = [
        migrations.CreateModel(
            name='Saving',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(default=uuid.uuid1, editable=False)),
                ('total', models.DecimalField(decimal_places=2, max_digits=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='savings', to='api.order')),
            ],
        ),
    ]
