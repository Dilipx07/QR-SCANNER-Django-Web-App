from django.shortcuts import render

from django.shortcuts import render, redirect, HttpResponse
# from . import views
from .models import *
from django.contrib import messages
from django.contrib.auth import authenticate, logout
from django.template import loader
from Login.models import *


#Login Starts#  
def login(request):
    template = loader.get_template('Login/login.html')
    context = {
    }
    return HttpResponse(template.render(context,request))
#Login Ends# 

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
        
# for checking login credentials
def LoginAuth(request):
    if request.method == 'POST':
        login_user = request.POST.get('username')
        login_pass = request.POST.get('password')
        user_id = qr_scanner_login.objects.filter(qr_scanned_name = login_user)
        user = authenticate(request, userid=login_user)

        if user_id.exists():
            for usid in user_id:
                if login_pass==usid.qr_scanned_password:
                    request.session['User_Name'] = usid.qr_scanned_name
                    request.session['Login_id'] = login_user
                    request.session['Dashboard'] = 'QR-Dashboard'
                    return redirect('Cylinder-Stock-Dashboard')
                else:
                    messages.error(request, 'Invalid Username / Password')
        else:
            messages.error(request, 'Invalid Username / Password')
        return redirect('/Login')