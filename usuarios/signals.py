from django.db.models.signals import post_save
from django.dispatch import receiver
from allauth.account.models import EmailAddress
from .models import CustomUser

@receiver(post_save, sender=EmailAddress)
def update_email_verified(sender, instance, **kwargs):
    user = instance.user
    if isinstance(user, CustomUser):
        user.email_verified = instance.verified
        user.save()