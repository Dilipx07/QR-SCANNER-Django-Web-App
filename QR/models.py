from django.db import models
from .models import *

class Cylinder_Type_Master(models.Model):
    cylinder_type_id = models.BigAutoField(primary_key=True,unique=True)
    cylinder_gas_type = models.CharField(null=False,unique=True)

class Gas_Cylinder_Vendors_Master(models.Model):
    gas_cylinder_vendor_id = models.BigAutoField(primary_key=True,unique=True)
    gas_cylinder_vendor_name = models.CharField(unique=True,null=False)

class Cylinder_Inward_Details(models.Model):
    cylinder_inward_id = models.BigAutoField(primary_key=True,unique=True)
    cylinder_po_no = models.CharField()
    cylinder_po_Date = models.DateField()
    cylinder_GRN_no= models.CharField(unique=True)
    cylinder_GRN_Date = models.DateField()
    cylinder_Invoice_DC_no = models.CharField(unique=True)
    cylinder_description = models.CharField()

class Cylinder_Outward_Details(models.Model):
    cylinder_outward_id = models.BigAutoField(primary_key=True,unique=True)
    cylinder_return_DC = models.CharField(unique=True)
    cylinder_remarks = models.CharField(null=True)

# Cyliner Store.
class Cylinder_Store(models.Model):
    cylinder_db_id = models.BigAutoField(primary_key=True,unique=True)
    cylinder_sl_r_qr_no = models.CharField()
    cylinder_vendor_name = models.ForeignKey(Gas_Cylinder_Vendors_Master,on_delete=models.SET,default=None)
    cylinder_gas_type = models.ForeignKey(Cylinder_Type_Master,on_delete=models.SET,default=None)
    cylinder_scanned_r_submitted_date = models.DateTimeField(default=None,null=True)
    cylinder_scanned_r_submitted_by = models.CharField(max_length=300)
    cylinder_Inward = models.BooleanField(default=False)
    cylinder_Inward_Date = models.DateTimeField(null=True)
    cylinder_Outward = models.BooleanField(default=False)
    cylinder_Outward_Date = models.DateTimeField(null=True)
    cylinder_stocked_in = models.BooleanField(default=False)
    cylinder_stocked_in_Date = models.DateTimeField(null=True)
    cylinder_stock_out = models.BooleanField(default=False)
    cylinder_stock_out_Date = models.DateTimeField(null=True)
    Cylinder_Inward_Table = models.ForeignKey(Cylinder_Inward_Details,on_delete=models.SET,null=True)
    Cylinder_Outward_Table = models.ForeignKey(Cylinder_Outward_Details,on_delete=models.SET,null=True)
