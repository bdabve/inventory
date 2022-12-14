# Generated by Django 2.2.5 on 2020-08-31 12:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('magasin', '0004_auto_20200818_1725'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='movement',
            options={'ordering': ('movement_date',)},
        ),
        migrations.RemoveField(
            model_name='movement',
            name='code',
        ),
        migrations.RemoveField(
            model_name='movement',
            name='designation',
        ),
        migrations.RemoveField(
            model_name='movement',
            name='slug',
        ),
        migrations.AddField(
            model_name='movement',
            name='user_id',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='user_id', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='movement',
            name='art_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='article_id', to='magasin.Article'),
        ),
    ]
