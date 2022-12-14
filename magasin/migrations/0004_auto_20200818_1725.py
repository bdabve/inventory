# Generated by Django 2.0.5 on 2020-08-18 15:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('magasin', '0003_auto_20200818_1651'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='magasinlog',
            options={'ordering': ('log_date', 'slug')},
        ),
        migrations.AddField(
            model_name='magasinlog',
            name='code',
            field=models.CharField(db_index=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='magasinlog',
            name='designation',
            field=models.CharField(db_index=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='magasinlog',
            name='emp',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='magasinlog',
            name='prix',
            field=models.DecimalField(decimal_places=2, max_digits=15, null=True),
        ),
        migrations.AddField(
            model_name='magasinlog',
            name='qte',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='magasinlog',
            name='ref',
            field=models.CharField(db_index=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='magasinlog',
            name='slug',
            field=models.SlugField(default='code', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='magasinlog',
            name='umesure',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='magasinlog',
            name='valeur',
            field=models.DecimalField(decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='magasinlog',
            name='art_id',
            field=models.IntegerField(db_index=True),
        ),
    ]
