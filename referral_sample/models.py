from django.db import models


class Referral(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    token = models.CharField(blank=True, null=True, max_length=512)