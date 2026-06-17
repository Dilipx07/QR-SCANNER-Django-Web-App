from django.shortcuts import render

# Create your views here.
from django.views import View
import json
from django.http import JsonResponse, Http404
from django.contrib.auth.models import User
from django.shortcuts import HttpResponse 
from django.shortcuts import redirect, reverse
import random
from django.apps import apps
# The following libraries is to return a variable to html which contains some information
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import loader
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.core import serializers
from datetime import datetime, time, timedelta
import ast
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from dateparser import parse
from django.db.models import Q
from django.core.mail import send_mail
import pytz
import calendar
import os
from QR.models import *
from django.utils import timezone

def current_ist_datetime():
    utc_datetime = timezone.now()
    ist = pytz.timezone('Asia/Kolkata')
    ist_datetime = utc_datetime.astimezone(ist)
    return ist_datetime

def cylinder_vendor_master(request):
    if request.method == 'POST':
        vendor_id = int(request.POST.get('vendor_id'))
        vendor_name = request.POST.get('vendor_name')
        vendor_details = Gas_Cylinder_Vendors_Master.objects.filter(gas_cylinder_vendor_id=vendor_id, gas_cylinder_vendor_name=vendor_name).first()
        cylinder_filter = {
            "cylinder_vendor_name":vendor_details,
            "cylinder_Inward": True,
            "cylinder_Outward": False,
            "cylinder_stocked_in": True,
            "cylinder_stock_out": False
        }
        cylinder_det = Cylinder_Store.objects.complex_filter(cylinder_filter).values('cylinder_db_id', 'cylinder_sl_r_qr_no')
        cylinder_list = list(cylinder_det)
        return JsonResponse(data=cylinder_list,safe=False,status=200)

def cylinder_master(request):
    if request.method == 'POST':
        cylinder_id = int(request.POST.get('cylinder_id'))
        cylinder_sl_no = request.POST.get('cylinder_sl_no')
        cylinder_det = Cylinder_Store.objects.filter(cylinder_db_id=cylinder_id, cylinder_sl_r_qr_no=cylinder_sl_no).get()
        cylinder_type = cylinder_det.cylinder_gas_type.cylinder_gas_type
        return JsonResponse(data=cylinder_type,safe=False,status=200)

def cylinder_master_outward_qr_check(request):
    if request.method == 'POST':
        cylinder_sl_no = request.POST.get('qr_sl_number')
        cylinder_filter = {
            'cylinder_sl_r_qr_no': cylinder_sl_no,
            "cylinder_Inward": True,
            "cylinder_Outward": False,
            "cylinder_stocked_in": True,
            "cylinder_stock_out": False
        }
        cylinder_det = Cylinder_Store.objects.complex_filter(cylinder_filter)
        if cylinder_det.values():
            cylinder_type = cylinder_det.get().cylinder_gas_type.cylinder_gas_type
            cylinder_type_id = cylinder_det.get().cylinder_gas_type.cylinder_type_id
            vendor_name = cylinder_det.get().cylinder_vendor_name.gas_cylinder_vendor_name
            vendor_id = cylinder_det.get().cylinder_vendor_name.gas_cylinder_vendor_id
            cylinder_id = cylinder_det.get().cylinder_db_id
            context = {
                'cylinder_type_id':cylinder_type_id,
                'cylinder_type':cylinder_type,
                'vendor_name': vendor_name,
                'vendor_id': vendor_id,
                'cylinder_id':cylinder_id
            }
            return JsonResponse(data=context,safe=False,status=200)
        else:
            raise Http404("Invalid Cylinder Serial Number!")

def cylinder_master_inward_qr_check(request):
    if request.method == 'POST':
        cylinder_sl_no = request.POST.get('qr_sl_number')
        cylinder_in_stock_filter = {
            'cylinder_sl_r_qr_no': cylinder_sl_no,
            "cylinder_Inward": True,
            "cylinder_Outward": False,
            "cylinder_stocked_in": True,
            "cylinder_stock_out": False
        }
        cylinder_inward_filter = {
            'cylinder_sl_r_qr_no': cylinder_sl_no,
            "cylinder_Inward": True,
            "cylinder_Outward": False,
            "cylinder_stocked_in": False,
            "cylinder_stock_out": False
        }
        cylinder_in_stock_det = Cylinder_Store.objects.complex_filter(cylinder_in_stock_filter)
        cylinder_inward_det = Cylinder_Store.objects.complex_filter(cylinder_inward_filter)
        if cylinder_in_stock_det.values():
            raise Http404("Cylinder is Already Stocked!")
        elif cylinder_inward_det.values():
            raise Http404("Cylinder is in Inward Process!")
        else:
            context = ''
            return JsonResponse(data=context,safe=False,status=200)
        
def cylinder_stock_dashboard(request):
    template = loader.get_template('QR/qr-dashboard-content.html')
    gas_cylinder_vendors = Gas_Cylinder_Vendors_Master.objects.order_by('gas_cylinder_vendor_id')
    cylinder_stock_filter = {
        'cylinder_Inward': True,
        'cylinder_Outward': False,
        'cylinder_stocked_in': True,
        'cylinder_stock_out': False
    }
    gas_cylinder_type = Cylinder_Type_Master.objects.order_by('cylinder_gas_type')
    gasCylinder_stock = {}
    for gasTypes in gas_cylinder_type:
        cylinder_stock_filter['cylinder_gas_type'] = gasTypes.cylinder_type_id
        count = Cylinder_Store.objects.complex_filter(cylinder_stock_filter).order_by('-cylinder_gas_type').count()
        gasCylinder_stock[f'{gasTypes.cylinder_gas_type}'] = count
        pass
    context = {
        'tdate': current_ist_datetime(),
        'dashboard_content': True,
        'gas_cylinder_type': gas_cylinder_type,
        'gas_cylinder_vendors':gas_cylinder_vendors,
        'stock':{'gasCylinder_stock':gasCylinder_stock},
    }
    print(context)
    return HttpResponse(template.render(context,request))

def cylinder_inward_form(request):
    template = loader.get_template('QR/Cylinder-Inward/cylinder-inward-form.html')
    cylinder_inward_filter = {
        'cylinder_Inward' : True,
        'cylinder_Outward' : False,
        'cylinder_stocked_in': False,
        'cylinder_stock_out': False
    }
    cylinder_inward_stock = Cylinder_Store.objects.order_by('-cylinder_db_id').complex_filter(cylinder_inward_filter)
    gas_cylinder_type = Cylinder_Type_Master.objects.order_by('cylinder_type_id')
    gas_cylinder_vendors = Gas_Cylinder_Vendors_Master.objects.order_by('gas_cylinder_vendor_id')
    context = {
        'cylinder_inward_form': True,
        'cylinder_inward_stock': cylinder_inward_stock,
        'gas_cylinder_type': gas_cylinder_type,
        'gas_cylinder_vendors':gas_cylinder_vendors,
    }
    return HttpResponse(template.render(context,request))

def cylinder_inward_submit(request):
    template = loader.get_template('QR/Cylinder-Inward/cylinder-inward-form.html')
    po_no = request.GET.get('po_number') or request.POST.get('po_number')
    po_date = request.GET.get('po_date') or request.POST.get('po_date')
    grn_no = request.GET.get('grn_number') or request.POST.get('grn_number')
    grn_date = request.GET.get('grn_date') or request.POST.get('grn_date')
    invoice_r_dc_no = request.GET.get('inv_dc_no') or request.POST.get('inv_dc_no')
    description = request.GET.get('inward_description') or request.POST.get('inward_description')
    vendor_id = request.GET.get('cylinder_gas_vendor') or request.POST.get('cylinder_gas_vendor')
    cylinder_inward_filter = {
        'cylinder_Inward' : True,
        'cylinder_Outward' : False,
        'cylinder_stocked_in': False,
        'cylinder_stock_out': False
    }
    cylinder_inward_stock = Cylinder_Store.objects.order_by('-cylinder_db_id').complex_filter(cylinder_inward_filter)
    gas_cylinder_type = Cylinder_Type_Master.objects.order_by('cylinder_type_id')
    gas_cylinder_vendors = Gas_Cylinder_Vendors_Master.objects.order_by('gas_cylinder_vendor_id')
    context = {
        'cylinder_inward_form': True,
        'cylinder_inward_stock': cylinder_inward_stock,
        'gas_cylinder_type': gas_cylinder_type,
        'gas_cylinder_vendors':gas_cylinder_vendors,
    }
    def setVar():
        context['po_no'] = po_no
        context['po_date'] = po_date
        context['grn_no'] = grn_no
        context['grn_date'] = grn_date
        context['invoice_r_dc_no'] = invoice_r_dc_no
        context['description'] = description
        context['vendor_id'] = int(vendor_id)
        pass
    if request.method == 'POST':
        cylinder_inward_details_filter = {
            'cylinder_po_no': po_no,
            'cylinder_po_Date': po_date,
            'cylinder_GRN_no': grn_no,
            'cylinder_GRN_Date': grn_date,
            'cylinder_Invoice_DC_no': invoice_r_dc_no,
            'cylinder_description': description,
        }
        try:
            cylinderInwardTable = Cylinder_Inward_Details.objects.complex_filter(cylinder_inward_details_filter).get()
            qr_sl_number = request.POST.get('cylinder_sl_no') or request.POST.get('qr_sl_number')
            vendor = Gas_Cylinder_Vendors_Master.objects.get(gas_cylinder_vendor_id = int(request.POST.get('cylinder_gas_vendor')))
            gas_cylinder_type = Cylinder_Type_Master.objects.get(cylinder_type_id = int(request.POST.get('cylinder_gas_type')))
            qr_scanned_by = request.session.get('Login_id')
            context['inward_table'] = True
            setVar()
            cylinder_inward_filter = {
                'cylinder_sl_r_qr_no': qr_sl_number,
                'cylinder_Inward' : True,
                'cylinder_Outward' : False,
                'cylinder_stocked_in': False,
                'cylinder_stock_out': False
            }
            cylinder_inward = Cylinder_Store.objects.complex_filter(cylinder_inward_filter)
            cylinder_inward_filter['cylinder_stocked_in'] = True
            cylinder_stocked_in = Cylinder_Store.objects.complex_filter(cylinder_inward_filter)
            cylinder_inward_filter['cylinder_stocked_in'] = True
            # cylinder_outward = Cylinder_Store.objects.complex_filter(cylinder_inward_filter)
            # cylinder_inward_filter['cylinder_stocked_in'] = True
            # cylinder_stock_out = Cylinder_Store.objects.complex_filter(cylinder_inward_filter)
            if not cylinder_inward.values():
                if not cylinder_stocked_in.values():
                    qr_scanner = Cylinder_Store()
                    qr_scanner.cylinder_sl_r_qr_no = qr_sl_number
                    qr_scanner.cylinder_vendor_name = vendor
                    qr_scanner.cylinder_gas_type = gas_cylinder_type
                    qr_scanner.cylinder_scanned_r_submitted_by = qr_scanned_by
                    qr_scanner.cylinder_scanned_r_submitted_date = current_ist_datetime()
                    qr_scanner.cylinder_Inward = True
                    qr_scanner.cylinder_Inward_Date = current_ist_datetime()
                    qr_scanner.Cylinder_Inward_Table = cylinderInwardTable
                    qr_scanner.save()
            return HttpResponse(template.render(context,request))
        except Exception as e:
            print(e)
            return HttpResponse(template.render(context,request))
    try:
        Inward_det = Cylinder_Inward_Details.objects
        Inward_det.update_or_create(
            cylinder_po_no = po_no,
            cylinder_po_Date = po_date,
            cylinder_GRN_no = grn_no,
            cylinder_GRN_Date = grn_date,
            cylinder_Invoice_DC_no = invoice_r_dc_no,
            cylinder_description = description
        )
        cylinder_inward_details_filter = {
            'cylinder_po_no': po_no,
            'cylinder_po_Date': po_date,
            'cylinder_GRN_no': grn_no,
            'cylinder_GRN_Date': grn_date,
            'cylinder_Invoice_DC_no': invoice_r_dc_no,
            'cylinder_description': description,
        }
        cylinderInwardTable = Cylinder_Inward_Details.objects.complex_filter(cylinder_inward_details_filter).get()
        cylinder_inward_stock = Cylinder_Store.objects.filter(Cylinder_Inward_Table = cylinderInwardTable)
        context['inward_table'] = True
        if cylinder_inward_stock.values():
            context['cylinder_inward_stock'] = cylinder_inward_stock
        else:
            context['cylinder_inward_stock'] = None
        setVar()
        return HttpResponse(template.render(context,request))
    except Exception as e:
        print('Error: Duplicate Key',e)
        if 'po_no' in str(e):
            context['error'] = 'PO Already Exists'
        elif 'GRN_no' in str(e):
            context['error'] = 'GRN Already Exists'
        elif 'Invoice_DC_no' in str(e):
            context['error'] = 'Invoice or DC Already Exists'
        setVar()
        return HttpResponse(template.render(context,request))

def cylinder_inward_remove(request):
    if request.method == 'POST':
        inward_selected = request.POST.getlist('selectedinward[]')
        for inward_c_id in inward_selected:
            Cylinder_Store.objects.filter(cylinder_db_id = inward_c_id).delete()
        return JsonResponse(data=True,safe=False,status=200)
    
def cylinder_stock_in(request):
    if request.method == 'POST':
        inward_selected = request.POST.getlist('selectedinward[]')
        for inward_c_id in inward_selected:
            qr_scanner = Cylinder_Store.objects.filter(cylinder_db_id = inward_c_id)
            qr_scanner.update(cylinder_stocked_in = True)
            qr_scanner.update(cylinder_stocked_in_Date = current_ist_datetime())
        return JsonResponse(data=True,safe=False,status=200)
    
def cylinder_outward_form(request):
    template = loader.get_template('QR/Cylinder-Outward/cylinder-outward-form.html')
    cylinder_outward_filter = {
        'cylinder_Inward' : True,
        'cylinder_Outward' : True,
        'cylinder_stocked_in': True,
        'cylinder_stock_out': False
    }
    cylinder_outward_stock = Cylinder_Store.objects.order_by('-cylinder_db_id').complex_filter(cylinder_outward_filter)
    gas_cylinder_vendors = Gas_Cylinder_Vendors_Master.objects.order_by('gas_cylinder_vendor_id')
    context = {
        'cylinder_outward_form': True,
        'cylinder_outward_stock': cylinder_outward_stock,
        'gas_cylinder_vendors':gas_cylinder_vendors,
    }
    return HttpResponse(template.render(context,request))

def cylinder_outward_submit(request):
    if request.method == 'POST':
        print(request.POST)
        cylinder_id = int(request.POST.get('cylinder_sl_no') or request.POST.get('qr_sl_no_id'))
        cylinder_gas_type = request.POST.get('cylinder_gas_type')
        cylinder_gas_vendor = int(request.POST.get('cylinder_gas_vendor'))
        cylinder_type_det = Cylinder_Type_Master.objects.get(cylinder_gas_type = cylinder_gas_type)
        cylinder_filter = {
            'cylinder_db_id': cylinder_id,
            'cylinder_gas_type':cylinder_type_det,
            'cylinder_vendor_name':cylinder_gas_vendor
        }
        cylinderInfo = Cylinder_Store.objects.complex_filter(cylinder_filter)
        cylinderInfo.update(cylinder_Outward = True)
        cylinderInfo.update(cylinder_Outward_Date = current_ist_datetime())
        return redirect('Cylinder-Outward-Form')

def cylinder_stock_out(request):
    if request.method == 'POST':
        print(request.POST)
        outwardSelected = request.POST.getlist('outwardSelected[]')
        return_dc_no = request.POST.get('return_dc_no')
        return_remarks = request.POST.get('return_remarks')
        outward_details = Cylinder_Outward_Details.objects.filter(cylinder_return_DC = return_dc_no)
        if not outward_details.values():
            Cylinder_Outward_Details.objects.update_or_create(
                cylinder_return_DC = return_dc_no,
                cylinder_remarks = return_remarks
            )
        print(outward_details)
        for outStockList in outwardSelected:
            cylinder_out = Cylinder_Store.objects.filter(cylinder_db_id = outStockList)
            cylinder_out.update(cylinder_stock_out = True)
            cylinder_out.update(cylinder_stock_out_Date = current_ist_datetime())
            cylinder_out.update(Cylinder_Outward_Table = outward_details.get())
        
        return JsonResponse(data=True,safe=False,status=200)
    
def cylinder_inward_outward_history_table(request):
    template = loader.get_template('QR/Cylinder-History/cylinder-history.html')
    gas_cylinder_vendors = Gas_Cylinder_Vendors_Master.objects.order_by('gas_cylinder_vendor_id')
    context = {
        'cylinder_inward_outward_history': True,
        'gas_cylinder_vendors':gas_cylinder_vendors,
    }
    return HttpResponse(template.render(context,request))

def cylinder_inward_outward_history_submit(request):
    template = loader.get_template('QR/Cylinder-History/cylinder-history.html')
    vendor_id = request.GET.get('cylinder_gas_vendor')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    gas_cylinder_vendors = Gas_Cylinder_Vendors_Master.objects.order_by('gas_cylinder_vendor_id')
    try:
        vendor_id = int(vendor_id)
        history_filter = {
            'cylinder_vendor_name': gas_cylinder_vendors.get(gas_cylinder_vendor_id = vendor_id)
        }
        cylinder_stock_history = Cylinder_Store.objects.complex_filter(history_filter).order_by('-cylinder_db_id')
        vendor_name = gas_cylinder_vendors.get(gas_cylinder_vendor_id = vendor_id).gas_cylinder_vendor_name
        pass
    except Exception as e:
        cylinder_stock_history = Cylinder_Store.objects.order_by('-cylinder_db_id')
        vendor_name = vendor_id
        pass
    context = {
        'cylinder_inward_outward_history': True,
        'gas_cylinder_vendors':gas_cylinder_vendors,
        'cylinder_stock_history':cylinder_stock_history,
        'vendor_name':vendor_name,
        'from_date':from_date,
        'to_date':to_date
    }
    return HttpResponse(template.render(context,request))