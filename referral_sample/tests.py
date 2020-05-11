from django.test import TestCase
from django.urls import reverse
from django.conf import settings

from .models import Profile


class SignupTests(TestCase):
    def setUp(self):
        pass

    def test_signup_simple(self):
        """
        Usual workflow: sign up with a good name and password should succeed.
        """
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
        """
        When signing up with a referral link, both the inviter's and invitee's referral status should update.
        The inviter should increase its people_invited count, and the invitee should get his reward.
        """
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
        """
        Wrong referral link should not lead to failure.
        """
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
        """
        When INVITER_TARGET_COUNT new users sign up using inviter's referral link the inviter should get his reward.
        """
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
        """
        Short, common, numeric passwords are invalid.
        """
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
        """
        Signing up with a username which already exists is an error.
        """
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