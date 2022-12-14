# Generated by Django 2.2.5 on 2020-08-28 11:07

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fournisseur', '0002_auto_20200828_1041'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fournisseur',
            name='email',
            field=models.EmailField(blank=True, max_length=254, unique=True, validators=[django.core.validators.EmailValidator]),
        ),
        migrations.AlterField(
            model_name='fournisseur',
            name='telephone',
            field=models.CharField(blank=True, max_length=20, validators=[django.core.validators.RegexValidator(message='Enter a valid phone number', regex='^\\+?1?\\d{9,15}$')]),
        ),
    ]
