from django.urls import path
from . import views

urlpatterns = [
    path('Dashboard',views.cylinder_stock_dashboard,name='Cylinder-Stock-Dashboard'),

    # Cylinder master
    path('Cylinder-List',views.cylinder_master,name='Cylinder-List'),

    # Cylinder Vendor Master
    path('Cylinder-Vendors',views.cylinder_vendor_master,name='Cylinder-Vendors'),

    # Cylinder Stocking In / Inwarding
    path('Cylinder-Stocking-In',views.cylinder_stock_in,name='Cylinder-Stocking-In'),

    # Cylinder Stocking Out / Outwarding
    path('Cylinder-Stocking-Out',views.cylinder_stock_out,name='Cylinder-Stocking-Out'),

    # Cylinder Inward
    path('Cylinder-Inward-Form',views.cylinder_inward_form,name='Cylinder-Inward-Form'),
    path('Cylinder-Inward-Submit',views.cylinder_inward_submit,name='Cylinder-Inward-Submit'),

    # Cylinder Inward Remove
    path('Cylinder-Inward-Remove',views.cylinder_inward_remove,name='Cylinder-Inward-Remove'),
    
    # Cylinder Outward
    path('Cylinder-Outward-Form',views.cylinder_outward_form,name='Cylinder-Outward-Form'),
    path('Cylinder-Outward-Submit',views.cylinder_outward_submit,name='Cylinder-Outward-Submit'),

    # Cylinder Outward QR Check
    path('Cylinder-Outward-Check',views.cylinder_master_outward_qr_check,name='Cylinder-Outward-Check'),
    path('Cylinder-Inward-Check',views.cylinder_master_inward_qr_check,name='Cylinder-Inward-Check'),

    # Cylinder Inward / Outward History Table
    path('Cylinder-Inward-Outward-History',views.cylinder_inward_outward_history_table,name='Cylinder-Inward-Outward-History'),

    # Cylinder Inward / Outward History Table
    path('Cylinder-Inward-Outward-History-Submit',views.cylinder_inward_outward_history_submit,name='Cylinder-Inward-Outward-History-Submit'),
]