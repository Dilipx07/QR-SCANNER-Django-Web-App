import logging

from django.conf import settings
from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from django.contrib.auth import logout
from django.middleware.csrf import rotate_token
from django.template import loader
from Login.models import qr_scanner_login

logger = logging.getLogger(__name__)


def login(request):
    if request.session.get('Login_id'):
        return redirect('Cylinder-Stock-Dashboard')
    template = loader.get_template('Login/login.html')
    context = {
    }
    return HttpResponse(template.render(context,request))

# for rendering login page.
def Login(request):
    if 'Dashboard' in request.session:
        if request.session['Dashboard']!='':
            dash = str(request.session['Dashboard'])
            return redirect(dash)
        
    request.session['User_Name'] = ''
    request.session['Login_id'] = ''
    request.session.flush()
    request.session.clear_expired()
    request.session.set_expiry(0)
    context = {
        'dashboard': True,
        'dash_content': True,
    }
    return HttpResponse(render(request,'Login/login.html',{'context':context}))

def Logout(request):
    logout(request)
    request.session['User_Name'] = ''
    request.session['Login_id'] = ''
    request.session.flush()
    request.session.clear_expired()
    request.session.set_expiry(0)
    return redirect('Login')
        
def LoginAuth(request):
    try:
        if request.method != 'POST':
            return redirect('Login')

        login_user = (request.POST.get('username') or '').strip()
        login_pass = request.POST.get('password') or ''
        user = qr_scanner_login.objects.filter(qr_scanned_name=login_user).first()

        if user and user.check_password(login_pass):
            request.session.cycle_key()
            rotate_token(request)
            request.session['User_Name'] = user.qr_scanned_name
            request.session['Login_id'] = user.qr_scanned_name
            request.session['Dashboard'] = 'QR-Dashboard'
            now = int(__import__('time').time())
            request.session['auth_session_started_at'] = now
            request.session['auth_last_activity'] = now
            request.session.set_expiry(settings.SESSION_COOKIE_AGE)
            return redirect('Cylinder-Stock-Dashboard')

        messages.error(request, 'Invalid Username / Password')
        return redirect('Login')
    except Exception:
        logger.exception('Login authentication failed with an unexpected error')
        raise
