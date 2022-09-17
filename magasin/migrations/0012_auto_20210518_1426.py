# Generated by Django 2.0.5 on 2021-05-18 13:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('magasin', '0011_article_observation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gestionstocks',
            name='art_id',
        ),
        migrations.AlterModelOptions(
            name='article',
            options={'ordering': ('code', 'ref', 'designation')},
        ),
        migrations.AlterModelOptions(
            name='movement',
            options={'ordering': ('-movement_date',)},
        ),
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(db_index=True, max_length=200, unique=True),
        ),
        migrations.DeleteModel(
            name='GestionStocks',
        ),
    ]