from django.db import models
from django.core.validators import EmailValidator, RegexValidator


# Create your models here.
class Fournisseur(models.Model):
    fourrnis_id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=200, unique=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    fourniture = models.CharField(max_length=255, blank=True)

    code_postal = models.IntegerField(null=True, blank=True)
    pays = models.CharField(max_length=255, blank=True)

    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message='Enter a valid phone number')
    telephone = models.CharField(max_length=20, validators=[phone_regex], blank=True)

    fax = models.CharField(max_length=100, null=True)
    email = models.EmailField(unique=True, blank=True, validators=[EmailValidator])
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ('fourrnis_id', 'nom')

    def __str__(self):
        return '{}: {}'.format(self.nom, self.address)
