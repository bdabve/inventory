# Generated by Django 2.0.5 on 2021-05-24 14:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('magasin', '0013_command'),
    ]

    operations = [
        migrations.AddField(
            model_name='command',
            name='status',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
