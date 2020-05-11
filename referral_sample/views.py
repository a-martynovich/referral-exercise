from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import urlencode
from django.views.generic import TemplateView


class RootView(LoginRequiredMixin, TemplateView):
    template_name = 'root.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ref_url = self.request.build_absolute_uri(reverse('signup')) + '?' + urlencode(
            {'ref': self.request.user.profile.referral.token})
        ctx['referral_link'] = ref_url
        ctx['balance'] = self.request.user.profile.balance
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
            new_user = form.save()
            ref = request.GET.get('ref')
            if ref:
                new_user.profile.update_referral(ref)
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('root')
        else:
            return self.render_to_response(self.get_context_data(form=form))


class SignInView(LoginView):
    template_name = 'login.html'


class SignOutView(LogoutView):
    template_name = 'logout.html'
