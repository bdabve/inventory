# Generated by Django 2.2.5 on 2020-08-31 16:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('magasin', '0006_auto_20200831_1426'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='magasinlog',
            name='prix',
        ),
        migrations.RemoveField(
            model_name='magasinlog',
            name='qte',
        ),
        migrations.RemoveField(
            model_name='magasinlog',
            name='valeur',
        ),
    ]