# Generated by Django 2.2.5 on 2020-07-23 10:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('magasin', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MagasinLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('log_date', models.DateTimeField()),
                ('operation', models.CharField(choices=[('nouveaux', 'Nouveaux'), ('modification', 'Modif'), ('suppression', 'Suppression')], max_length=10)),
                ('art_id', models.IntegerField(db_index=True)),
                ('slug', models.SlugField(max_length=200)),
                ('designation', models.CharField(db_index=True, max_length=255, null=True)),
                ('code', models.CharField(db_index=True, max_length=100, null=True)),
                ('ref', models.CharField(db_index=True, max_length=255, null=True)),
                ('umesure', models.CharField(max_length=50, null=True)),
                ('emp', models.CharField(max_length=50, null=True)),
                ('qte', models.PositiveIntegerField(null=True)),
                ('prix', models.DecimalField(decimal_places=2, max_digits=15, null=True)),
                ('valeur', models.DecimalField(decimal_places=2, max_digits=20, null=True)),
            ],
            options={
                'ordering': ('log_date', 'slug'),
            },
        ),
        migrations.CreateModel(
            name='Movement',
            fields=[
                ('movement_id', models.AutoField(primary_key=True, serialize=False)),
                ('art_id', models.IntegerField(db_index=True)),
                ('movement_date', models.DateTimeField()),
                ('slug', models.SlugField(max_length=200)),
                ('designation', models.CharField(db_index=True, max_length=255, null=True)),
                ('code', models.CharField(db_index=True, max_length=100, null=True)),
                ('movement', models.CharField(choices=[('entree', 'Entree'), ('sortie', 'Sortie')], max_length=10)),
                ('qte', models.PositiveIntegerField(null=True)),
                ('prix', models.DecimalField(decimal_places=2, max_digits=15, null=True)),
                ('valeur', models.DecimalField(decimal_places=2, max_digits=20, null=True)),
            ],
            options={
                'ordering': ('movement_date', 'code'),
            },
        ),
    ]
