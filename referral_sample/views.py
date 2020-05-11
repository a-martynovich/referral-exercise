import os

from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect
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


class SignupView(TemplateView):
    template_name = 'signup.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['form'] = UserCreationForm()
        return ctx

    # def get(self, request, *args, **kwargs):
    #     return super().get(request, *args, **kwargs)
    #
    def post(self, request, *args, **kwargs):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('root')
        else:
            return self.render_to_response(self.get_context_data(form=form))


class LoginView(TemplateView):
    pass
