from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.conf import settings

from .models import Profile


class SignupTests(TestCase):
    def setUp(self):
        pass

    def test_signup_simple(self):
        response = self.client.post(reverse('signup'), {
            'username': 'user0',
            'password1': 'Password123!',
            'password2': 'Password123!',
        }, follow=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('root'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hello user0!')
        self.assertEqual(response.context['balance'], 0)

    def test_signup_referral(self):
        response = self.client.post(reverse('signup'), {
            'username': 'user0',
            'password1': 'Password123!',
            'password2': 'Password123!',
        }, follow=True)
        self.assertEqual(response.status_code, 200)

        p = Profile.objects.get(user__username='user0')
        response = self.client.post(p.referral_url, {
            'username': 'user1',
            'password1': 'Password123!',
            'password2': 'Password123!',
        })
        self.assertEqual(response.status_code, 302)
        p.refresh_from_db()
        self.assertEqual(p.people_invited, 1)

    def test_signup_wrong_referral(self):
        response = self.client.post(reverse('signup'), {
            'username': 'user0',
            'password1': 'Password123!',
            'password2': 'Password123!',
        }, follow=True)
        self.assertEqual(response.status_code, 200)

        p = Profile.objects.get(user__username='user0')
        response = self.client.post(p.referral_url + 'abc', {
            'username': 'user1',
            'password1': 'Password123!',
            'password2': 'Password123!',
        })
        self.assertEqual(response.status_code, 302)
        p.refresh_from_db()
        self.assertEqual(p.people_invited, 0)

    def test_invite_reward(self):
        response = self.client.post(reverse('signup'), {
            'username': 'user',
            'password1': 'Password123!',
            'password2': 'Password123!',
        }, follow=True)
        self.assertEqual(response.status_code, 200)

        p = Profile.objects.get(user__username='user')
        for i in range(settings.INVITER_TARGET_COUNT):
            response = self.client.post(p.referral_url, {
                'username': f'user{i}',
                'password1': 'Password123!',
                'password2': 'Password123!',
            })
            self.assertEqual(response.status_code, 302)
            response = self.client.get(reverse('root'))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context['balance'], settings.INVITEE_REWARD)

        p.refresh_from_db()
        self.assertEqual(p.people_invited, 0)
        self.assertEqual(p.balance, settings.INVITER_REWARD)


class SignupValidationTests(TestCase):
    def setUp(self):
        self.url = reverse('signup')

    def test_weak_pass(self):
        response = self.client.post(self.url, {
            'username': f'user',
            'password1': '123',
            'password2': '123',
        })
        self.assertEqual(response.status_code, 200)

        form = response.context[0]['form']
        self.assertFalse(form.is_valid())
        self.assertDictEqual(form.errors, {
            'password2': ['This password is too short. It must contain at least 8 characters.',
                          'This password is too common.', 'This password is entirely numeric.']})

    def test_username_exists(self):
        response = self.client.post(self.url, {
            'username': f'user',
            'password1': 'Password123!',
            'password2': 'Password123!',
        })
        self.assertEqual(response.status_code, 302)

        response = self.client.post(self.url, {
            'username': f'user',
            'password1': 'Password123!',
            'password2': 'Password123!',
        })
        self.assertEqual(response.status_code, 200)

        form = response.context[0]['form']
        self.assertFalse(form.is_valid())
        self.assertDictEqual(form.errors, {'username': ['A user with that username already exists.']})