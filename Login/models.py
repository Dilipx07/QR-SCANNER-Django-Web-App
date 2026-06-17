from django.db import models
from .models import *

# Create your models here.
class qr_scanner_login(models.Model):
    qr_scanner_id = models.BigAutoField(primary_key=True,unique=True)
    qr_scanned_name = models.CharField(max_length=150,null=True)
    qr_scanned_password = models.CharField(max_length=150,null=True)