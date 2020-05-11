from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Referral(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    token = models.CharField(blank=True, null=True, max_length=512)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    referral = models.OneToOneField(Referral, null=True, on_delete=models.CASCADE)
    balance = models.PositiveIntegerField(default=0)

    def update_referral(self, ref_token):
        self.balance = 10
        self.save(update_fields=['balance'])


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()
