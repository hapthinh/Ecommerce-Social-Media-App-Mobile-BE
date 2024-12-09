from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Account, Role, User

@receiver(post_save, sender=User)
def create_account_for_new_user(sender, instance, created, **kwargs):
    if created:
        user_role = Role.objects.get(role_name='User')
        Account.objects.create(user=instance, role=user_role)


@receiver(post_save, sender=User)
def save_account_for_user(sender, instance, **kwargs):
    instance.account.save()
