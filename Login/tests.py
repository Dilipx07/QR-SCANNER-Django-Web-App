import time

from django.contrib.auth.hashers import identify_hasher
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import qr_scanner_login


@override_settings(SECURE_SSL_REDIRECT=False)
class LoginAuthenticationTests(TestCase):
    def setUp(self):
        self.user = qr_scanner_login(qr_scanned_name='scanner-user')
        self.user.set_password('StrongPass123!')
        self.user.save()

    def test_passwords_are_hashed_and_verified(self):
        identify_hasher(self.user.qr_scanned_password)

        self.assertTrue(self.user.check_password('StrongPass123!'))
        self.assertFalse(self.user.check_password('wrong-password'))
        self.assertNotEqual(self.user.qr_scanned_password, 'StrongPass123!')

    def test_successful_login_sets_secure_session_state(self):
        response = self.client.post(reverse('Login-Auth'), {
            'username': 'scanner-user',
            'password': 'StrongPass123!',
        })

        self.assertRedirects(response, reverse('Cylinder-Stock-Dashboard'), fetch_redirect_response=False)
        self.assertEqual(self.client.session['Login_id'], 'scanner-user')
        self.assertIn('auth_session_started_at', self.client.session)
        self.assertIn('auth_last_activity', self.client.session)

    def test_invalid_login_does_not_create_session(self):
        response = self.client.post(reverse('Login-Auth'), {
            'username': 'scanner-user',
            'password': 'wrong-password',
        })

        self.assertRedirects(response, reverse('Login'))
        self.assertNotIn('Login_id', self.client.session)


@override_settings(SECURE_SSL_REDIRECT=False)
class SessionExpiryMiddlewareTests(TestCase):
    def test_protected_qr_route_requires_login_session(self):
        response = self.client.get(reverse('Cylinder-Stock-Dashboard'))

        self.assertRedirects(response, reverse('Login'), fetch_redirect_response=False)

    @override_settings(SESSION_IDLE_TIMEOUT_SECONDS=1, SESSION_COOKIE_AGE=604800)
    def test_idle_session_auto_logs_out_and_redirects(self):
        session = self.client.session
        session['Login_id'] = 'scanner-user'
        session['User_Name'] = 'scanner-user'
        session['auth_session_started_at'] = int(time.time())
        session['auth_last_activity'] = int(time.time()) - 5
        session.save()

        response = self.client.get(reverse('Cylinder-Stock-Dashboard'))

        self.assertRedirects(response, reverse('Login'), fetch_redirect_response=False)
        self.assertNotIn('Login_id', self.client.session)

    @override_settings(SESSION_IDLE_TIMEOUT_SECONDS=1800, SESSION_COOKIE_AGE=1)
    def test_absolute_session_expiry_logs_out_and_redirects(self):
        session = self.client.session
        session['Login_id'] = 'scanner-user'
        session['User_Name'] = 'scanner-user'
        session['auth_session_started_at'] = int(time.time()) - 5
        session['auth_last_activity'] = int(time.time())
        session.save()

        response = self.client.get(reverse('Cylinder-Stock-Dashboard'))

        self.assertRedirects(response, reverse('Login'), fetch_redirect_response=False)
        self.assertNotIn('Login_id', self.client.session)
