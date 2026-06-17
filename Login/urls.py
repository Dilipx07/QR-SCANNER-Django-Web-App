from django.urls import path
from . import views

urlpatterns = [
    path('',views.login,name='Login'),
    path('Login',views.login,name='Login'),
    path('Login-Auth',views.LoginAuth,name='Login-Auth'),

    #Logout
    path('Logout',views.Logout,name='Logout'),
]