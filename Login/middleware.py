import time

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.http import JsonResponse
from django.shortcuts import redirect


class SessionExpiryMiddleware:
    """Protect QR routes and expire inactive custom-login sessions."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/QR/'):
            if not request.session.get('Login_id'):
                return self._unauthorized_response(request)

            now = int(time.time())
            session_started_at = int(request.session.get('auth_session_started_at', now))
            last_activity = int(request.session.get('auth_last_activity', now))
            idle_timeout = getattr(settings, 'SESSION_IDLE_TIMEOUT_SECONDS', 1800)
            absolute_timeout = settings.SESSION_COOKIE_AGE
            if now - session_started_at > absolute_timeout or now - last_activity > idle_timeout:
                logout(request)
                request.session.flush()
                messages.warning(request, 'Your session has expired. Please login again.')
                return self._unauthorized_response(request)

            request.session['auth_last_activity'] = now
            request.session.set_expiry(settings.SESSION_COOKIE_AGE)

        return self.get_response(request)

    def _unauthorized_response(self, request):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'detail': 'Session expired. Please login again.'}, status=401)
        return redirect('Login')
