import os

from django.conf import settings
from django.views.generic import TemplateView

from .models import Referral


class RootView(TemplateView):
    template_name = 'root.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['db_info'] = settings.DATABASES
        ctx['env'] = os.environ

        ctx['refs'] = Referral.objects.all()
        return ctx
