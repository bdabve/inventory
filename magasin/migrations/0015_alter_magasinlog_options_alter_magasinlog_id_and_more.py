# Generated by Django 4.0 on 2025-04-20 21:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('magasin', '0014_command_status'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='magasinlog',
            options={'ordering': ('-log_date', 'slug')},
        ),
        migrations.AlterField(
            model_name='magasinlog',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='movement',
            name='movement',
            field=models.CharField(choices=[('entree', 'Entree'), ('sortie', 'Sortie'), ('initial', 'Initial')], max_length=10),
        ),
    ]
