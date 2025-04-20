from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Article, MagasinLog
from django.utils.timezone import now


@receiver(post_save, sender=Article)
def log_article_save(sender, instance, created, **kwargs):
    operation = 'Création' if created else 'Modification'
    MagasinLog.objects.create(
        log_date=now(),
        operation=operation,
        art_id=instance.art_id,
        code=instance.code,
        slug=instance.code.lower(),
        designation=instance.designation,
        ref=instance.ref,
        umesure=instance.umesure,
        emp=instance.emp
    )


@receiver(post_delete, sender=Article)
def log_article_delete(sender, instance, **kwargs):
    MagasinLog.objects.create(
        log_date=now(),
        operation='Suppression',
        art_id=instance.art_id,
        code=instance.code,
        slug=instance.code.lower(),
        designation=instance.designation,
        ref=instance.ref,
        umesure=instance.umesure,
        emp=instance.emp
    )
