# Generated by Django 3.1.14 on 2024-02-06 12:10

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_auto_20240205_1641'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConfigPoint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(default=uuid.uuid1, editable=False)),
                ('point', models.PositiveIntegerField(default=0)),
                ('prix', models.DecimalField(decimal_places=2, default=0, max_digits=50)),
                ('is_active', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]