from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.generic import TemplateView


class AcceptJsonMixin:
    """
    A simple mixin providing one method telling whether the request was made with Accept: application/json
    """
    def is_ajax(self):
        return self.request.META.get('HTTP_ACCEPT') == 'application/json'


class RootView(LoginRequiredMixin, AcceptJsonMixin, TemplateView):
    template_name = 'root.html'

    def _update_context(self, ctx):
        ctx['referral_link'] = self.request.build_absolute_uri(self.request.user.profile.referral_url)
        ctx['balance'] = self.request.user.profile.balance
        return ctx

    def handle_no_permission(self):
        """
        Overridden from LoginRequiredMixin. Returns 401 for an AJAX request if unauthorized.
        """
        if self.is_ajax():
            return JsonResponse({'error': 'unauthorized'}, status=401)
        return super().handle_no_permission()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        return self._update_context(ctx)

    def get(self, request, *args, **kwargs):
        if self.is_ajax():
            return JsonResponse(self._update_context({}))
        else:
            return super().get(request, *args, **kwargs)


class SignupView(AcceptJsonMixin, TemplateView):
    template_name = 'signup.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if 'form' not in ctx:
            ctx['form'] = UserCreationForm()
        return ctx

    def post(self, request, *args, **kwargs):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # Save the new user, update its referral status, login and redirect to root page.
            new_user = form.save()
            ref = request.GET.get('ref')
            new_user.profile.update_referral(ref)
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            if self.is_ajax():
                return JsonResponse({})
            return redirect('root')
        else:
            if self.is_ajax():
                return JsonResponse(form.errors, status=400)
            return self.render_to_response(self.get_context_data(form=form))


class SignInView(AcceptJsonMixin, LoginView):
    template_name = 'login.html'

    def form_invalid(self, form):
        """
        Overridden from LoginView to return 400 for AJAX requests.
        """
        response = super().form_invalid(form)
        if self.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        """
        Overridden from LoginView to return empty response for AJAX requests.
        """
        response = super().form_valid(form)
        if self.is_ajax():
            return JsonResponse({})
        else:
            return response


class SignOutView(AcceptJsonMixin, LogoutView):
    template_name = 'logout.html'

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        if self.is_ajax():
            return JsonResponse({}, status=response.status_code)
        return response
