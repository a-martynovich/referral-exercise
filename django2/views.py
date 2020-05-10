import os

from django.conf import settings
from django.views.generic import TemplateView


class RootView(TemplateView):
    # model = Device
    template_name = 'root.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['db_info'] = settings.DATABASES
        ctx['env'] = os.environ
        return ctx
