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
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

def current_ist_datetime():
    utc_datetime = timezone.now()
    ist = pytz.timezone('Asia/Kolkata')
    ist_datetime = utc_datetime.astimezone(ist)
    return ist_datetime

def _date_label(value):
    return value.strftime('%d %b') if value else 'Unknown'

def _build_daily_movement_chart(queryset):
    inward = {
        item['day']: item['count']
        for item in queryset.exclude(cylinder_Inward_Date__isnull=True)
        .annotate(day=TruncDate('cylinder_Inward_Date'))
        .values('day')
        .annotate(count=Count('cylinder_db_id'))
        .order_by('day')
    }
    outward = {
        item['day']: item['count']
        for item in queryset.exclude(cylinder_Outward_Date__isnull=True)
        .annotate(day=TruncDate('cylinder_Outward_Date'))
        .values('day')
        .annotate(count=Count('cylinder_db_id'))
        .order_by('day')
    }
    days = sorted(set(inward.keys()) | set(outward.keys()))
    return {
        'labels': [_date_label(day) for day in days],
        'inward': [inward.get(day, 0) for day in days],
        'outward': [outward.get(day, 0) for day in days],
    }

def _build_stock_type_chart(queryset):
    rows = (
        queryset.filter(
            cylinder_Inward=True,
            cylinder_stocked_in=True,
            cylinder_Outward=False,
            cylinder_stock_out=False,
        )
        .values('cylinder_gas_type__cylinder_gas_type')
        .annotate(count=Count('cylinder_db_id'))
        .order_by('cylinder_gas_type__cylinder_gas_type')
    )
    labels = [row['cylinder_gas_type__cylinder_gas_type'] or 'Unknown' for row in rows]
    data = [row['count'] for row in rows]
    return {'labels': labels, 'data': data}

def _build_vendor_chart(queryset):
    rows = (
        queryset.filter(cylinder_Inward=True)
        .values('cylinder_vendor_name__gas_cylinder_vendor_name')
        .annotate(count=Count('cylinder_db_id'))
        .order_by('-count')[:8]
    )
    labels = [row['cylinder_vendor_name__gas_cylinder_vendor_name'] or 'Unknown' for row in rows]
    data = [row['count'] for row in rows]
    return {'labels': labels, 'data': data}

def _average_hours(queryset, start, end):
    records = [
        (getattr(item, start), getattr(item, end))
        for item in queryset
        if getattr(item, start) and getattr(item, end)
    ]
    if not records:
        return 0
    total_seconds = sum((end_value - start_value).total_seconds() for start_value, end_value in records)
    return round((total_seconds / len(records)) / 3600, 1)

def build_cylinder_analytics(queryset=None):
    if queryset is None:
        queryset = Cylinder_Store.objects.all()
    available_filter = {
        'cylinder_Inward': True,
        'cylinder_Outward': False,
        'cylinder_stocked_in': True,
        'cylinder_stock_out': False,
    }
    pending_inward_filter = {
        'cylinder_Inward': True,
        'cylinder_Outward': False,
        'cylinder_stocked_in': False,
        'cylinder_stock_out': False,
    }
    pending_outward_filter = {
        'cylinder_Inward': True,
        'cylinder_Outward': True,
        'cylinder_stocked_in': True,
        'cylinder_stock_out': False,
    }
    available_stock = queryset.complex_filter(available_filter).count()
    pending_inward = queryset.complex_filter(pending_inward_filter).count()
    pending_outward = queryset.complex_filter(pending_outward_filter).count()
    stock_out = queryset.filter(cylinder_stock_out=True).count()
    total_cylinders = queryset.count()
    risk_count = pending_outward + pending_inward
    movement_chart = _build_daily_movement_chart(queryset)
    stock_type_chart = _build_stock_type_chart(queryset)
    vendor_chart = _build_vendor_chart(queryset)
    top_type = 'No active stock'
    if stock_type_chart['labels']:
        max_index = stock_type_chart['data'].index(max(stock_type_chart['data']))
        top_type = f"{stock_type_chart['labels'][max_index]} leads active stock with {stock_type_chart['data'][max_index]} cylinders"
    return {
        'summary': {
            'total_cylinders': total_cylinders,
            'available_stock': available_stock,
            'pending_inward': pending_inward,
            'pending_outward': pending_outward,
            'stock_out': stock_out,
            'risk_count': risk_count,
            'stock_health': round((available_stock / total_cylinders) * 100, 1) if total_cylinders else 0,
            'avg_stock_in_hours': _average_hours(queryset, 'cylinder_Inward_Date', 'cylinder_stocked_in_Date'),
            'avg_stock_out_hours': _average_hours(queryset, 'cylinder_Outward_Date', 'cylinder_stock_out_Date'),
        },
        'charts': {
            'movement': movement_chart,
            'stock_by_type': stock_type_chart,
            'vendor_mix': vendor_chart,
        },
        'insights': [
            top_type,
            f"{pending_inward} cylinders are scanned inward but not stocked in.",
            f"{pending_outward} cylinders are outward-marked but not stock-out confirmed.",
        ],
    }

def movement_date_filter(from_date=None, to_date=None):
    fields = [
        'cylinder_Inward_Date',
        'cylinder_Outward_Date',
        'cylinder_stocked_in_Date',
        'cylinder_stock_out_Date',
    ]
    movement_query = Q()
    for field in fields:
        field_query = Q()
        if from_date:
            field_query &= Q(**{f'{field}__date__gte': from_date})
        if to_date:
            field_query &= Q(**{f'{field}__date__lte': to_date})
        if from_date or to_date:
            movement_query |= field_query
    return movement_query

def empty_cylinder_analytics():
    return {
        'summary': {
            'total_cylinders': 0,
            'available_stock': 0,
            'pending_inward': 0,
            'pending_outward': 0,
            'stock_out': 0,
            'risk_count': 0,
            'stock_health': 0,
            'avg_stock_in_hours': 0,
            'avg_stock_out_hours': 0,
        },
        'charts': {
            'movement': {'labels': [], 'inward': [], 'outward': []},
            'stock_by_type': {'labels': [], 'data': []},
            'vendor_mix': {'labels': [], 'data': []},
        },
        'insights': [
            'Loading report insights.',
            'Loading inward workflow load.',
            'Loading outward workflow load.',
        ],
    }

def _json_auth_required(request):
    if not request.session.get('Login_id'):
        return JsonResponse({'detail': 'Authentication required.'}, status=401)
    return None

def _display_date(value, fmt='%d/%m/%Y | %I:%M %p'):
    if not value:
        return 'NA'
    if hasattr(value, 'astimezone'):
        value = timezone.localtime(value)
    return value.strftime(fmt)

def _vendor_options():
    return list(
        Gas_Cylinder_Vendors_Master.objects.order_by('gas_cylinder_vendor_name')
        .values('gas_cylinder_vendor_id', 'gas_cylinder_vendor_name')
    )

def _serialize_cylinder_record(record):
    return {
        'id': record.cylinder_db_id,
        'cylinder': record.cylinder_sl_r_qr_no or 'NA',
        'type': record.cylinder_gas_type.cylinder_gas_type if record.cylinder_gas_type else 'NA',
        'vendor': record.cylinder_vendor_name.gas_cylinder_vendor_name if record.cylinder_vendor_name else 'NA',
        'submitted_date': _display_date(record.cylinder_scanned_r_submitted_date),
        'entered_by': record.cylinder_scanned_r_submitted_by or 'NA',
        'inward_date': _display_date(record.cylinder_Inward_Date, '%d-%m-%Y %I:%M %p'),
        'stocked_in_date': _display_date(record.cylinder_stocked_in_Date, '%d-%m-%Y %I:%M %p'),
        'outward_date': _display_date(record.cylinder_Outward_Date, '%d-%m-%Y %I:%M %p'),
        'stock_out_date': _display_date(record.cylinder_stock_out_Date, '%d-%m-%Y %I:%M %p'),
        'return_dc': (
            record.Cylinder_Outward_Table.cylinder_return_DC
            if record.Cylinder_Outward_Table else 'NA'
        ),
    }

def _history_queryset(request):
    vendor_id = request.GET.get('cylinder_gas_vendor')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    queryset = Cylinder_Store.objects.select_related(
        'cylinder_vendor_name',
        'cylinder_gas_type',
        'Cylinder_Outward_Table',
    ).order_by('-cylinder_db_id')
    if vendor_id and vendor_id != 'ALL':
        try:
            queryset = queryset.filter(cylinder_vendor_name_id=int(vendor_id))
        except (TypeError, ValueError):
            pass
    if from_date or to_date:
        queryset = queryset.filter(movement_date_filter(from_date, to_date))
    return queryset

def cylinder_vendor_master(request):
    auth_response = _json_auth_required(request)
    if auth_response:
        return auth_response
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
    auth_response = _json_auth_required(request)
    if auth_response:
        return auth_response
    if request.method == 'POST':
        cylinder_id = int(request.POST.get('cylinder_id'))
        cylinder_sl_no = request.POST.get('cylinder_sl_no')
        cylinder_det = Cylinder_Store.objects.filter(cylinder_db_id=cylinder_id, cylinder_sl_r_qr_no=cylinder_sl_no).get()
        cylinder_type = cylinder_det.cylinder_gas_type.cylinder_gas_type
        return JsonResponse(data=cylinder_type,safe=False,status=200)

def cylinder_master_outward_qr_check(request):
    auth_response = _json_auth_required(request)
    if auth_response:
        return auth_response
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
    auth_response = _json_auth_required(request)
    if auth_response:
        return auth_response
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
    gas_cylinder_type = Cylinder_Type_Master.objects.order_by('cylinder_gas_type')
    analytics = build_cylinder_analytics()
    context = {
        'tdate': current_ist_datetime(),
        'dashboard_content': True,
        'gas_cylinder_type': gas_cylinder_type,
        'gas_cylinder_vendors':gas_cylinder_vendors,
        'analytics': analytics,
        'analytics_json': json.dumps(analytics, cls=DjangoJSONEncoder),
    }
    return HttpResponse(template.render(context,request))

def cylinder_dashboard_analytics(request):
    auth_response = _json_auth_required(request)
    if auth_response:
        return auth_response
    analytics = build_cylinder_analytics()
    return JsonResponse(
        {
            'timestamp': current_ist_datetime(),
            'analytics': analytics,
        },
        encoder=DjangoJSONEncoder,
        status=200,
    )

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
        'analytics': build_cylinder_analytics(),
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
        'analytics': build_cylinder_analytics(),
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
            logger.exception("Cylinder inward scan failed.")
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
        logger.exception("Cylinder inward detail creation failed.")
        if 'po_no' in str(e):
            context['error'] = 'PO Already Exists'
        elif 'GRN_no' in str(e):
            context['error'] = 'GRN Already Exists'
        elif 'Invoice_DC_no' in str(e):
            context['error'] = 'Invoice or DC Already Exists'
        setVar()
        return HttpResponse(template.render(context,request))

def cylinder_inward_remove(request):
    auth_response = _json_auth_required(request)
    if auth_response:
        return auth_response
    if request.method == 'POST':
        inward_selected = request.POST.getlist('selectedinward[]')
        for inward_c_id in inward_selected:
            Cylinder_Store.objects.filter(cylinder_db_id = inward_c_id).delete()
        return JsonResponse(data=True,safe=False,status=200)
    
def cylinder_stock_in(request):
    auth_response = _json_auth_required(request)
    if auth_response:
        return auth_response
    if request.method == 'POST':
        inward_selected = request.POST.getlist('selectedinward[]')
        if not inward_selected:
            return JsonResponse({'success': False, 'message': 'Select at least one cylinder to stock in.'}, status=400)
        updated_count = Cylinder_Store.objects.filter(
            cylinder_db_id__in=inward_selected,
            cylinder_Inward=True,
            cylinder_Outward=False,
            cylinder_stocked_in=False,
            cylinder_stock_out=False,
        ).update(
            cylinder_stocked_in=True,
            cylinder_stocked_in_Date=current_ist_datetime(),
        )
        if updated_count != len(inward_selected):
            return JsonResponse({'success': False, 'message': 'Some selected cylinders are no longer pending inward.'}, status=409)
        return JsonResponse({'success': True, 'updated': updated_count}, status=200)
    
def cylinder_outward_form(request):
    template = loader.get_template('QR/Cylinder-Outward/cylinder-outward-form.html')
    context = {
        'cylinder_outward_form': True,
        'cylinder_outward_stock': [],
        'gas_cylinder_vendors':[],
        'analytics': empty_cylinder_analytics(),
    }
    return HttpResponse(template.render(context,request))

def cylinder_outward_data(request):
    auth_response = _json_auth_required(request)
    if auth_response:
        return auth_response
    cylinder_outward_filter = {
        'cylinder_Inward': True,
        'cylinder_Outward': True,
        'cylinder_stocked_in': True,
        'cylinder_stock_out': False,
    }
    cylinder_outward_stock = (
        Cylinder_Store.objects.select_related('cylinder_gas_type', 'cylinder_vendor_name')
        .order_by('-cylinder_db_id')
        .complex_filter(cylinder_outward_filter)
    )
    return JsonResponse(
        {
            'analytics': build_cylinder_analytics(),
            'rows': [_serialize_cylinder_record(row) for row in cylinder_outward_stock],
            'vendors': _vendor_options(),
        },
        encoder=DjangoJSONEncoder,
        status=200,
    )

def cylinder_outward_submit(request):
    if request.method == 'POST':
        cylinder_id = request.POST.get('cylinder_sl_no') or request.POST.get('qr_sl_no_id')
        cylinder_gas_type = request.POST.get('cylinder_gas_type')
        cylinder_gas_vendor = request.POST.get('cylinder_gas_vendor')
        if not cylinder_id or not cylinder_gas_type or not cylinder_gas_vendor:
            raise Http404("Cylinder outward details are incomplete.")
        cylinder_type_det = Cylinder_Type_Master.objects.get(cylinder_gas_type=cylinder_gas_type)
        updated_count = Cylinder_Store.objects.filter(
            cylinder_db_id=int(cylinder_id),
            cylinder_gas_type=cylinder_type_det,
            cylinder_vendor_name=int(cylinder_gas_vendor),
            cylinder_Inward=True,
            cylinder_Outward=False,
            cylinder_stocked_in=True,
            cylinder_stock_out=False,
        ).update(
            cylinder_Outward=True,
            cylinder_Outward_Date=current_ist_datetime(),
        )
        if not updated_count:
            raise Http404("Cylinder is not available for outward.")
        return redirect('Cylinder-Outward-Form')

def cylinder_stock_out(request):
    auth_response = _json_auth_required(request)
    if auth_response:
        return auth_response
    if request.method == 'POST':
        outwardSelected = request.POST.getlist('outwardSelected[]')
        return_dc_no = request.POST.get('return_dc_no')
        return_remarks = request.POST.get('return_remarks')
        if not outwardSelected:
            return JsonResponse({'success': False, 'message': 'Select at least one cylinder to stock out.'}, status=400)
        if not return_dc_no:
            return JsonResponse({'success': False, 'message': 'Return DC number is required.'}, status=400)
        with transaction.atomic():
            outward_details, _ = Cylinder_Outward_Details.objects.update_or_create(
                cylinder_return_DC=return_dc_no,
                defaults={'cylinder_remarks': return_remarks}
            )
            updated_count = Cylinder_Store.objects.filter(
                cylinder_db_id__in=outwardSelected,
                cylinder_Inward=True,
                cylinder_Outward=True,
                cylinder_stocked_in=True,
                cylinder_stock_out=False,
            ).update(
                cylinder_stock_out=True,
                cylinder_stock_out_Date=current_ist_datetime(),
                Cylinder_Outward_Table=outward_details,
            )
            if updated_count != len(outwardSelected):
                transaction.set_rollback(True)
                return JsonResponse({'success': False, 'message': 'Some selected cylinders are no longer pending outward.'}, status=409)
        return JsonResponse({'success': True, 'updated': updated_count}, status=200)
    
def cylinder_inward_outward_history_table(request):
    template = loader.get_template('QR/Cylinder-History/cylinder-history.html')
    analytics = empty_cylinder_analytics()
    context = {
        'cylinder_inward_outward_history': True,
        'gas_cylinder_vendors':[],
        'analytics': analytics,
        'analytics_json': json.dumps(analytics, cls=DjangoJSONEncoder),
    }
    return HttpResponse(template.render(context,request))

def cylinder_history_data(request):
    auth_response = _json_auth_required(request)
    if auth_response:
        return auth_response
    cylinder_stock_history = _history_queryset(request)
    analytics = build_cylinder_analytics(cylinder_stock_history)
    return JsonResponse(
        {
            'analytics': analytics,
            'rows': [_serialize_cylinder_record(row) for row in cylinder_stock_history],
            'vendors': _vendor_options(),
        },
        encoder=DjangoJSONEncoder,
        status=200,
    )

def cylinder_inward_outward_history_submit(request):
    template = loader.get_template('QR/Cylinder-History/cylinder-history.html')
    vendor_id = request.GET.get('cylinder_gas_vendor')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    analytics = empty_cylinder_analytics()
    context = {
        'cylinder_inward_outward_history': True,
        'gas_cylinder_vendors':[],
        'cylinder_stock_history':[],
        'vendor_name':vendor_id,
        'from_date':from_date,
        'to_date':to_date,
        'analytics': analytics,
        'analytics_json': json.dumps(analytics, cls=DjangoJSONEncoder),
    }
    return HttpResponse(template.render(context,request))
