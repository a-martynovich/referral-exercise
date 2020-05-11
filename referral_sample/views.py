import os

from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.views.generic import TemplateView

from .models import Referral


class RootView(LoginRequiredMixin, TemplateView):
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
        if 'form' not in ctx:
            ctx['form'] = UserCreationForm()
        return ctx

    def post(self, request, *args, **kwargs):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        else:
            return self.render_to_response(self.get_context_data(form=form))


class SignInView(LoginView):
    template_name = 'login.html'


class SignOutView(LogoutView):
    template_name = 'logout.html'
