from uuid import uuid4

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.http import urlencode


def random_token():
    return uuid4().hex


class Referral(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    token = models.CharField(default=random_token, max_length=32, db_index=True)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    referral = models.OneToOneField(Referral, null=True, on_delete=models.CASCADE)
    people_invited = models.PositiveIntegerField(default=0)
    balance = models.PositiveIntegerField(default=0)

    def update_referral(self, ref_token):
        fields = ['referral']
        if ref_token:
            ref = Referral.objects.filter(token=ref_token)
            if ref.exists():
                ref = ref.first()
                self.balance = settings.INVITEE_REWARD
                ref.profile.reward_inviter()
                fields.append('balance')
        self.referral = Referral.objects.create()
        self.save(update_fields=fields)

    def reward_inviter(self):
        self.people_invited += 1
        fields = ['people_invited']
        if self.people_invited == settings.INVITER_TARGET_COUNT:
            self.people_invited = 0
            self.balance += settings.INVITER_REWARD
            fields.append('balance')
        self.save(update_fields=fields)

    @property
    def referral_url(self):
        return reverse('signup') + '?' + urlencode({'ref': self.referral.token})


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()
