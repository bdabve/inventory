from django.db import models
from django.conf import settings


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    poste_travaille = models.CharField(max_length=100)
    groupe_choice = (('admin', 'Admin'), ('other', 'Other'),)
    groupe = models.CharField(max_length=10, choices=groupe_choice)

    def __str__(self):
        return 'Profile user: {}, poste_travaille: {}'.format(self.user.username, self.poste_travaille)
