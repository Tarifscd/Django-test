# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import csv
import datetime
import json
import smtplib
from xmlrpc.client import DateTime

from django.db.models.functions import Coalesce
from ipware import ip
from datetime import timezone
from conf.settings import TIMEOUT_OF_EXTERNAL_MEMBER_LINK
import requests
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.files.storage import FileSystemStorage
from django.core.mail import EmailMessage, send_mail, EmailMultiAlternatives, get_connection
import html
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django.db.models import Sum, Count, Case, IntegerField, When, F, Q, Max, OuterRef, Subquery
from django.db.models.functions import Cast

from lged.models import User, Profile, Gallery, Tender, Budget, Office, Announcement, Issue, \
    AnnouncementStatus, IssueTitle, AuditTrail, Devices, PackageNo, TrainingBatch, Inventory, Lot, Package, \
    HomePageImage, APP, NewContract, TenderCost, Payment, InventoryProducts, TransferHistory, HomepageWriting, \
    Permission, ExpiredLink, TemporaryOffice, PasswordRequest, TrainingUser
from .tokens import account_activation_token

from lged.serializers import ProfileSerializer
from datetime import date
import datetime
from conf import settings
from django.core import serializers


# Create your views here.

def index(request):
    objects = HomePageImage.objects.values_list('image', 'title')
    image_list = []
    title_list = []
    for object in objects:
        image_list.append(object[0])
        title_list.append(object[1])
    user_count = User.objects.all().count()
    tender_count = Tender.objects.all().count()
    training_count = TrainingBatch.objects.filter(batch_number__isnull=False).values('batch_number').distinct().count()
    office_count = Office.objects.all().count()
    no = HomepageWriting.objects.count()
    no == 0 and HomepageWriting.objects.create(pk=1)
    notice_no_limit = HomepageWriting.objects.first().notice_no_limit
    if not notice_no_limit:
        notice_no_limit = 6
    count = {
        'user_count': user_count,
        'tender_count': tender_count,
        'training_count': training_count,
        'office_count': office_count,
        'notice_no_limit': notice_no_limit
    }
    return render(request, 'new_home.html', {'images': image_list, 'titles': title_list, 'count': count})


# ----------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------- User -------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------


@login_required(login_url='/')
def users(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'user-profile/users.html', {'user_permissions': user_permissions})


@login_required(login_url='/')
def filter_users(request, type):
    print('request === ', request.user.profile.role)
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    if request.GET.get('transfer'):
        return render(request, 'user-profile/users.html',
                      {'type': type, 'transfer': 1, 'user_permissions': user_permissions})
    else:
        return render(request, 'user-profile/users.html',
                      {'type': type, 'transfer': None, 'user_permissions': user_permissions})


@login_required(login_url='/')
def update_user(request, id):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'user-profile/../templates/old/update_user.html',
                  {'id': id, 'user_permissions': user_permissions})


@login_required(login_url='/')
def profile_details(request, id):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'user-profile/office_profile_details.html', {'id': id, 'user_permissions': user_permissions})
    # office_category = request.user.profile.office.office_category
    # if office_category == 'PAURASHAVA OFFICES' or office_category == 'CITY CORPORATION OFFICES' or office_category == 'ZILA PARISHAD OFFICES':
    #     return render(request, 'user-profile/office_profile_details.html', {'id': id})
    # else:
    #     return render(request, 'user-profile/profile_details.html', {'id': id})


@login_required(login_url='/')
def add_user(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'user-profile/../templates/old/add_user.html', {'user_permissions': user_permissions})


@login_required(login_url='/')
def update_profile(request):
    if request.user.is_authenticated():
        user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
        current_user = request.user
        # print(current_user)
        if current_user.is_active:
            return render(request, 'user-profile/../templates/old/update_profile.html',
                          {'user_permissions': user_permissions})
        else:
            return redirect('lged:not_found')
    else:
        return render(request, 'error-pages/404_body.html', {'error_code': '403'})


@login_required(login_url='/')
def transfer_history(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'user-profile/user_transfer.html', {'user_permissions': user_permissions})


@login_required(login_url='/')
def password_requests(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'user-profile/password_requests.html', {'id': None, 'user_permissions': user_permissions})


@login_required(login_url='/')
def request_password(request, id):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    data = {'id': id, 'user_permissions': user_permissions}
    return render(request, 'user-profile/password_requests.html', data)


def is_pending_egp_id(request_id):
    try:
        request = PasswordRequest.objects.get(e_gp_id=request_id, status='Pending')
        if request:
            return True
    except PasswordRequest.MultipleObjectsReturned:
        raise ValidationError({'Detail': 'Multipe request for a single EMAIL or E GP ID'})
    except PasswordRequest.DoesNotExist:
        return False
    return False


def last_egp_id_password(request_id):
    password = PasswordRequest.objects.filter(e_gp_id=request_id, status='Solved').order_by('updated_at').reverse()
    if password:
        return password[0].new_password
    return ''


@api_view(["GET"])
@login_required(login_url='/')
@permission_classes((permissions.IsAuthenticated,))
def e_gp_table(request, id):
    user = User.objects.get(id=id)
    if request.GET.get('temp_office_id') is None:
        proc_roles_for_lged = user.profile.procurement_roles.values_list('role', flat=True)
        proc_roles_for_lgis = user.profile.procurement_roles_lgis.values_list('role', flat=True)

    if request.GET.get('temp_office_id'):
        temp_office = TemporaryOffice.objects.filter(id=request.GET.get('temp_office_id'))[0]
        proc_roles_for_lged = temp_office.procurement_roles.values_list('role', flat=True)
        proc_roles_for_lgis = temp_office.procurement_roles_lgis.values_list('role', flat=True)

    var = ["Focal Point", "PE Admin", "Organization Admin"]
    govt_roles_for_lged = list(set(proc_roles_for_lged) - set(var))
    govt_roles_for_lgis = list(set(proc_roles_for_lgis) - set(var))
    data = []

    if ('PE Admin' in proc_roles_for_lged and user.profile.e_gp_user_id_for_pe_admin is not None and request.GET.get(
            'temp_office_id') is None) or (
            'PE Admin' in proc_roles_for_lged and temp_office.e_gp_user_id_for_pe_admin is not None and request.GET.get(
        'temp_office_id')):

        e_gp_id = user.profile.e_gp_user_id_for_pe_admin
        if request.GET.get('temp_office_id'):
            e_gp_id = temp_office.e_gp_user_id_for_pe_admin

        temp = {
            'e_gp_id for LGED': e_gp_id,
            'is_pending': is_pending_egp_id(e_gp_id),
            'lged_password': last_egp_id_password(e_gp_id),
            'e_gp_id for LGIS': None,
            'lgis_password': None
        }
        data.append(temp)
    if (
            'Organization Admin' in proc_roles_for_lged and user.profile.e_gp_user_id_for_org_admin is not None and request.GET.get(
        'temp_office_id') is None) or (
            'Organization Admin' in proc_roles_for_lged and temp_office.e_gp_user_id_for_org_admin is not None and request.GET.get(
        'temp_office_id')):

        e_gp_id = user.profile.e_gp_user_id_for_org_admin
        if request.GET.get('temp_office_id'):
            e_gp_id = temp_office.e_gp_user_id_for_org_admin

        temp = {
            'e_gp_id for LGED': e_gp_id,
            'is_pending': is_pending_egp_id(e_gp_id),
            'lged_password': last_egp_id_password(e_gp_id),
            'e_gp_id for LGIS': None,
            'lgis_password': None
        }
        data.append(temp)

    if (govt_roles_for_lged and user.profile.e_gp_user_id_for_govt is not None and request.GET.get(
            'temp_office_id') is None) or (
            govt_roles_for_lged and temp_office.e_gp_user_id_for_govt is not None and request.GET.get(
        'temp_office_id')):
        e_gp_id = user.profile.e_gp_user_id_for_govt
        if request.GET.get('temp_office_id'):
            e_gp_id = temp_office.e_gp_user_id_for_govt
        temp = {
            'e_gp_id for LGED': e_gp_id,
            'is_pending': is_pending_egp_id(e_gp_id),
            'lged_password': last_egp_id_password(e_gp_id),
            'e_gp_id for LGIS': None,
            'lgis_password': None
        }
        data.append(temp)
    if (
            'PE Admin' in proc_roles_for_lgis and user.profile.e_gp_user_id_lgis_for_pe_admin is not None and request.GET.get(
        'temp_office_id') is None) or (
            'PE Admin' in proc_roles_for_lgis and temp_office.e_gp_user_id_lgis_for_pe_admin is not None and request.GET.get(
        'temp_office_id')):

        e_gp_id = user.profile.e_gp_user_id_lgis_for_pe_admin
        if request.GET.get('temp_office_id'):
            e_gp_id = temp_office.e_gp_user_id_lgis_for_pe_admin

        temp = {
            'e_gp_id for LGIS': e_gp_id,
            'is_pending': is_pending_egp_id(e_gp_id),
            'lgis_password': last_egp_id_password(e_gp_id),
            'e_gp_id for LGED': None,
            'lged_password': None
        }
        data.append(temp)
    if (
            'Organization Admin' in proc_roles_for_lgis and user.profile.e_gp_user_id_lgis_for_org_admin is not None and request.GET.get(
        'temp_office_id') is None) or (
            'Organization Admin' in proc_roles_for_lgis and temp_office.e_gp_user_id_lgis_for_org_admin is not None and request.GET.get(
        'temp_office_id')):
        e_gp_id = user.profile.e_gp_user_id_lgis_for_org_admin
        if request.GET.get('temp_office_id'):
            e_gp_id = temp_office.e_gp_user_id_lgis_for_org_admin

        temp = {
            'e_gp_id for LGIS': e_gp_id,
            'is_pending': is_pending_egp_id(e_gp_id),
            'lgis_password': last_egp_id_password(e_gp_id),
            'e_gp_id for LGED': None,
            'lged_password': None
        }
        data.append(temp)
    if (govt_roles_for_lgis and user.profile.e_gp_user_id_lgis_for_govt is not None and request.GET.get(
            'temp_office_id') is None) or (
            govt_roles_for_lgis and temp_office.e_gp_user_id_lgis_for_govt is not None and request.GET.get(
        'temp_office_id')):
        e_gp_id = user.profile.e_gp_user_id_lgis_for_govt
        if request.GET.get('temp_office_id'):
            e_gp_id = temp_office.e_gp_user_id_lgis_for_govt

        temp = {
            'e_gp_id for LGIS': e_gp_id,
            'is_pending': is_pending_egp_id(e_gp_id),
            'lgis_password': last_egp_id_password(e_gp_id),
            'e_gp_id for LGED': None,
            'lged_password': None
        }
        data.append(temp)
    json_data = {
        'data': data,
        'recordsTotal': len(data),
        'recordsFiltered': len(data),
        'draw': None
    }
    return Response(json_data)


@login_required(login_url='/')
def transfer_user(request):
    user_id = None
    to = None
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    if request.GET.get('id'):
        user_id = request.GET.get('id')
    # if request.GET.get('to'):
    #     to = request.GET.get('to')
    return render(request, 'user-profile/user_transfer.html',
                  {'id': user_id, 'to': to, 'user_permissions': user_permissions})


# ------------------------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------User Multiple Assigning------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------

@login_required(login_url='/')
def multi_assign_user(request):
    user_id = None
    to = None
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    if request.GET.get('id'):
        user_id = request.GET.get('id')
    # if request.GET.get('to'):
    #     to = request.GET.get('to')
    return render(request, 'user-profile/user_multipe_assign.html',
                  {'id': user_id, 'to': to, 'user_permissions': user_permissions})


# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------- Office ----------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

@login_required(login_url='/')
def add_office(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'user-profile/add_office.html', {'user_permissions': user_permissions})


@login_required(login_url='/')
def update_office(request, id):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'user-profile/update_office.html', {'id': id, 'user_permissions': user_permissions})


@login_required(login_url='/')
def office_users(request, id):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'user-profile/office_users.html', {'id': id, 'user_permissions': user_permissions})


@login_required(login_url='/')
def user_profile(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    if 'office_admin' not in user_permissions:
        return render(request, 'user-profile/other_office_view.html', {'user_permissions': user_permissions})
    else:
        return render(request, 'user-profile/select_office.html', {'user_permissions': user_permissions})


# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------- Tender ----------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
@login_required(login_url='/')
def all_tender_list(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'app/all_tender_list.html', {'user_permissions': user_permissions})


@api_view(["GET"])
@login_required(login_url='/')
@permission_classes((permissions.AllowAny,))
def tender_status_detail(request, id):
    app = APP.objects.get(id=id)
    lot_list = Lot.objects.filter(package_no__app_id__id=id)
    data = []
    for lot in lot_list:
        package = lot.package_no
        tender = Tender.objects.filter(package=package)[0] if Tender.objects.filter(package=package) else None
        contract = NewContract.objects.filter(tender=tender)[0] if NewContract.objects.filter(tender=tender) else None
        payment = Payment.objects.filter(contract=contract)[0] if Payment.objects.filter(contract=contract) else None
        obj = {
            'office_name': app.office.name if app.office else '',
            'package_id': package.id,
            'package_no': package.package_no,
            'package_description': package.package_description,
            'proc_nature': package.proc_nature.nature if package.proc_nature else None,
            'proc_method': package.proc_method.method if package.proc_method else None,
            'proc_type': package.proc_type.type if package.proc_type else None,
            'type_of_emergency': package.type_of_emergency.type,
            'approving_authority': package.approving_authority.authority,
            'status': package.status,
            'package_approval_date': package.approval_date,
            'lot_id': lot.id,
            'lot_description': lot.lot_description,
            'lot_cost': lot.cost,
            'publication_date': tender.publication_date if tender else '',
            'closing_date': tender.closing_date if tender else '',
            'tender_approval_date': tender.approval_date if tender else '',
            'tender_validity': tender.tender_validity if tender else '',
            'no_of_tender_doc_sold': tender.no_of_tender_doc_sold if tender else '',
            'no_of_tender_doc_received': tender.no_of_tender_doc_received if tender else '',
            'no_of_responsive_tenderer': tender.no_of_responsive_tenderer if tender else '',
            'tender_status': tender.status if tender else '',
            'noa_issuing_date': contract.noa_issuing_date if contract else '',
            'responsive_bidder': contract.responsive_bidder if contract else '',
            'contract_signing_date': contract.contract_signing_date if contract else '',
            'contract_amount': contract.contract_amount if contract else '',
            'payment_start_date': payment.start_date if payment else '',
            'payment_completion_date': payment.completion_date if payment else '',
            'payment_commencement_date': payment.commencement_date if payment else ''
        }
        data.append(obj)

    json_data = {
        'data': data,
        'recordsTotal': len(data),
        'recordsFiltered': len(data),
        'draw': None
    }
    return Response(json_data)


@login_required(login_url='/')
def app_common_list(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'app/new_app_common_list.html', {'user_permissions': user_permissions})


@login_required(login_url='/')
def app_list(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'app/../templates/old/app_list.html', {'user_permissions': user_permissions})


@login_required(login_url='/')
def package_list(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    if request.GET.get('app'):
        return render(request, 'package/../templates/old/package_list.html',
                      {'app': request.GET.get('app'), 'user_permissions': user_permissions})
    else:
        return render(request, 'package/../templates/old/package_list.html',
                      {'app': None, 'user_permissions': user_permissions})


@login_required(login_url='/')
def lot_list(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    if request.GET.get('package'):
        return render(request, 'lot/../templates/old/lot_list.html',
                      {'package': request.GET.get('package'), 'user_permissions': user_permissions})
    else:
        return render(request, 'lot/../templates/old/lot_list.html',
                      {'package': None, 'user_permissions': user_permissions})


# @login_required(login_url='/')
# def tender_list(request):
#     if request.GET.get('package'):
#         return render(request, 'tender/old_tender_list.html', {'package': request.GET.get('package')})
#     else:
#         return render(request, 'tender/old_tender_list.html', {'package': None})


@login_required(login_url='/')
def payment(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'contract/payment.html', {'user_permissions': user_permissions})


@login_required(login_url='/')
def add_payment(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    contract_id = request.GET.get('contract')
    return render(request, 'contract/add_payment.html',
                  {'contract_id': contract_id, 'user_permissions': user_permissions})


@login_required(login_url='/')
def edit_payment(request, id):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'contract/edit_payment.html', {'id': id, 'user_permissions': user_permissions})


def get_contract_filter(qs, request):
    tender_id = request.GET.get('tender')
    organization = request.GET.get('organization')
    office_category = request.GET.get('office_category')
    region = request.GET.get('region')
    district = request.GET.get('district')
    office = request.GET.get('office')
    updated_at_from = request.GET.get('updated_at_from')
    updated_at_to = request.GET.get('updated_at_to')
    if tender_id:
        qs = qs.filter(tender__id=tender_id)
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    if 'tender_admin' not in user_permissions:
        qs = qs.filter(tender__package__app_id__office=request.user.profile.office.id)

    if organization:
        qs = qs.filter(tender__office__organization=organization)
    if office_category:
        qs = qs.filter(tender__office__office_category=office_category)
    if region:
        qs = qs.filter(tender__office__region=region)
    if district:
        qs = qs.filter(tender__office__district=district)
    if office:
        qs = qs.filter(tender__office=office)
    if updated_at_from:
        updated_from = datetime.datetime.strptime(updated_at_from, "%Y-%m-%d").date()
        qs = qs.filter(updated_at__gte=updated_from)
    if updated_at_to:
        updated_to = datetime.datetime.strptime(updated_at_to, "%Y-%m-%d").date()
        updated_to += datetime.timedelta(days=1)
        qs = qs.filter(updated_at__lte=updated_to)
    return qs


@login_required(login_url='/')
def contract_list(request):
    hide_contract_id = None
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    if request.GET.get('tender'):
        tender = request.GET.get('tender')
        tender_object = Tender.objects.get(id=tender)
        noa_no = tender_object.package.lots.count() - tender_object.newcontract_set.count()
        if tender_object.package.app_id.type == 'Off-line':
            hide_contract_id = 1
        return render(request, 'contract/new_contract_list.html', {'tender': tender, 'noa_no': noa_no,
                                                                   'hide_contract_id': hide_contract_id,
                                                                   'tender_id': tender_object.tender_id,
                                                                   'user_permissions': user_permissions})
    else:
        return render(request, 'contract/new_contract_list.html', {'tender': None, 'noa_no': None,
                                                                   'hide_contract_id': hide_contract_id,
                                                                   'tender_id': None,
                                                                   'user_permissions': user_permissions})
        # return render(request, 'contract/new_contract_list.html', {'tender': None})


@login_required(login_url='/')
def tender_list(request):
    hide_tender_id = None
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    if request.GET.get('package'):
        package_id = request.GET.get('package')
        package_obj = Package.objects.get(id=package_id)
        if package_obj.app_id.type == 'Off-line':
            hide_tender_id = 1
    if request.GET.get('package') and request.GET.get('add'):
        return render(request, 'tender/tender_list.html',
                      {'package': request.GET.get('package'), 'add': request.GET.get('add'),
                       'hide_tender_id': hide_tender_id, 'user_permissions': user_permissions})
    elif request.GET.get('package'):
        return render(request, 'tender/tender_list.html',
                      {'package': request.GET.get('package'), 'add': None, 'hide_tender_id': None,
                       'user_permissions': user_permissions})
    else:
        return render(request, 'tender/tender_list.html',
                      {'package': None, 'add': None, 'hide_tender_id': None, 'user_permissions': user_permissions})


@login_required(login_url='/')
def add_tender(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'tender/add_tender.html', {'user_permissions': user_permissions})


@login_required(login_url='/')
def update_tender(request, id):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'tender/update_tender.html', {'id': id, 'user_permissions': user_permissions})


@login_required(login_url='/')
def tender_report(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'tender/tender_report.html', {'user_permissions': user_permissions})


# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------- Budget ----------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
@login_required(login_url='/')
def budget_list(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'budget/budget_list.html', {'user_permissions': user_permissions})


@login_required(login_url='/')
def budget_csv(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'budget/budget_csv.html', {'user_permissions': user_permissions})


def get_budget_filter(request):
    qs = Budget.objects.all()
    organization = request.GET.get('organization')
    office_category = request.GET.get('office_category')
    region = request.GET.get('region')
    district = request.GET.get('district')
    office = request.GET.get('office')
    updated_at_from = request.GET.get('updated_at_from')
    updated_at_to = request.GET.get('updated_at_to')
    financial_year = request.GET.get('financial_year')
    fund_disburse_from = request.GET.get('fund_disburse_from')
    installment_no = request.GET.get('installment_no')

    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    if 'budget_admin' not in user_permissions:
        qs = qs.filter(office=request.user.profile.office.id)

    if organization:
        qs = qs.filter(office__organization=organization)
    if office_category:
        qs = qs.filter(office__office_category=office_category)
    if region:
        qs = qs.filter(office__region=region)
    if district:
        qs = qs.filter(office__district=district)
    if office:
        qs = qs.filter(office=office)
    if updated_at_from:
        updated_from = datetime.datetime.strptime(updated_at_from, "%Y-%m-%d").date()
        qs = qs.filter(updated_at__gte=updated_from)
    if updated_at_to:
        updated_to = datetime.datetime.strptime(updated_at_to, "%Y-%m-%d").date()
        updated_to += datetime.timedelta(days=1)
        qs = qs.filter(updated_at__lte=updated_to)
    if financial_year:
        qs = qs.filter(financial_year=financial_year)
    if fund_disburse_from:
        qs = qs.filter(fund_disburse_from=fund_disburse_from)
    if installment_no:
        qs = qs.filter(installment_no=installment_no)
    return qs


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def budget_report(request):
    response = []
    qs = get_budget_filter(request)
    # # print(qs)
    temp = qs.values('financial_year', 'fund_disburse_from').annotate(max_created_at=Max('created_at')). \
        values_list('financial_year', 'fund_disburse_from', 'max_created_at')
    # # print('ashiq1', temp)
    if temp:
        qs = Budget.objects.extra(where=['(financial_year, fund_disburse_from, created_at) in %s'],
                                  params=[tuple(temp)]).distinct()
    office = request.GET.get('office')
    # # print('ashiq', qs.values_list('financial_year', 'fund_disburse_from', 'created_at'))
    for entry in qs:
        # # print(entry.fund_disburse_from)
        total_amount = 0
        tender_under_process = 0
        if office:
            tender_under_process = TenderCost.objects.filter(tender__office=office,
                                                             tender__package__app_id__financial_year=entry.financial_year,
                                                             tender__package__app_id__source_of_fund__source=entry.fund_disburse_from).aggregate(
                tender_cost=Sum('cost'))['tender_cost']
            if tender_under_process is None:
                tender_under_process = 0
            total_amount = \
                qs.filter(office=office, financial_year=entry.financial_year,
                          fund_disburse_from=entry.fund_disburse_from) \
                    .aggregate(total_amount=Sum('budget_amount'))['total_amount']
        else:
            tender_under_process = \
                TenderCost.objects.filter(tender__package__app_id__financial_year=entry.financial_year).filter(
                    tender__package__app_id__source_of_fund__source=entry.fund_disburse_from).aggregate(
                    tender_cost=Sum('cost'))[
                    'tender_cost']
            if tender_under_process is None:
                tender_under_process = 0
            total_amount = qs.filter(financial_year=entry.financial_year, fund_disburse_from=entry.fund_disburse_from) \
                .aggregate(total_amount=Sum('budget_amount'))['total_amount']

        obj = {'financial_year': entry.financial_year}
        obj['fund_disburse_from'] = entry.fund_disburse_from
        obj['last_installment_no'] = entry.installment_no
        obj['tender_under_process'] = tender_under_process
        obj['total_amount'] = total_amount
        obj['pending_cost'] = total_amount - tender_under_process
        response.append(obj)

    return Response(response)


# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------- Inventory ----------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
@login_required(login_url='/')
def inventory_list(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'inventory/inventory_list_2.html', {'user_permissions': user_permissions})


# egp.ae.sht@lged.gov.bd

@login_required(login_url='/')
def add_inventory(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'inventory/add_inventory.html', {'user_permissions': user_permissions})


# @login_required(login_url='/')
# def add_asset_code(request):
#     return render(request, 'inventory/inventory_asset_code.html')


@login_required(login_url='/')
def asset_code(request, id):
    print("iddddddddd ========= ", id)
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    try:
        inv = Inventory.objects.get(id=id)
        if inv.supplied_quantity:
            quantity = inv.supplied_quantity
        else:
            quantity = 1
        asset_no = inv.asset_no
        if inv.asset_no is None:
            asset_no = ''
    except Exception as e:
        quantity = 0
        asset_no = ''
    return render(request, 'inventory/inventory_asset_code.html', {'id': id, 'quantity': quantity,
                                                                   'asset_no': asset_no,
                                                                   'user_permissions': user_permissions})


@login_required(login_url='/')
def update_inventory(request, id):
    print("iiiiiiiiiiiiiid ========= ", id)
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    try:
        inv = Inventory.objects.get(id=id)
        if inv.supplied_quantity:
            quantity = inv.supplied_quantity
        else:
            quantity = 1
        asset_no = inv.asset_no
        if inv.asset_no is None:
            asset_no = ''
    except Exception as e:
        quantity = 0
        asset_no = ''
    return render(request, 'inventory/update_inventory.html', {'id': id, 'quantity': quantity,
                                                               'asset_no': asset_no,
                                                               'user_permissions': user_permissions})


# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------- Training ----------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

def get_training_filter(request):
    qs = TrainingBatch.objects.all()
    organization = request.GET.get('organization')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    training_category = request.GET.get('training_category')
    training_name = request.GET.get('training_name')
    resource_center = request.GET.get('venue')
    user_id = request.GET.get('user_id')
    updated_at_from = request.GET.get('updated_at_from')
    updated_at_to = request.GET.get('updated_at_to')
    project = request.GET.get('project')
    financial_year = request.GET.get('financial_year')
    batch_no = request.GET.get('batch_no')
    user_list = request.GET.get('user_list')
    certificate = request.GET.get('certificate')
    training_name_name = request.GET.get('training_name_name')

    filters = {}
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    office_id = request.user.profile.office.id
    # if 'training_admin' not in user_permissions:
    #     qs_copy = qs
    #     qs = qs.filter(office_id=office_id).order_by('updated_at').distinct()
    #     training_user_list = []
    #     for user in User.objects.filter(profile__office_id=office_id):
    #         training_user_list.append(user.id)
    #     filters['traininguser__user__in'] = training_user_list
    #     qs = qs | qs_copy.filter(**filters).order_by('updated_at').distinct()
    #     qs = qs.filter(draft=0)
    if organization:
        qs = qs.filter(organization=organization)
    if training_category:
        qs = qs.filter(training_category=training_category)
    if training_name:
        qs = qs.filter(training_name=training_name)
    if training_name_name:
        if training_name_name == 'Training on Tender ':
            training_name_name = 'Training on Tender & Contract Management'
        qs = qs.filter(training_name__training_name=training_name_name)
    if project:
        qs = qs.filter(project=project)
    if resource_center:
        qs = qs.filter(venue=resource_center)
    if user_id:
        filters['traininguser__user__in'] = user_list.split(",")
        qs = qs.filter(**filters).order_by('updated_at').distinct()
    if certificate:
        qs = qs.filter(traininguser__certificate__isnull=False).distinct()
    if updated_at_from:
        updated_from = datetime.datetime.strptime(updated_at_from, "%Y-%m-%d").date()
        qs = qs.filter(updated_at__gte=updated_from)
    if updated_at_to:
        updated_to = datetime.datetime.strptime(updated_at_to, "%Y-%m-%d").date()
        updated_to += datetime.timedelta(days=1)
        qs = qs.filter(updated_at__lte=updated_to)
    if start_date:
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
        qs = qs.filter(start_date__gte=start_date)
    if end_date:
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
        qs = qs.filter(end_date__lte=end_date)
    if financial_year:
        qs = qs.filter(financial_year=financial_year)
    if batch_no:
        qs = qs.filter(batch_number=batch_no)

    if user_list:
        filters['traininguser__user__in'] = user_list.split(",")
        qs = qs.filter(**filters).order_by('updated_at').distinct()

    return qs


@login_required(login_url='/')
def training_list(request, category_id):
    category_id = int(category_id)
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    # category = ""
    # subtext = ""
    # if category_id == 0:
    #     category = "Training on e-GP"
    #     subtext = "List of the training batches in e-GP"
    # elif category_id == 1:
    #     category = "TOT Training on e-GP"
    #     subtext = "List of the TOT Training on e-GP"
    # elif category_id == 2:
    #     category = "Training on PPR"
    #     subtext = "List of the Training on PPR"
    # elif category_id == 3:
    #     category = "Training on CONT. MGT."
    #     subtext = "List of the Training on CONT. MGT."
    # elif category_id == 4:
    #     category = "Training on ICT"
    #     subtext = "List of the Training on ICT"
    # elif category_id == 5:
    #     category = "Training on BIDDERS"
    #     subtext = "List of the Training on BIDDERS"
    # elif category_id == 6:
    #     category = "Procurement Training"
    #     subtext = "List of the Procurement Training"
    # elif category_id == 7:
    #     category = "Foreign Training"
    #     subtext = "List of the Foreign Training"
    #
    # # print(category)
    # # print(subtext)
    return render(request, 'training/../templates/old/training_list.html', {'user_permissions': user_permissions})


@login_required(login_url='/')
def training_list_for_user(request, user_id):
    # user_id = request.user.profile.office.id
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'training/all_training_list.html', {'id': user_id, 'user_permissions': user_permissions})


@login_required(login_url='/')
def all_training_list(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    # user_office_category = request.user.profile.office.office_category
    # if user_office_category == 'LGED HQ':
    #     user_id = -1
    # else:
    #     user_id = request.user.profile.office.id
    return render(request, 'training/all_training_list.html', {'id': -1, 'user_permissions': user_permissions})


@login_required(login_url='/')
def single_user_training_list(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'training/single_user_training_list.html', {'user_permissions': user_permissions})


@login_required(login_url='/')
def trainers_pool(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    try:
        region = request.user.profile.office.region.id
    except Exception as e:
        region = ''
    return render(request, 'training/trainers_pool.html', {'region': region, 'user_permissions': user_permissions})


@login_required(login_url='/')
def users_training_list(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'training/users_training_list.html', {'user_permissions': user_permissions})


@login_required(login_url='/')
def training_details(request, id):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'training/training_details.html', {'id': id, 'user_permissions': user_permissions})


@login_required(login_url='/')
def add_training(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'training/add_training.html', {'user_permissions': user_permissions})


@login_required(login_url='/')
def add_local_training(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'training/add_local_training.html', {'user_permissions': user_permissions})


@login_required(login_url='/')
def training_update(request, id):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    finalized = request.GET.get('finalized')
    if finalized:
        finalized = 1
    else:
        finalized = 0
    return render(request, 'training/update_training.html',
                  {'id': id, 'finalized': finalized, 'user_permissions': user_permissions})


@login_required(login_url='/')
def local_training_update(request, id):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    finalized = request.GET.get('finalized')
    if finalized:
        finalized = 1
    else:
        finalized = 0
    return render(request, 'training/local_update_training.html',
                  {'id': id, 'finalized': finalized, 'user_permissions': user_permissions})


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def training_report(request):
    qs = get_training_filter(request)
    response = []
    obj = {'training_count': qs.count()}
    if qs.count() == 0:
        obj['no_of_participants'] = 0
    else:
        obj['no_of_participants'] = qs.aggregate(participants=Sum('no_of_participants'))['participants']
    response.append(obj)
    training_categories = qs.values_list('training_category', flat=True).distinct()
    for category in training_categories:
        obj = {}
        trainings = qs.filter(training_category=category)
        trainings = trainings.values('training_name__training_name').annotate(count=Count('id'),
                                                                              participants=Sum('no_of_participants'))
        if category != '':
            obj[category] = trainings
            response.append(obj)

    return Response(response)


# @login_required(login_url='/')
# def get_training_report(request):
#     organization = request.GET.get('organization')
#     start_date = request.GET.get('start_date')
#     end_date = request.GET.get('end_date')
#     training_category = request.GET.get('training_category')
#     training_name = request.GET.get('training_name')
#     resource_center = request.GET.get('resource_center')
#     user_id = request.GET.get('user_id')
#     updated_at_from = request.GET.get('updated_at_from')
#     updated_at_to = request.GET.get('updated_at_to')
#     project = request.GET.get('project')
#     financial_year = request.GET.get('financial_year')
#     batch_no = request.GET.get('batch_no')
#     user_list = request.GET.get('user_list')
#     certificate = request.GET.get('certificate')
#     qs = TrainingBatch.objects.all()
#     filters = {}
#     user_office_category = request.user.profile.office.office_category
#     office_id = request.user.profile.office.id
#     if user_office_category != "LGED HQ" and user_office_category != 'e-GP LAB OFFICES':
#         qs_copy = qs
#         qs = qs.filter(office_id=office_id).order_by('updated_at').distinct()
#         training_user_list = []
#         for user in User.objects.filter(profile__office_id=office_id):
#             training_user_list.append(user.id)
#         filters['traininguser__user__in'] = training_user_list
#
#         qs = qs | qs_copy.filter(**filters).order_by('updated_at').distinct()
#     if organization:
#         qs = qs.filter(organization=organization)
#     if training_category:
#         qs = qs.filter(training_category=training_category)
#     if training_name:
#         qs = qs.filter(training_name=training_name)
#     if project:
#         qs = qs.filter(project=project)
#     if resource_center:
#         qs = qs.filter(venue=resource_center)
#     if user_id:
#         filters['traininguser__user__in'] = user_list.split(",")
#         qs = qs.filter(**filters).order_by('updated_at').distinct()
#     if certificate:
#         qs = qs.filter(traininguser__certificate__isnull=False).distinct()
#     if updated_at_from:
#         updated_from = datetime.datetime.strptime(updated_at_from, "%Y-%m-%d").date()
#         qs = qs.filter(updated_at__gte=updated_from)
#     if updated_at_to:
#         updated_to = datetime.datetime.strptime(updated_at_to, "%Y-%m-%d").date()
#         updated_to += datetime.timedelta(days=1)
#         qs = qs.filter(updated_at__lte=updated_to)
#     if start_date:
#         start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
#         qs = qs.filter(start_date__gte=start_date)
#     if end_date:
#         end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
#         qs = qs.filter(end_date__lte=end_date)
#     if financial_year:
#         qs = qs.filter(financial_year=financial_year)
#     if batch_no:
#         qs = qs.filter(batch_no=batch_no)
#
#     if user_list:
#         filters['traininguser__user__in'] = user_list.split(",")
#         qs = qs.filter(**filters).order_by('updated_at').distinct()
#
#     return qs


# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------- External Members ---------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
@login_required(login_url='/')
def external_member(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'external-member/external_member_temp.html', {'user_permissions': user_permissions})


def external_member_link(request, case):
    user_id = request.GET.get('id') if request.GET.get('id') else None
    office_id = request.GET.get('off') if request.GET.get('off') else None
    # print('off id === ', office_id)
    office_data = None
    organization = None
    office_category = None
    office_name = None
    if office_id:
        office_data = Office.objects.filter(id=office_id).values_list('name', 'organization', 'office_category')
        # print('office data === ', office_data)
        if office_data is not None:
            office_name = office_data[0][0]
            organization = office_data[0][1]
            office_category = office_data[0][2]
    # print('office name === ', office_name)
    # print('organization === ', organization)
    # print('office category === ', office_category)

    if ExpiredLink.objects.filter(link=request.build_absolute_uri()).count() == 0:  # no such link exists
        return redirect('lged:not_found')
    if ExpiredLink.objects.filter(link=request.build_absolute_uri()).first().expired:  # link expired
        return redirect('lged:not_found')
    if (datetime.datetime.now(timezone.utc) - ExpiredLink.objects.filter(
            link=request.build_absolute_uri()).first().created_at).days > TIMEOUT_OF_EXTERNAL_MEMBER_LINK:  # 1 day
        return redirect('lged:not_found')
    if case == '4' and user_id is None:
        return redirect('lged:not_found')
    if user_id and User.objects.filter(id=user_id).count() == 0:
        return redirect('lged:not_found')
    user_permissions = list(
        request.user.profile.role.permission.values_list('code', flat=True)) if request.user.is_authenticated else []
    return render(request, 'external-member/external_member_inclusion_link.html', {'user_permissions': user_permissions,
                                                                                   'case': case, 'user_id': user_id,
                                                                                   'office_name': office_name,
                                                                                   'organization': organization,
                                                                                   'office_category': office_category})


@login_required(login_url='/')
def external_member_organization(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'settings/ext_member_org.html', {'user_permissions': user_permissions})


@login_required(login_url='/')
def fund_disburse_from(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'settings/fund_disburse_from.html', {'user_permissions': user_permissions})


@login_required(login_url='/')
def committee_type(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'settings/committee_type.html', {'user_permissions': user_permissions})


@login_required(login_url='/')
def invitee_office(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'settings/invitee_office.html', {'user_permissions': user_permissions})


def read_more(request):
    return render(request, 'read_more.html')


def e_gp_trainers_pool(request):
    user_permissions = list(
        request.user.profile.role.permission.values_list('code', flat=True)) if request.user.is_authenticated else []
    return render(request, 'e_gp_trainers_pool.html', {'user_permissions': user_permissions})


def about_lgis(request):
    return render(request, 'about_lgis.html')


def about_dimapp(request):
    return render(request, 'about_dimapp.html')


def contacts(request):
    user_permissions = list(
        request.user.profile.role.permission.values_list('code', flat=True)) if request.user.is_authenticated else []
    return render(request, 'contacts.html', {'user_permissions': user_permissions})


def lgis_category(request, category):
    user_permissions = list(
        request.user.profile.role.permission.values_list('code', flat=True)) if request.user.is_authenticated else []
    if category == 'city_corporation_offices':
        category = 'CITY CORPORATION OFFICES'
    elif category == 'zila_parishad_offices':
        category = 'ZILA PARISHAD OFFICES'
    elif category == 'paurashava_offices':
        category = 'PAURASHAVA OFFICES'
    else:
        category = 'UPAZILA PARISHAD OFFICES'
    return render(request, 'submenu_of_LGIs.html', {'category': category, 'user_permissions': user_permissions})


@login_required(login_url='/')
def responsive_bidder(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'settings/responsive_bidder.html', {'user_permissions': user_permissions})


# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------- Audit Trail---------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
@login_required(login_url='/')
def audit_trail(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    param = {'module_id': None, 'module': None, 'user_permissions': user_permissions}
    if request.GET.get('module_id'):
        param['module_id'] = request.GET.get('module_id')
    if request.GET.get('module'):
        param['module'] = request.GET.get('module')
    return render(request, 'audit_trail/audit_trail.html', param)


def audit_trail_record(request, obj, prev_data, module_name, action):
    user_ip = ip.get_ip(request)
    data = {}
    if module_name == "OFFICE PROFILE":
        data = get_office_profile_data(obj.id)
    elif module_name == "USER PROFILE":
        data = get_user_profile_data(obj.id)
    elif module_name == "INVENTORY RECORDS":
        data = get_inventory_data(obj.id)
    elif module_name == 'USER TRANSFER':
        data = get_user_transfer_data(obj.id)

    AuditTrail(module_name=module_name, module_id=obj.pk, user=request.user,
               time=datetime.datetime.now(), action=action, prev_detail=prev_data, detail=data,
               ip_address=user_ip).save()


def get_user_transfer_data(key):
    data = TransferHistory.objects.filter(id=key).values(ID=F('id'), Office=F('transferred_office__name'),
                                                         Name=F('user__first_name'),
                                                         Designation=F('new_designation__designation'),
                                                         Memo_No=F('transfer_memo_no'),
                                                         Charge_Takeover_Date=F('charge_takeover_date'),
                                                         Charge_Handover_Date=F('charge_handover_date'),
                                                         Status=F('approved_status'))[0]
    data = json.loads(json.dumps(data, default=str))  # to avoid json serializable error
    return data


def get_office_profile_data(key):
    data = Office.objects.filter(id=key).values(Office_Name=F('name'), Division=F('division__name'),
                                                Region=F('region__name'), District=F('district__name'),
                                                Upazila=F('upazila__name'), Class=F('pourashava_class'),
                                                Post_Code=F('post_code'), Phone_No=F('phone_no'),
                                                Fax_No=F('fax_no'), Website=F('website_link'),
                                                Email=F('email'), Latitude=F('latt'), Longitude=F('long'))[0]
    data = json.loads(json.dumps(data, default=str))  # to avoid json serializable error
    return data


def get_user_profile_data(key):
    data = User.objects.filter(id=key).values(Office=F('profile__office__name'), First_Name=F('first_name'),
                                              Designation=F('profile__designation__designation'),
                                              Personal_Mobile_No=F('profile__mobile_no'),
                                              Official_Mobile_No=F('profile__official_mobile_no'),
                                              Personal_Email=F('profile__personal_email'),
                                              Official_Email=F('profile__official_email'),
                                              NID=F('profile__nid'),
                                              Gender=F('profile__gender'), Date_of_Birth=F('profile__date_of_birth'),
                                              )[0]
    data = json.loads(json.dumps(data, default=str))  # to avoid json serializable error
    proc_role = list(
        Profile.objects.get(user__id=key).procurement_roles.all().distinct().values_list('role', flat=True))
    proc_role_lgis = list(
        Profile.objects.get(user__id=key).procurement_roles_lgis.all().distinct().values_list('role', flat=True))
    data['Procurement_Role_LGED'] = ", ".join(proc_role)
    data['Procurement_Role_LGIs'] = ", ".join(proc_role_lgis)
    return data


def get_inventory_data(key):
    data = Inventory.objects.filter(id=key).values(Office=F('office__name'), ID=F('id'),
                                                   Inventory_Type=F('type__type'), Brand_Name=F('device__brand_name'),
                                                   Model_No=F('device__model_no'),
                                                   Date_of_Received=F('date_of_delivery'),
                                                   Warranty_Period=F('device__validity'), Status=F('status__status'),
                                                   Package=F('package_no__package_no'),
                                                   Procured_By=F('package_no__source__source'),
                                                   Supplied_Quantity=F('supplied_quantity'))[0]
    data = json.loads(json.dumps(data, default=str))  # to avoid json serializable error
    return data


# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------- Publication --------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
def publication_list1(request):
    user_permissions = list(
        request.user.profile.role.permission.values_list('code', flat=True)) if request.user.is_authenticated else []
    return render(request, 'publication/publication_list.html', {'parent': None, 'user_permissions': user_permissions})


def publication_list2(request, parent):
    user_permissions = list(
        request.user.profile.role.permission.values_list('code', flat=True)) if request.user.is_authenticated else []
    return render(request, 'publication/publication_list.html',
                  {'parent': parent, 'user_permissions': user_permissions})


@login_required(login_url='/')
def add_publication1(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'publication/add_publication.html', {'user_permissions': user_permissions})


@login_required(login_url='/')
def add_publication2(request, parent):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'publication/add_publication.html', {'parent': parent, 'user_permissions': user_permissions})


@login_required(login_url='/')
def update_publication(request, id):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'publication/update_publication.html', {'id': id, 'user_permissions': user_permissions})


# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------- Gallery ----------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
def gallery_list(request):
    images = Gallery.objects.all()
    user_permissions = list(
        request.user.profile.role.permission.values_list('code', flat=True)) if request.user.is_authenticated else []
    return render(request, 'gallery/gallery_list.html', {'images': images, 'user_permissions': user_permissions})


def gallery_list1(request):
    parent = None
    user_permissions = list(
        request.user.profile.role.permission.values_list('code', flat=True)) if request.user.is_authenticated else []
    if request.user.is_authenticated and request.user.profile.office.office_category == 'e-GP LAB OFFICES':
        try:
            parent = Gallery.objects.filter(title=request.user.profile.office.name).first().id
        except Exception as e:
            parent = None
    return render(request, 'gallery/gallery_list_2.html', {'parent': parent, 'user_permissions': user_permissions})


def gallery_list2(request, parent):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'gallery/gallery_list_2.html', {'parent': parent, 'user_permissions': user_permissions})


@login_required(login_url='/')
def add_gallery1(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'gallery/add_gallery.html', {'user_permissions': user_permissions})


@login_required(login_url='/')
def add_gallery2(request, parent):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'gallery/add_gallery.html', {'parent': parent, 'user_permissions': user_permissions})


@login_required(login_url='/')
def gallery_add_title1(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'gallery/gallery_add_title.html', {'parent': None, 'user_permissions': user_permissions})


@login_required(login_url='/')
def gallery_add_title2(request, parent):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'gallery/gallery_add_title.html', {'parent': parent, 'user_permissions': user_permissions})


# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------- Error ----------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
def not_found(request):
    return render(request, '404/404_body.html')


def custom_error(request):
    return render(request, 'error-pages/404_body.html')


# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------- Project ----------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
@login_required(login_url='/')
def project_profile(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'project-profile/project_profile.html', {'user_permissions': user_permissions})


@login_required(login_url='/')
def add_project(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'project-profile/add_project.html', {'user_permissions': user_permissions})


@login_required(login_url='/')
def update_project(request, id):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'project-profile/update_project.html', {'id': id, 'user_permissions': user_permissions})


@login_required(login_url='/')
def project_details(request, id):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'project-profile/project_details.html', {'id': id, 'user_permissions': user_permissions})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        if request.user.is_authenticated():
            # print("user is logged in. so, trying to log out")
            logout(request)
        login(request, user)
        # return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
        flash_message = "Your mail has been successfully actived"
        return redirect('lged:update_profile')
    else:
        return HttpResponse('Activation link is invalid!')


# ----------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------- Resource Centers -------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
def resource_centers(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'resource-centers/../templates/old/resource_centers.html',
                  {'user_permissions': user_permissions})


def venue(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'settings/Venue.html', {'user_permissions': user_permissions})


# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------- Settings -----------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
@login_required(login_url='/')
def designation(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'settings/designation.html', {'user_permissions': user_permissions})


@login_required(login_url='/')
def procurement_role(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'settings/procurement_role.html', {'user_permissions': user_permissions})


@login_required(login_url='/')
def inv_type(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'settings/inv_type.html', {'user_permissions': user_permissions})


@login_required(login_url='/')
def inv_type_category(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'settings/inv_type_category.html', {'user_permissions': user_permissions})


@login_required(login_url='/')
def inv_status(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'settings/inv_status.html', {'user_permissions': user_permissions})


@login_required(login_url='/')
def inv_file_type(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'settings/inv_file_type.html', {'user_permissions': user_permissions})


@login_required(login_url='/')
def inv_package(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'settings/inv_package.html', {'user_permissions': user_permissions})


@login_required(login_url='/')
def inv_package_devices(request, id):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    devices = Devices.objects.filter(package_no=id)
    return render(request, 'settings/inv_package_device.html',
                  {'id': id, 'devices': devices, 'user_permissions': user_permissions})


@login_required(login_url='/')
def division(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'settings/division.html', {'user_permissions': user_permissions})


@login_required(login_url='/')
def region(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'settings/region.html', {'user_permissions': user_permissions})


@login_required(login_url='/')
def district(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'settings/district.html', {'user_permissions': user_permissions})


@login_required(login_url='/')
def upazila(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'settings/upazila.html', {'user_permissions': user_permissions})


@login_required(login_url='/')
def budget_type(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'settings/BudgetType.html', {'user_permissions': user_permissions})


@login_required(login_url='/')
def procurement_nature(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'settings/ProcurementNature.html', {'user_permissions': user_permissions})


@login_required(login_url='/')
def type_of_emergency(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'settings/TypeOfEmergency.html', {'user_permissions': user_permissions})


@login_required(login_url='/')
def proc_method(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'settings/ProcMethod.html', {'user_permissions': user_permissions})


@login_required(login_url='/')
def proc_type(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'settings/ProcType.html', {'user_permissions': user_permissions})


@login_required(login_url='/')
def source_of_fund(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'settings/SourceOfFund.html', {'user_permissions': user_permissions})


@login_required(login_url='/')
def role_permission(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    if request.user.profile.role.code != 'admin_category_1':
        return redirect('lged:not_found')
    permissions = Permission.objects.all()
    return render(request, 'settings/Role.html', {'permissions': permissions, 'user_permissions': user_permissions})


@login_required(login_url='/')
def external_member_inclusion(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'external-member/ExternalMemberInclusionHistory.html',
                  {'user_permissions': user_permissions})


# for Training
@login_required(login_url='/')
def funded_by(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'settings/FundedBy.html', {'user_permissions': user_permissions})


@login_required(login_url='/')
def approving_authority(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'settings/ApprovingAuthority.html', {'user_permissions': user_permissions})


@login_required(login_url='/')
def contract_status(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'settings/ContractStatus.html', {'user_permissions': user_permissions})


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def email_verification(request):
    email = request.data.get('email', '')
    try:
        user = User.objects.get(email=email)
    except Exception as e:
        return Response({'status': '404', 'error_message': 'This email address can not be found in the database'})

    current_site = get_current_site(request)

    mail_subject = 'Activate your lged account.'
    message = render_to_string('email/acc_active_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
    })
    email = EmailMessage(
        mail_subject, message, to=[email]
    )
    try:
        email.send()
    except Exception as e:
        return Response({'status': '404', 'error_message': 'Email could not be sent'})
    return Response({'status': '200', 'error_message': ''})


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def otp_verification(request):
    connection = get_connection(host=settings.EMAIL_HOST, port=settings.EMAIL_PORT,
                                username=settings.EMAIL_HOST_USER, password=settings.EMAIL_HOST_PASSWORD,
                                use_tls=settings.EMAIL_USE_TLS)

    cc = []
    try:
        user = User.objects.get(email=request.data['email'])
    except Exception as e:
        return Response({'status': '404', 'error_message': 'This email address can not be found in the database'})

    mail_subject = 'OTP for password reset'
    message = render_to_string('email/otp_email.html', {
        'otp': request.data['otp'],
    })

    # email = EmailMessage(
    #     mail_subject, message, to=[request.data['email']]
    # )
    from_email = settings.EMAIL_HOST_USER
    email = EmailMultiAlternatives(subject=mail_subject, body=message, from_email=from_email,
                                   to=[request.data['email']],
                                   cc=cc,
                                   connection=connection)
    try:
        connection.open()
        email.send()
        connection.close()
    except Exception as e:
        print(e)
        return Response({'status': '404', 'error_message': 'Email could not be sent'})
    return Response({'status': '200', 'error_message': ''})


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def loginUser(request):
    if request.method == 'POST':
        email = request.data['email']
        password = request.data['password']
        user = authenticate(request, username=email, password=password)
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                login(request, user)
                # return HttpResponseRedirect(reverse('lged:user_profile'))

                # audit trail action here-----------------------
                audit_trail_record(request, user, {}, "LOGIN MODULE", 'LOGIN')
                # audit trail action here-----------------------

                return Response('OK')
        else:
            return Response('NO')


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def changePassword(request):
    if request.method == 'POST':
        type = request.data['type']
        password = request.data['password']
        email_or_mobile = request.data['email_or_mobile']
        # print(request.data)

        if type == 'email':
            # user = User.objects.get(email=email_or_mobile)

            user = get_object_or_404(User, email=email_or_mobile)
            # print(user)

            user.set_password(password)
            user.save()
        elif type == 'mobile':

            try:
                profile = Profile.objects.filter(mobile_no=email_or_mobile)
                profile = profile[0]
                user = User.objects.get(profile=profile)
                user.set_password(password)
                user.save()
            except Exception as e:
                return Response('NO')

        # print(request.data)
        return Response('OK')


@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,))
def simple_change_password(request):
    if request.method == 'POST':
        password = request.data['new_password']
        prev_password = request.data['password']
        email = request.data['email']

        user = get_object_or_404(User, email=email)

        if user.check_password('{}'.format(prev_password)) == False:
            return Response('NO')
        # Tarif_Update
        if prev_password == password:
            return Response('Same')
        # **

        user.set_password(password)
        user.password_reset = False
        user.save()
    return Response('OK')


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def change_stage(request):
    if request.method == 'POST':
        id = request.data['id']
        User.objects.filter(id=id).update(stage=F('stage') + 1)
        # User.objects.filter(id=id).update(password_reset=False)
    return Response('OK')


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def logoutUser(request):
    if request.method == 'POST':
        # print("logging out")
        # audit trail action here-----------------------
        audit_trail_record(request, request.user, {}, "LOGIN MODULE", 'LOGOUT')
        # audit trail action here-----------------------
        logout(request)
        return Response('OK')


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def sendSMS(request):
    # http: // bangladeshsms.com / smsapi?api_key = APIKEY & type = text & contacts = NUMBER & senderid =Approved SenderID & msg = MessageContent
    # print(request.data)
    api_key = "api_key=C2000035590430644fa064.54220829"
    type = "type=text"
    contacts = "contacts=+88" + request.data['mobile_no']
    senderid = "senderid=8804445629108"
    msg = "msg=Your OTP for LGED is " + request.data['otp']
    url = "http://bangladeshsms.com/smsapi?" + api_key + "&" + type + "&" + contacts + "&" + senderid + "&" + msg

    response = requests.post(url, data="")
    content = response.content
    content = content.decode("utf-8")
    array = content.split(',')
    status = array[0]
    # print(status)
    if status == "1000":
        return Response({'status': '200', 'error_message': ''})

    return Response({'status': '404', 'error_message': 'Could not send sms'})


# @api_view(['POST'])
# @permission_classes((permissions.AllowAny,))
# def sendTrainingSMS(request):
#     # http: // bangladeshsms.com / smsapi?api_key = APIKEY & type = text & contacts = NUMBER & senderid =Approved SenderID & msg = MessageContent
#     # print(request.data)
#     api_key = "api_key=C2000035590430644fa064.54220829"
#     type = "type=text"
#     contacts = "contacts=+88" + request.data['mobile_no']
#     senderid = "senderid=8804445629108"
#     url = "http://bangladeshsms.com/smsapi?" + api_key + "&" + type + "&" + contacts + "&" + senderid
#
#     response = requests.post(url, data="")
#     content = response.content
#     content = content.decode("utf-8")
#     array = content.split(',')
#     status = array[0]
#     # print(status)
#     if status == "1000":
#         return Response({'status': '200', 'error_message': ''})
#
#     return Response({'status': '404', 'error_message': 'Could not send sms'})


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def otp_verification_mobile(request):
    user = User.objects.filter(profile__mobile_no=request.data['mobile_no'])
    len = user.__len__()
    if len == 0:
        return Response({'status': '404', 'error_message': 'Could not find the mobile no in the database'})

    # http: // bangladeshsms.com / smsapi?api_key = APIKEY & type = text & contacts = NUMBER & senderid =Approved SenderID & msg = MessageContent
    # print(request.data)
    api_key = "api_key=C2000035590430644fa064.54220829"
    type = "type=text"
    contacts = "contacts=+88" + request.data['mobile_no']
    senderid = "senderid=8804445629108"
    msg = "msg=Your OTP for LGED is " + request.data['otp']
    url = "http://bangladeshsms.com/smsapi?" + api_key + "&" + type + "&" + contacts + "&" + senderid + "&" + msg + "&reply=Y"

    response = requests.post(url, data="")
    content = response.content
    content = content.decode("utf-8")
    array = content.split(',')
    status = array[0]
    # print(status)
    if status == "1000":
        return Response({'status': '200', 'error_message': ''})

    return Response({'status': '404', 'error_message': 'Could not send sms'})


# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------- Statistics ---------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def total_tender(request):
    response = []
    e_gp = Tender.objects.filter(package_no__app_id__type='e-GP').count()
    offline = Tender.objects.filter(package_no__app_id__type='Off-line').count()
    response.append({"name": "e-GP", "y": e_gp})
    response.append({"name": "Off-line", "y": offline})
    return Response(response)


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def monthly_tender(request):
    month_list = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
    e_gp = []
    offline = []
    response = {"JAN": {"e-GP": 3, "Off-line": 1}, "FEB": {"e-GP": 2, "Off-line": 1}, "MAR": {"e-GP": 1, "Off-line": 2},
                "APR": {"e-GP": 4, "Off-line": 1}, "MAY": {"e-GP": 1, "Off-line": 4}, "JUN": {"e-GP": 5, "Off-line": 2},
                "JUL": {"e-GP": 2, "Off-line": 3}, "AUG": {"e-GP": 4, "Off-line": 2}, "SEP": {"e-GP": 1, "Off-line": 3},
                "OCT": {"e-GP": 2, "Off-line": 5}, "NOV": {"e-GP": 3, "Off-line": 2},
                "DEC": {"e-GP": 5, "Off-line": 5}, }

    e_gp.append(Tender.objects.filter(package_no__app_id__type='e-GP', publication_date__month=1).count())
    offline.append(Tender.objects.filter(package_no__app_id__type='Off-line',
                                         publication_date__month=1).count())

    e_gp.append(Tender.objects.filter(package_no__app_id__type='e-GP', publication_date__month=2).count())
    offline.append(Tender.objects.filter(package_no__app_id__type='Off-line',
                                         publication_date__month=2).count())

    e_gp.append(Tender.objects.filter(package_no__app_id__type='e-GP', publication_date__month=3).count())
    offline.append(Tender.objects.filter(package_no__app_id__type='Off-line',
                                         publication_date__month=3).count())

    e_gp.append(Tender.objects.filter(package_no__app_id__type='e-GP', publication_date__month=4).count())
    offline.append(Tender.objects.filter(package_no__app_id__type='Off-line',
                                         publication_date__month=4).count())

    e_gp.append(Tender.objects.filter(package_no__app_id__type='e-GP', publication_date__month=5).count())
    offline.append(Tender.objects.filter(package_no__app_id__type='Off-line',
                                         publication_date__month=5).count())

    e_gp.append(Tender.objects.filter(package_no__app_id__type='e-GP', publication_date__month=6).count())
    offline.append(Tender.objects.filter(package_no__app_id__type='Off-line',
                                         publication_date__month=6).count())

    e_gp.append(Tender.objects.filter(package_no__app_id__type='e-GP', publication_date__month=7).count())
    offline.append(Tender.objects.filter(package_no__app_id__type='Off-line',
                                         publication_date__month=7).count())

    e_gp.append(Tender.objects.filter(package_no__app_id__type='e-GP', publication_date__month=8).count())
    offline.append(Tender.objects.filter(package_no__app_id__type='Off-line',
                                         publication_date__month=8).count())

    e_gp.append(Tender.objects.filter(package_no__app_id__type='e-GP', publication_date__month=9).count())
    offline.append(Tender.objects.filter(package_no__app_id__type='Off-line',
                                         publication_date__month=9).count())

    e_gp.append(Tender.objects.filter(package_no__app_id__type='e-GP', publication_date__month=10).count())
    offline.append(Tender.objects.filter(package_no__app_id__type='Off-line',
                                         publication_date__month=10).count())

    e_gp.append(Tender.objects.filter(package_no__app_id__type='e-GP', publication_date__month=11).count())
    offline.append(Tender.objects.filter(package_no__app_id__type='Off-line',
                                         publication_date__month=11).count())

    e_gp.append(Tender.objects.filter(package_no__app_id__type='e-GP', publication_date__month=12).count())
    offline.append(Tender.objects.filter(package_no__app_id__type='Off-line',
                                         publication_date__month=12).count())

    return Response({'months': month_list, 'e_gp': e_gp, 'offline': offline})


# ----------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------- Budget -----------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,))
def upload_budget_csv(request):
    file = request.FILES['document']
    # print(file)

    fs = FileSystemStorage(location='media/budget-csv/')
    filename = fs.save(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + file.name, file)
    filename = 'media/budget-csv/' + filename

    total_amount = 0
    total_row = 0

    objects = []
    released_budget = 0
    deficit = 0
    with open(filename) as csvfile:
        budgetReader = csv.reader(csvfile, skipinitialspace=True)
        flag = 0
        budget_amount, office_id, district, financial_year, fund_disburse_from, installment_no, issue_date, memo_no, subject, \
        total_provision, type, comments = ('',) * 12
        for row in budgetReader:
            if row[1] == '':
                deficit = int(row[0])
                break
            if flag == 0:
                flag = 1
                continue
            for i in range(0, len(row)):
                if i == 0:
                    budget_amount = row[i]
                elif i == 13:
                    office_id = row[i]
                elif i == 2:
                    district = row[i]
                elif i == 3:
                    financial_year = row[i]
                elif i == 4:
                    fund_disburse_from = row[i]
                elif i == 5:
                    installment_no = row[i]
                elif i == 6:
                    issue_date = row[i]
                    issue_date = datetime.datetime.strptime(issue_date, '%d/%m/%Y')
                    issue_date = datetime.datetime.strftime(issue_date, '%Y-%m-%d')
                elif i == 7:
                    memo_no = row[i]
                elif i == 8:
                    subject = row[i]
                elif i == 9:
                    total_provision = row[i]
                elif i == 10:
                    type = row[i]
                elif i == 11:
                    released_budget = row[i]
                elif i == 12:
                    comments = row[i]
            # print('budget_amount -> ', budget_amount, ' office_id -> ', office_id, 'fy -> ', financial_year, ' fdf -> ',
            #      fund_disburse_from, 'in -> ', installment_no, 'id -> ', issue_date, ' mn -> ', memo_no, ' s -> ',
            #      subject,
            #      'tp -> ', total_provision)
            office = Office.objects.get(pk=int(office_id))
            objects.append({'budget_amount': budget_amount, 'office': office, 'financial_year': financial_year,
                            'fund_disburse_from': fund_disburse_from, 'installment_no': installment_no,
                            'issue_date': issue_date, 'memo_no': memo_no, 'subject': subject,
                            'total_provision': total_provision, 'type': type, 'comments': comments,
                            'released_budget': released_budget})
            if budget_amount == '':
                raise ValidationError("Budget amount of " + office.name + " is empty. Please provide an amount.")
            total_amount += int(budget_amount)
            # Budget.objects.create(budget_amount=budget_amount, office=office, financial_year=financial_year,
            #                       fund_disburse_from=fund_disburse_from, installment_no=installment_no,
            #                       issue_date=issue_date, memo_no=memo_no, subject=subject,
            #                       total_provision=total_provision, type=type)
    # # print('total_amount', total_amount)
    # # print(objects)
    if int(released_budget) != int(total_amount) + deficit:
        raise ValidationError("Total budget amount should be equal to released budget.")
    for row in objects:
        Budget.objects.create(budget_amount=row['budget_amount'], office=row['office'],
                              financial_year=row['financial_year'],
                              fund_disburse_from=row['fund_disburse_from'], installment_no=row['installment_no'],
                              issue_date=row['issue_date'], memo_no=row['memo_no'], subject=row['subject'],
                              total_provision=row['total_provision'], type=row['type'], comments=row['comments'],
                              released_budget=row['released_budget'])
        total_row += 1
    return Response({'status': '200', 'error_message': '', 'total_amount': total_amount, 'row_count': total_row})


# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------- Announcement ----------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
@login_required(login_url='/')
def create_announcement(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'announcement/create_announcement.html', {'user_permissions': user_permissions})


@login_required(login_url='/')
def create_announcement_for_homepage(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'announcement/create_announcement_for_homepage.html', {'user_permissions': user_permissions})


def announcements(request):
    user_permissions = list(
        request.user.profile.role.permission.values_list('code', flat=True)) if request.user.is_authenticated else []
    return render(request, 'announcement/announcements.html', {'user_permissions': user_permissions})


def announcement_detail(request, id):
    announcement = Announcement.objects.get(pk=id)
    # m = announcement.attachment.name
    # pdf = False
    # if m.endswith('.pdf'):
    #     pdf = True
    if request.user.is_authenticated and (
            'notice_admin' in list(
        request.user.profile.role.permission.values_list('code', flat=True)) or request.user.profile.office.id in list(
        announcement.office.all().values_list('id', flat=True))):
        user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
        attachments = announcement.announcement_attachment.all()
        announcement_status = AnnouncementStatus.objects.filter(announcement=announcement)
        seen_office_list = announcement_status.values_list('office__name', flat=True)
        return render(request, 'announcement/announcement_details.html',
                      {'announcement': announcement, 'attachments': attachments,
                       'seen': seen_office_list, 'user_permissions': user_permissions})
    elif request.user.is_authenticated and announcement.for_homepage == 1:
        user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
        attachments = announcement.announcement_attachment.all()
        announcement_status = AnnouncementStatus.objects.filter(announcement=announcement)
        seen_office_list = announcement_status.values_list('office__name', flat=True)
        return render(request, 'announcement/announcement_details.html',
                      {'announcement': announcement, 'attachments': attachments,
                       'seen': seen_office_list, 'user_permissions': user_permissions})
    elif request.user.is_anonymous and announcement.for_homepage == 1:
        # user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
        attachments = announcement.announcement_attachment.all()
        return render(request, 'announcement/announcement_details.html',
                      {'announcement': announcement, 'attachments': attachments, 'user_permissions': []})
    else:
        return render(request, '404/404_body.html')


@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,))
def generate_budget_csv(request):
    # print(request.data)
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'

    writer = csv.writer(response)
    writer.writerow(
        ['Budget Amount', 'Office Name', 'District', 'Financial Year', 'Fund Disburse From', 'Installment No',
         'Issue Date', 'Memo No', 'Subject', 'Total Provision', 'Type', 'Released Budget', 'Comments', 'Office ID'])
    qs = Office.objects.all()
    organization = request.data.get('organization')
    office_category = request.data.get('office_category')
    # region = request.data.get('region')
    # district = request.data.get('district')
    region_list = request.data.getlist('region_list')
    district_list = request.data.getlist('district_list')
    excluded_office_list = request.data.getlist('excluded_office_list')
    fund_disburse_from = request.data.get('fund_disburse_from')
    issue_date = request.data.get('issue_date')
    total_provision = request.data.get('total_provision')
    released_budget = request.data.get('released_budget')
    installment_no = request.data.get('installment_no')
    subject = request.data.get('subject')
    memo_no = request.data.get('memo_no')
    financial_year = request.data.get('financial_year')
    comments = request.data.get('comments')

    if organization:
        qs = qs.filter(organization=organization)
    if office_category:
        qs = qs.filter(office_category=office_category)
    # if region:
    #     qs = qs.filter(region__id=region)
    # if district:
    #     qs = qs.filter(district__id=district)
    if region_list:
        qs = qs.filter(region__id__in=region_list)
    if district_list and 'all' not in district_list:
        qs = qs.filter(district__id__in=district_list)
    if excluded_office_list:
        qs = qs.exclude(id__in=excluded_office_list)

    # # print(qs.values_list('district', flat=True))
    qs = qs.order_by('district__name')
    # # print(qs.values_list('district', flat=True))
    for row in qs:
        writer.writerow(
            ['', row.name, row.district, financial_year, fund_disburse_from, installment_no, issue_date, memo_no,
             subject,
             total_provision, "National", released_budget, comments, row.id])

    return response
    # return Response({'status': '200', 'error_message': '', 'csv':response})


@login_required(login_url='/')
def issue_title(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'issue/issue-title.html', {'user_permissions': user_permissions})


# def get_issue_report(request):
#     response = issue_report(request)
#     return response
def get_issue_filter(request):
    qs = Issue.objects.all()

    updated_at_from = request.GET.get('updated_at_from')
    updated_at_to = request.GET.get('updated_at_to')
    org_or_off_cat = request.GET.get('parameter')
    seen_status = request.GET.get('seen_status')
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))

    if org_or_off_cat:
        if org_or_off_cat == 'LGED' or org_or_off_cat == 'e-GP LAB':
            qs = qs.filter(raised_by__profile__office__organization=org_or_off_cat)
        else:
            qs = qs.filter(raised_by__profile__office__office_category=org_or_off_cat)
    if request.GET.get('status') and request.GET.get('status') == 'pending':
        # if request.user.profile.office.office_category == "LGED HQ":
        #     qs = qs.exclude(user_end_action=2)
        # else:
        qs = qs.exclude(user_end_action=2)
    if request.GET.get('status') and request.GET.get('status') == 'solved':
        qs = qs.filter(user_end_action=2)
    if request.GET.get('item_id') and request.GET.get('category'):
        qs = qs.filter(item_id=request.GET.get('item_id'))
        qs_copy = qs
        qs = qs.filter(title__category=request.GET.get('category'))
        qs_copy = qs_copy.filter(other_category=request.GET.get('category'))
        qs = qs | qs_copy
    # if self.request.GET.get('search_action'):
    #     qs = qs.filter(user_end_action=self.request.GET.get('search_action'))
    if request.GET.get('search_category'):
        qs_copy = qs
        qs = qs.filter(title__category=request.GET.get('search_category'))
        qs_copy = qs_copy.filter(other_category=request.GET.get('search_category'))
        qs = qs | qs_copy
    if 'issue_admin' not in user_permissions:
        qs = qs.filter(raised_by=request.user)

    if updated_at_from:
        updated_from = datetime.datetime.strptime(updated_at_from, "%Y-%m-%d").date()
        qs = qs.filter(updated_at__gte=updated_from)
    if updated_at_to:
        updated_to = datetime.datetime.strptime(updated_at_to, "%Y-%m-%d").date()
        updated_to += datetime.timedelta(days=1)
        qs = qs.filter(updated_at__lte=updated_to)
    if seen_status == 'false':
        qs = qs.filter(seen_status=False)
    return qs.filter().order_by('-created_at')


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def issue_report1(request):
    response = []
    issues = get_issue_filter(request)
    issue_categories = IssueTitle.objects.values_list('category', flat=True).distinct()
    for issue_category in issue_categories:
        obj = {}
        issues_for_issue_category = issues.filter(title__category=issue_category)
        obj["category"] = issue_category
        obj["no_of_issues"] = issues_for_issue_category.count()
        obj["pending_issue_count"] = issues_for_issue_category.filter(user_end_action=1).count()
        obj["solved_issue_count"] = issues_for_issue_category.filter(user_end_action=2).count()
        solved_issues = issues_for_issue_category.filter(user_end_action=2)
        total_solving_time = solved_issues.aggregate(total_solving_time=Sum(F('updated_at') - F('created_at')))[
            'total_solving_time']
        if solved_issues.count() == 0:
            obj["avg_solving_time"] = '---'
        else:
            avg_solving_time = total_solving_time / solved_issues.count()
            days, hours, minutes = avg_solving_time.days, avg_solving_time.seconds // 3600, avg_solving_time.seconds // 60 % 60
            obj["avg_solving_time"] = str(days) + ' day ' + str(hours) + ' hours ' + str(minutes) + ' minutes'
        response.append(obj)

    return Response(response)


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def issue_report2(request):
    response = []
    issues = get_issue_filter(request)
    # print('Issue', issues.count(), Issue.objects.all().count(), request.GET.get('search_category'))
    # categories = Office.objects.values_list('office_category', flat=True).distinct()
    categories = ['LGED', 'e-GP LAB', 'CITY CORPORATION OFFICES', 'ZILA PARISHAD OFFICES', 'UPAZILA PARISHAD OFFICES',
                  'PAURASHAVA OFFICES']
    for category in categories:
        obj = {}
        if category == 'LGED' or category == 'e-GP LAB':
            issues_for_office_category = issues.filter(raised_by__profile__office__organization=category)
        else:
            issues_for_office_category = issues.filter(raised_by__profile__office__office_category=category)
        obj["category"] = category
        obj["no_of_issues"] = issues_for_office_category.count()
        obj["pending_issue_count"] = issues_for_office_category.filter(user_end_action=1).count()
        obj["solved_issue_count"] = issues_for_office_category.filter(user_end_action=2).count()
        solved_issues = issues_for_office_category.filter(user_end_action=2)
        total_solving_time = solved_issues.aggregate(total_solving_time=Sum(F('updated_at') - F('created_at')))[
            'total_solving_time']
        if solved_issues.count() == 0:
            obj["avg_solving_time"] = '---'
        else:
            avg_solving_time = total_solving_time / solved_issues.count()
            days, hours, minutes = avg_solving_time.days, avg_solving_time.seconds // 3600, avg_solving_time.seconds // 60 % 60
            obj["avg_solving_time"] = str(days) + ' day ' + str(hours) + ' hours ' + str(minutes) + ' minutes'
        response.append(obj)

    return Response(response)


@login_required(login_url='/')
def pending_issue_list(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'issue/issue-list.html',
                  {'category': '', 'item_id': '', 'action': 'pending', 'user_permissions': user_permissions})


@login_required(login_url='/')
def solved_issue_list(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'issue/issue-list.html',
                  {'category': '', 'item_id': '', 'action': 'solved', 'user_permissions': user_permissions})


@login_required(login_url='/')
def item_issue(request, category, item_id):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'issue/issue-list.html',
                  {'category': category, 'item_id': item_id, 'action': 'pending', 'user_permissions': user_permissions})


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def issue_action(request):
    status = []
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    if 'issue_admin' in user_permissions:
        for s in Issue.ADMIN_ISSUE_ACTION:
            if s[0] != 0:
                status.append({'id': s[0], 'name': s[1]})
    else:
        for s in Issue.USER_ISSUE_ACTION:
            status.append({'id': s[0], 'name': s[1]})
    return Response(status)


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def title_category(request):
    category = []
    for s in IssueTitle.MODEL_CHOICES:
        category.append({'id': s[0], 'name': s[1]})

    return Response(category)
    # return Response({"data": IssueTitle.MODEL_CHOICES})


@login_required(login_url='/')
def training_name(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'settings/training_name.html', {'user_permissions': user_permissions})


@login_required(login_url='/')
def training_category(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'settings/training_category.html', {'user_permissions': user_permissions})


@login_required(login_url='/')
def home_page_image(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'settings/home_page_image.html', {'user_permissions': user_permissions})


@login_required(login_url='/')
def home_page_writing(request, category):
    no = HomepageWriting.objects.count()
    no == 0 and HomepageWriting.objects.create(pk=1)
    if category == 'about_lgis':
        label = 'About LGIs'
    elif category == 'about_lged':
        label = 'About LGED'
    elif category == 'about_dimappp':
        label = 'About DIMAPPP'
    elif category == 'contact':
        label = 'Contact'
    # obj = HomepageWriting.objects.first()
    # data = getattr(obj, category)
    user_permissions = list(
        request.user.profile.role.permission.values_list('code', flat=True)) if request.user.is_authenticated else []
    return render(request, 'settings/home_page_writing.html',
                  {'category': category, 'label': label, 'user_permissions': user_permissions})


@login_required(login_url='/')
def important_link(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'settings/important_links.html', {'user_permissions': user_permissions})


@login_required(login_url='/')
def batch_number(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'settings/batch_number.html', {'user_permissions': user_permissions})


@login_required(login_url='/')
def from_announcement(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'settings/FromAnnouncement.html', {'user_permissions': user_permissions})


@login_required(login_url='/')
def publication_type(request):
    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    return render(request, 'settings/publication_type.html', {'user_permissions': user_permissions})


def get_office_filter(request, qs):
    type = request.GET.get('type')
    organization = request.GET.get('organization')
    office_category = request.GET.get('office_category')
    division = request.GET.get('division')
    region = request.GET.get('region')
    district = request.GET.get('district')
    upazilla = request.GET.get('upazilla')
    upazila_class = request.GET.get('class')
    post_code = request.GET.get('post_code')  # __icontains
    phone_no = request.GET.get('phone_no')
    fax_no = request.GET.get('fax_no')
    name = request.GET.get('name')
    id = request.GET.get('id')
    id_list = request.GET.get('id_list')
    office_id = request.GET.get('office')

    city_corporation = request.GET.get('city_corporation')
    updated_at_from = request.GET.get('updated_at_from')
    updated_at_to = request.GET.get('updated_at_to')

    organization_list = request.GET.get('organization_list')
    office_category_list = request.GET.get('office_category_list')
    region_list = request.GET.get('region_list')
    district_list = request.GET.get('district_list')
    office_list = request.GET.get('office_list')
    transfer = request.GET.get('transfer')
    public = request.GET.get('public')
    # # print(organization_list, organization_list.split(','))
    if request.user.is_anonymous and not office_category:
        return qs.filter(office_category='e-GP LAB OFFICES')
    if request.user.is_anonymous and office_category:
        qs = qs.filter(office_category=office_category)
    if public and not office_category:
        return qs.filter(office_category='e-GP LAB OFFICES')
    if public and office_category:
        qs = qs.filter(office_category=office_category)

    all = request.GET.get('all')
    filters = {}

    if request.user.is_authenticated:
        user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
        if 'office_admin' not in user_permissions and type != 'e-GP LAB' and transfer != '1' and public != '1':
            filters['id'] = request.user.profile.office.id

    if organization is not None:
        filters['organization'] = request.GET.get('organization')
    if office_category is not None:
        filters['office_category'] = request.GET.get('office_category')
    if division is not None:
        filters['division'] = request.GET.get('division')
    if region is not None:
        filters['region'] = request.GET.get('region')
    if district is not None:
        filters['district'] = district
    if upazilla is not None:
        filters['upazila'] = upazilla
    if upazila_class is not None:
        filters['pourashava_class'] = upazila_class
    if post_code is not None:
        filters['post_code__icontains'] = post_code
    if phone_no is not None:
        filters['phone_no__icontains'] = phone_no
    if fax_no is not None:
        filters['fax_no__icontains'] = fax_no
    if name is not None:
        filters['name'] = request.GET.get('name')
    if id is not None:
        filters['id'] = request.GET.get('id')
    if city_corporation is not None:
        filters['city_corporation'] = city_corporation
    if office_id:
        filters['id'] = office_id
    if id_list:
        filters['id__in'] = id_list.split(",")

    if organization_list:
        filters['organization__in'] = organization_list.split(",")
    if office_category_list:
        filters['office_category__in'] = office_category_list.split(",")
    if region_list:
        filters['region__in'] = region_list.split(",")
    if district_list:
        filters['district__in'] = district_list.split(",")
    if office_list:
        filters['name__in'] = office_list.split(',')

    if all is not None and all == 'true':
        filters = {}

    # print(filters)
    qs = qs.filter(**filters)

    if updated_at_from:
        updated_from = datetime.datetime.strptime(updated_at_from, "%Y-%m-%d").date()
        qs = qs.filter(updated_at__gte=updated_from)
    if updated_at_to:
        updated_to = datetime.datetime.strptime(updated_at_to, "%Y-%m-%d").date()
        updated_to += datetime.timedelta(days=1)
        qs = qs.filter(updated_at__lte=updated_to)
    return qs


def get_inv_filter(request, qs):
    organization = request.GET.get('organization')
    office_category = request.GET.get('office_category')
    region = request.GET.get('region')
    district = request.GET.get('district')
    office = request.GET.get('office')
    updated_at_from = request.GET.get('updated_at_from')
    updated_at_to = request.GET.get('updated_at_to')
    type_category_adv = request.GET.get('type_category_adv')
    type_adv = request.GET.get('type_adv')
    status_adv = request.GET.get('status_adv')
    procured_by_adv = request.GET.get('procured_by_adv')
    package_no_adv = request.GET.get('package_no_adv')
    id_adv = request.GET.get('id_adv')
    brand_name_adv = request.GET.get('brand_name_adv')
    model_no_adv = request.GET.get('model_no_adv')
    serial_no_adv = request.GET.get('serial_no_adv')
    supplied_quantity_adv = request.GET.get('supplied_quantity_adv')
    warranty_period_adv = request.GET.get('warranty_period_adv')
    date_received_adv = request.GET.get('date_received_adv')
    asset_no_adv = request.GET.get('asset_no_adv')
    item = request.GET.get('item')

    raw = request.GET.get('raw')

    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    if 'inv_admin' not in user_permissions:
        qs = qs.filter(office=request.user.profile.office.id)

    if organization:
        qs = qs.filter(office__organization=organization)
    if office_category:
        qs = qs.filter(office__office_category=office_category)
    if region:
        qs = qs.filter(office__region=region)
    if district:
        qs = qs.filter(office__district=district)
    if office:
        qs = qs.filter(office=office)
    if type_category_adv:
        qs = qs.filter(device__type__type_category=type_category_adv)
    if type_adv:
        qs = qs.filter(device__type=type_adv)
    if status_adv:
        qs = qs.filter(status__id=status_adv)
    if procured_by_adv:
        qs = qs.filter(package_no__source__id=procured_by_adv)
    if package_no_adv:
        qs = qs.filter(package_no__id=package_no_adv)
    if id_adv:
        qs = qs.filter(id=id_adv)
    if updated_at_from:
        updated_from = datetime.datetime.strptime(updated_at_from, "%Y-%m-%d").date()
        qs = qs.filter(updated_at__gte=updated_from)
    if updated_at_to:
        updated_to = datetime.datetime.strptime(updated_at_to, "%Y-%m-%d").date()
        updated_to += datetime.timedelta(days=1)
        qs = qs.filter(updated_at__lte=updated_to)

    if raw:
        qs = qs.filter(date_of_delivery__isnull=True)
    if warranty_period_adv:
        warranty_period = datetime.datetime.strptime(warranty_period_adv, "%Y-%m-%d").date()
        qs = qs.filter(device__validity__lte=warranty_period)
    if date_received_adv:
        date_received = datetime.datetime.strptime(date_received_adv, "%Y-%m-%d").date()
        qs = qs.filter(date_of_delivery=date_received)
    if brand_name_adv:
        qs = qs.filter(device__brand_name__icontains=brand_name_adv)
    if model_no_adv:
        qs = qs.filter(device__model_no__icontains=model_no_adv)
    if asset_no_adv:
        inv_product = InventoryProducts.objects.filter(asset_no=asset_no_adv).values('inventory__id').distinct()
        qs = qs.filter(id__in=inv_product)
    if serial_no_adv:
        inv_product = InventoryProducts.objects.filter(serial_no__icontains=serial_no_adv).values(
            'inventory__id').distinct()
        qs = qs.filter(id__in=inv_product)
    if supplied_quantity_adv:
        qs = qs.filter(supplied_quantity=supplied_quantity_adv)
    if item:
        qs = qs.filter(device__type__type=item)
    return qs


def get_inv_report_ob(request):
    response = inv_report(request)
    return response.data[4].get("qs")


@login_required(login_url='/')
def update_supplied_quantity(request, id):
    try:
        inv = Inventory.objects.get(id=id)
        inv.supplied_quantity = InventoryProducts.objects.filter(inventory__id=id).count()
        inv.save()
        return HttpResponse(status=200)
    except Exception as e:
        return HttpResponse(status=500)


def get_inv_product_filter(request, qs):
    organization = request.GET.get('organization')
    office_category = request.GET.get('office_category')
    region = request.GET.get('region')
    district = request.GET.get('district')
    office = request.GET.get('office')
    updated_at_from = request.GET.get('updated_at_from')
    updated_at_to = request.GET.get('updated_at_to')
    type_category_adv = request.GET.get('type_category_adv')
    type_adv = request.GET.get('type_adv')
    status_adv = request.GET.get('status_adv')
    procured_by_adv = request.GET.get('procured_by_adv')
    package_no_adv = request.GET.get('package_no_adv')
    id_adv = request.GET.get('id_adv')
    brand_name_adv = request.GET.get('brand_name_adv')
    model_no_adv = request.GET.get('model_no_adv')
    serial_no_adv = request.GET.get('serial_no_adv')
    supplied_quantity_adv = request.GET.get('supplied_quantity_adv')
    warranty_period_adv = request.GET.get('warranty_period_adv')
    date_received_adv = request.GET.get('date_received_adv')
    asset_no_adv = request.GET.get('asset_no_adv')
    item = request.GET.get('item')
    cost_adv = request.GET.get('cost_adv')
    cost_below_adv = request.GET.get('cost_below_adv')
    cost_above_adv = request.GET.get('cost_above_adv')
    designation_adv = request.GET.get('designation_adv')

    raw = request.GET.get('raw')
    report_type = request.GET.get('report_type')

    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    if 'inv_admin' not in user_permissions:
        qs = qs.filter(inventory__office=request.user.profile.office.id)
    if organization:
        qs = qs.filter(inventory__office__organization=organization)
    if office_category:
        qs = qs.filter(inventory__office__office_category=office_category)
    if region:
        qs = qs.filter(inventory__office__region=region)
    if district:
        qs = qs.filter(inventory__office__district=district)
    if office:
        qs = qs.filter(inventory__office=office)
    if type_category_adv:
        qs = qs.filter(inventory__device__type__type_category=type_category_adv)
    if type_adv:
        qs = qs.filter(inventory__device__type=type_adv)
    if status_adv:
        qs = qs.filter(inventory__status__id=status_adv)
    if procured_by_adv:
        qs = qs.filter(inventory__package_no__source__id=procured_by_adv)
    if package_no_adv:
        qs = qs.filter(inventory__package_no__id=package_no_adv)
    if id_adv:
        qs = qs.filter(inventory__id=id_adv)
    if updated_at_from:
        updated_from = datetime.datetime.strptime(updated_at_from, "%Y-%m-%d").date()
        qs = qs.filter(inventory__updated_at__gte=updated_from)
    if updated_at_to:
        updated_to = datetime.datetime.strptime(updated_at_to, "%Y-%m-%d").date()
        updated_to += datetime.timedelta(days=1)
        qs = qs.filter(inventory__updated_at__lte=updated_to)

    if raw:
        qs = qs.filter(inventory__date_of_delivery__isnull=True)
    if warranty_period_adv:
        warranty_period = datetime.datetime.strptime(warranty_period_adv, "%Y-%m-%d").date()
        qs = qs.filter(inventory__device__validity__lte=warranty_period)
    if date_received_adv:
        date_received = datetime.datetime.strptime(date_received_adv, "%Y-%m-%d").date()
        qs = qs.filter(inventory__date_of_delivery=date_received)
    if brand_name_adv:
        qs = qs.filter(inventory__device__brand_name__icontains=brand_name_adv)
    if model_no_adv:
        qs = qs.filter(inventory__device__model_no__icontains=model_no_adv)
    if asset_no_adv:
        qs = qs.filter(asset_no__icontains=asset_no_adv)
    if serial_no_adv:
        qs = qs.filter(serial_no__icontains=serial_no_adv)
    if cost_adv:
        qs = qs.filter(cost__exact=cost_adv)
    if cost_below_adv:
        qs = qs.filter(cost__lt=cost_below_adv)
    if cost_above_adv:
        qs = qs.filter(cost__isnull=False, cost__gt=cost_above_adv)
    if designation_adv:
        qs = qs.filter(user_designation=designation_adv)
    if supplied_quantity_adv:
        qs = qs.filter(inventory__supplied_quantity=supplied_quantity_adv)
    if item:
        qs = qs.filter(inventory__device__type__type=item)
    if report_type:
        offices = Office.objects.annotate(inv_count=Count('inventory__id'),
                                          inv_updated_count=Sum(
                                              Case(When(Q(inventory__inventoryproducts__serial_no__isnull=False) &
                                                        Q(inventory__date_of_delivery__isnull=False), then=1),
                                                   default=0), output_field=IntegerField()))
        # does an or over all rows
        offices = get_office_filter(request, offices)
        partially_updated_offices = offices.filter(~Q(inv_count=F('inv_updated_count')), ~Q(inv_updated_count=0)). \
            values_list('id', flat=True)
        fully_updated_offices = offices.filter(Q(inv_count=F('inv_updated_count')), ~Q(inv_updated_count=0)). \
            values_list('id', flat=True)
        not_updated_offices = offices.filter(~Q(inv_count=F('inv_updated_count')), Q(inv_updated_count=0)). \
            values_list('id', flat=True)
        if report_type == 'p_office':
            qs = qs.filter(inventory__office_id__in=partially_updated_offices)
        elif report_type == 'n_inv':
            qs = qs.filter(Q(inventory__date_of_delivery__isnull=True) |
                           Q(inventory__inventoryproducts__serial_no__isnull=True))
        elif report_type == 'f_office':
            qs = qs.filter(inventory__office_id__in=fully_updated_offices)
        elif report_type == 'n_office':
            qs = qs.filter(inventory__office_id__in=not_updated_offices)
    return qs


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def inv_report(request):
    report_type = request.GET.get('report_type')
    response = []

    offices = Office.objects.annotate(inv_count=Count('inventory__id'),
                                      inv_updated_count=Sum(
                                          Case(When(Q(inventory__inventoryproducts__serial_no__isnull=False) &
                                                    Q(inventory__date_of_delivery__isnull=False), then=1),
                                               default=0), output_field=IntegerField()))
    # does an or over all rows
    offices = get_office_filter(request, offices)
    partially_updated_offices = offices.filter(~Q(inv_count=F('inv_updated_count')), ~Q(inv_updated_count=0)). \
        values_list('id', flat=True)
    fully_updated_offices = offices.filter(Q(inv_count=F('inv_updated_count')), ~Q(inv_updated_count=0)). \
        values_list('id', flat=True)
    not_updated_offices = offices.filter(~Q(inv_count=F('inv_updated_count')), Q(inv_updated_count=0)). \
        values_list('id', flat=True)

    inventory_products = InventoryProducts.objects.all()
    qs = get_inv_product_filter(request, inventory_products)
    not_updated_inv = qs.filter(Q(inventory__date_of_delivery__isnull=True) |
                                Q(inventory__inventoryproducts__serial_no__isnull=True))

    # for device type count
    grp_inventories = qs.values('inventory__device__type__type'). \
        annotate(count=Coalesce(Count('inventory__device__type__type'), 0))

    device_type_count = {}
    for type in grp_inventories:
        if type.get("inventory__device__type__type"):
            device_type_count[type.get("inventory__device__type__type")] = type.get("count")

    response.append({"partially": partially_updated_offices.count()})
    response.append({"fully": fully_updated_offices.count()})
    response.append({"not_updated": not_updated_offices.count()})
    response.append({"inv_not_updated": not_updated_inv.count()})

    if report_type == 'p_office':
        response.append({"qs": qs})
        return Response(response)
    elif report_type == 'n_inv':
        response.append({"qs": not_updated_inv})
        return Response(response)
    elif report_type == 'n_office':
        response.append({"qs": qs})
        return Response(response)
    elif report_type == 'f_office':
        response.append({"qs": qs})
        return Response(response)
    else:
        response.append({'device_type_count': device_type_count})
        return Response(response)


def get_app_filter(request, qs):
    organization = request.GET.get('organization')
    office_category = request.GET.get('office_category')
    region = request.GET.get('region')
    district = request.GET.get('district')
    office = request.GET.get('office')
    updated_at_from = request.GET.get('updated_at_from')
    updated_at_to = request.GET.get('updated_at_to')

    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    if 'tender_admin' not in user_permissions:
        qs = qs.filter(office=request.user.profile.office.id)

    if organization:
        qs = qs.filter(office__organization=organization)
    if office_category:
        qs = qs.filter(office__office_category=office_category)
    if region:
        qs = qs.filter(office__region=region)
    if district:
        qs = qs.filter(office__district=district)
    if office:
        qs = qs.filter(office=office)
    if updated_at_from:
        updated_from = datetime.datetime.strptime(updated_at_from, "%Y-%m-%d").date()
        qs = qs.filter(updated_at__gte=updated_from)
    if updated_at_to:
        updated_to = datetime.datetime.strptime(updated_at_to, "%Y-%m-%d").date()
        updated_to += datetime.timedelta(days=1)
        qs = qs.filter(updated_at__lte=updated_to)
    return qs


def get_package_filter(request, qs):
    organization = request.GET.get('organization')
    office_category = request.GET.get('office_category')
    region = request.GET.get('region')
    district = request.GET.get('district')
    office = request.GET.get('office')
    updated_at_from = request.GET.get('updated_at_from')
    updated_at_to = request.GET.get('updated_at_to')
    app = request.GET.get('app')
    package_from_lot = request.GET.get('package_from_lot')
    lot_exist = request.GET.get('does_lot_exist')

    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    if 'tender_admin' not in user_permissions:
        qs = qs.filter(app_id__office=request.user.profile.office.id)

    if organization:
        qs = qs.filter(app_id__office__organization=organization)
    if office_category:
        qs = qs.filter(app_id__office__office_category=office_category)
    if region:
        qs = qs.filter(app_id__office__region=region)
    if district:
        qs = qs.filter(app_id__office__district=district)
    if office:
        qs = qs.filter(app_id__office=office)
    if updated_at_from:
        updated_from = datetime.datetime.strptime(updated_at_from, "%Y-%m-%d").date()
        qs = qs.filter(updated_at__gte=updated_from)
    if updated_at_to:
        updated_to = datetime.datetime.strptime(updated_at_to, "%Y-%m-%d").date()
        updated_to += datetime.timedelta(days=1)
        qs = qs.filter(updated_at__lte=updated_to)
    if app:
        qs = qs.filter(app_id__id=app)
    if package_from_lot:
        pack = Package.objects.get(id=package_from_lot)
        qs = qs.filter(app_id=pack.app_id)
    if lot_exist:
        qs = qs.filter(lots__lot_description__isnull=False)
    # qs = qs.lots.all()
    return qs.distinct()


def get_tender_filter(request, qs):
    organization = request.GET.get('organization')
    office_category = request.GET.get('office_category')
    region = request.GET.get('region')
    district = request.GET.get('district')
    office = request.GET.get('office')
    updated_at_from = request.GET.get('updated_at_from')
    updated_at_to = request.GET.get('updated_at_to')
    package = request.GET.get('package')
    status = request.GET.get('status')

    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    if 'tender_admin' not in user_permissions:
        qs = qs.filter(package__app_id__office=request.user.profile.office.id)

    if organization:
        qs = qs.filter(package__app_id__office__organization=organization)
    if office_category:
        qs = qs.filter(package__app_id__office__office_category=office_category)
    if region:
        qs = qs.filter(package__app_id__office__region=region)
    if district:
        qs = qs.filter(package__app_id__office__district=district)
    if office:
        qs = qs.filter(package__app_id__office=office)
    if updated_at_from:
        updated_from = datetime.datetime.strptime(updated_at_from, "%Y-%m-%d").date()
        qs = qs.filter(updated_at__gte=updated_from)
    if updated_at_to:
        updated_to = datetime.datetime.strptime(updated_at_to, "%Y-%m-%d").date()
        updated_to += datetime.timedelta(days=1)
        qs = qs.filter(updated_at__lte=updated_to)
    if package:
        qs = qs.filter(package__id=package)
    if status and status == 'Ongoing':
        qs = qs.exclude(Q(status='Cancelled') | Q(status='Rejected'))
    if status and status == 'Cancel':
        qs = qs.filter(status='Cancelled')
    if status and status == 'Reject':
        qs = qs.filter(status='Rejected')
    return qs


def get_lot_filter(request, qs):
    organization = request.GET.get('organization')
    office_category = request.GET.get('office_category')
    region = request.GET.get('region')
    district = request.GET.get('district')
    office = request.GET.get('office')
    updated_at_from = request.GET.get('updated_at_from')
    updated_at_to = request.GET.get('updated_at_to')
    package = request.GET.get('package')
    status = request.GET.get('status')
    type = request.GET.get('type')
    budget_type = request.GET.get('budget_type')

    user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
    if 'tender_admin' not in user_permissions:
        qs = qs.filter(package_no__app_id__office=request.user.profile.office.id)

    if organization:
        qs = qs.filter(package_no__app_id__office__organization=organization)
    if office_category:
        qs = qs.filter(package_no__app_id__office__office_category=office_category)
    if region:
        qs = qs.filter(package_no__app_id__office__region=region)
    if district:
        qs = qs.filter(office__district=district)
    if office:
        qs = qs.filter(package_no__app_id__office=office)
    if updated_at_from:
        updated_from = datetime.datetime.strptime(updated_at_from, "%Y-%m-%d").date()
        qs = qs.filter(updated_at__gte=updated_from)
    if updated_at_to:
        updated_to = datetime.datetime.strptime(updated_at_to, "%Y-%m-%d").date()
        updated_to += datetime.timedelta(days=1)
        qs = qs.filter(updated_at__lte=updated_to)
    if package:
        qs = qs.filter(package_no__id=package)
    if status:
        qs = qs.filter(package_no__status=status)
    if type:
        qs = qs.filter(package_no__app_id__type=type)
    if budget_type:
        qs = qs.filter(package_no__app_id__budget_type__type=budget_type)
    return qs


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def app_report(request):
    response = []
    qs = Lot.objects.all()
    qs = get_lot_filter(request, qs)
    qs = qs.filter(package_no__status='Approved')

    qs_app = APP.objects.all()
    qs_app = get_app_filter(request, qs_app)
    qs_app_prev = qs_app

    qs_tender = Tender.objects.all()
    qs_tender = get_tender_filter(request, qs_tender)

    # for app in qs_app:
    #     # print(app.lot_count, app.contract_count)

    # # print(qs.count())
    # # print(qs.distinct('package_no').count())
    # # print(qs.filter(package_no__app_id__type='e-GP').distinct('package_no').count())
    # # print(qs.filter(package_no__app_id__type='Off-line').distinct('package_no').count())

    response.append({"total": qs.distinct('package_no').count()})

    response.append({"e_gp": qs.filter(package_no__app_id__type='e-GP').distinct('package_no').count()})
    response.append({"offline": qs.filter(package_no__app_id__type='Off-line').distinct('package_no').count()})

    response.append({"e_gp_cost": qs.filter(package_no__app_id__type='e-GP').aggregate(Sum('cost'))})
    response.append({"offline_cost": qs.filter(package_no__app_id__type='Off-line').aggregate(Sum('cost'))})

    response.append(
        {"revenue": qs.filter(package_no__app_id__budget_type__type='Revenue').distinct('package_no').count()})
    response.append(
        {"development": qs.filter(package_no__app_id__budget_type__type='Development').distinct('package_no').count()})
    response.append(
        {"own_fund": qs.filter(package_no__app_id__budget_type__type='Own Fund').distinct('package_no').count()})

    response.append(
        {"revenue_cost": qs.filter(package_no__app_id__budget_type__type='Revenue').aggregate(Sum('cost'))})
    response.append(
        {"development_cost": qs.filter(package_no__app_id__budget_type__type='Development').aggregate(Sum('cost'))})
    response.append(
        {"own_fund_cost": qs.filter(package_no__app_id__budget_type__type='Own Fund').aggregate(Sum('cost'))})

    response.append({"app": qs_app.filter(package__tender__isnull=True).distinct('id').count()})
    response.append({"tender": qs_tender.filter(~Q(tender_status='Approved')).count()})
    # qs_app = qs_app.filter(package__tender__newcontract__isnull=False, lot_count__gt=F('contract_count'))
    qs_app = qs_app.annotate(lot_count=Count('package__lots'),
                             lot_cost=Coalesce(Sum('package__lots__cost'), 0))
    incomplete_contract_count = 0
    incomplete_contract_cost = 0
    total_contract_count = NewContract.objects.all().count()
    total_contract_cost = NewContract.objects.all().aggregate(contract_cost=Coalesce(Sum('contract_amount'), 0))[
        'contract_cost']
    for app in qs_app:
        incomplete_contract_count += \
            qs_app.filter(id=app.id).aggregate(contract_count=Count('package__tender__newcontract'))['contract_count']
        incomplete_contract_cost += qs_app.filter(id=app.id).aggregate(
            contract_cost=Coalesce(Sum('package__tender__newcontract__contract_amount'), 0))['contract_cost']
    # contract_count = \
    #     qs_app.filter(package__tender__newcontract__isnull=False, lot_count__gt=F('contract_count')).aggregate(
    #         x=Coalesce(Sum('contract_count'), 0))['x']
    response.append({"contract": incomplete_contract_count})

    lot_cost = 0
    qs_temp = qs_app.filter(package__tender__isnull=True)
    for temp in qs_temp:
        qs_temp1 = temp.package_set.all()
        for temp1 in qs_temp1:
            lot_cost += temp1.lots.all().aggregate(cost__sum=Coalesce(Sum('cost'), 0))['cost__sum']

    # response.append({"app_cost": qs_app.filter(package__tender__isnull=True).aggregate(Sum('lot_cost'))})
    response.append({"app_cost": {'lot_cost__sum': lot_cost}})
    response.append({"tender_cost": qs_tender.filter(~Q(tender_status='Approved')).aggregate(
        tender_cost=Coalesce(Sum('tendercost__cost'), 0))})
    response.append({"contract_cost": incomplete_contract_cost})

    response.append({"app_total": qs_app_prev.distinct('id').count()})
    response.append({"tender_total": qs_tender.count()})
    response.append({"contract_total": total_contract_count})

    response.append({"app_total_cost": qs_app.aggregate(Sum('lot_cost'))})
    response.append({"tender_total_cost": qs_tender.aggregate(tender_total_cost=Coalesce(Sum('tendercost__cost'), 0))})
    response.append({"contract_total_cost": total_contract_cost})

    #
    # response.append({"tender": qs_tender.filter(~Q(tender_status='Approved')).count()})
    # qs_app = qs_app.annotate(lot_count=Count('package__lots'), contract_count=Count('package__tender__newcontract'))
    # contract_count = \
    #     qs_app.filter(package__tender__newcontract__isnull=False, lot_count__gt=F('contract_count')).aggregate(
    #         x=Coalesce(Sum('contract_count'), 0))['x']

    return Response(response)


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def tender_report(request):
    response = []
    qs = Tender.objects.all()
    qs = get_lot_filter(request, qs)

    response.append({"total": qs.count()})
    response.append({"e_gp": qs.filter(package__app_id__type='e-GP').count()})
    response.append({"offline": qs.filter(package__app_id__type='Off-line').count()})
    return Response(response)


# this api is used to generate Request Password request #Saiful
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def password_request_report(request):
    report_type = request.GET.get('report_type')
    start = request.GET.get('start')
    end = request.GET.get('end')
    day = request.GET.get('day')

    organization = request.GET.get('organization')
    office_category = request.GET.get('office_category')
    division = request.GET.get('division')
    region = request.GET.get('region')
    district = request.GET.get('district')
    upazilla = request.GET.get('upazilla')
    e_gp_id = request.GET.get('e_gp_id')
    office = request.GET.get('office')
    designation = request.GET.get('designation')

    previous_day = datetime.date.today() - datetime.timedelta(1)

    if end:
        end = datetime.datetime.strptime(end, "%Y-%m-%d") + datetime.timedelta(days=1)

    if report_type and report_type == 'domain_report':
        reports = PasswordRequest.objects.values('type', 'status').annotate(count=Cast(Count('status'), IntegerField()))

        if organization:
            reports = reports.filter(user__profile__office__organization=organization)
        if office_category:
            reports = reports.filter(user__profile__office__office_category=office_category)
        if division:
            reports = reports.filter(user__profile__office__division=division)
        if region:
            reports = reports.filter(user__profile__office__region=region)
        if district:
            reports = reports.filter(user__profile__office__district=district)
        if upazilla:
            reports = reports.filter(user__profile__office__upazila=upazilla)
        if office:
            reports = reports.filter(user__profile__office=office)
        if designation:
            reports = reports.filter(user__profile__designation=designation)
        if e_gp_id:
            reports = reports.filter(e_gp_id__icontains=e_gp_id)
        if start and end:
            reports = reports.filter(created_at__gte=start, created_at__lt=end)
        if start and (end is None or not end):
            reports = reports.filter(Q(created_at__gte=start))
        if (start is None or not start) and end:
            reports = reports.filter(Q(created_at__lt=start))
        if day == 'today':
            reports = reports.filter(Q(created_at__gte=date.today()))
        if day == 'previous_day':
            reports = reports.filter(Q(created_at__gte=previous_day), Q(created_at__lt=datetime.date.today()))
        generate_report = []
        main_domain = {
            'type': 'Main Domain',
            'Pending': 0,
            'Solved': 0
        }
        other_domain = {
            'type': 'Other Domain',
            'Pending': 0,
            'Solved': 0
        }
        all_domain = {
            'type': 'All Domain',
            'Pending': 0,
            'Solved': 0
        }

        pending = 0
        solved = 0

        for report in reports:
            if report['status'] == 'Pending':
                pending = pending + report['count']

            if report['status'] == 'Solved':
                solved = solved + report['count']

            if report['type'] == 'Main Domain':
                main_domain.update({'type': report['type'], report['status']: report['count']})

            if report['type'] == 'Other Domain':
                other_domain.update({'type': report['type'], report['status']: report['count']})

        all_domain.update({'type': 'All Domain', 'Pending': pending, 'Solved': solved})

        generate_report.append(all_domain)
        generate_report.append(main_domain)
        generate_report.append(other_domain)
        return Response(data={'data': generate_report}, status=200)

    if report_type and report_type == 'top_requesters':
        reports = PasswordRequest.objects.values(user_id=F('user'), name=F('user__first_name'),
                                                 username=F('user__username'),
                                                 district=F('user__profile__office__district__name'),
                                                 office_name=F('user__profile__office__name'),
                                                 request_id=F('e_gp_id'), domain_type=F('type')).annotate(
            request=Count('e_gp_id')).filter(request__gte=2).order_by('request').reverse()

        if organization:
            reports = reports.filter(user__profile__office__organization=organization)
        if office_category:
            reports = reports.filter(user__profile__office__office_category=office_category)
        if division:
            reports = reports.filter(user__profile__office__division=division)
        if region:
            reports = reports.filter(user__profile__office__region=region)
        if district:
            reports = reports.filter(user__profile__office__district=district)
        if upazilla:
            reports = reports.filter(user__profile__office__upazila=upazilla)
        if office:
            reports = reports.filter(user__profile__office=office)
        if designation:
            reports = reports.filter(user__profile__designation=designation)
        if e_gp_id:
            reports = reports.filter(e_gp_id__icontains=e_gp_id)
        if start and end:
            reports = reports.filter(created_at__gte=start, created_at__lt=end)
        if start and (end is None or not end):
            reports = reports.filter(Q(created_at__gte=start))

        if (start is None or not start) and end:
            reports = reports.filter(Q(created_at__lt=start))
        if day == 'today':
            reports = reports.filter(Q(created_at__gte=date.today()))
        return Response(data={'data': reports}, status=200)

    return Response(status=404)


# specific office designation # Saiful
@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def specific_office_designation(request):
    if request.method == 'GET':
        office_id = request.GET.get('office_id')
        transfer_type = request.GET.get('transfer_type')
        multiassign_type = request.GET.get('multiassign_type')
        # specific office designation
        if office_id and transfer_type == 'both':
            profile = Profile.objects.filter(office=office_id).exclude(
                procurement_roles_lgis__role__icontains='Focal Point').exclude(
                procurement_roles__role__icontains='Focal Point')
            serializer = ProfileSerializer(profile, many=True)
            return JsonResponse(serializer.data, status=200, safe=False)

        if office_id and multiassign_type == 'to':
            profile = Profile.objects.filter(office=office_id, nid=None, is_temp_office_assign=False).exclude(
                procurement_roles_lgis__role__icontains='Focal Point').exclude(
                procurement_roles__role__icontains='Focal Point')

            # profile= list(profile)
            # print('profile prevoius ========= ', profile)
            # for x in profile:
            #     user = User.objects.get(profile=x)
            #     print('name ', user.first_name)
            #     if user.first_name is not None:
            #         profile.remove(x)

            # print('profile next ============= ', prof)
            serializer = ProfileSerializer(profile, many=True)
            return JsonResponse(serializer.data, status=200, safe=False)

        return JsonResponse(status=500)


# Get district from specific office # Saiful
@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def get_district_from_office_info(request):
    organization = request.GET.get('organization')
    office_category = request.GET.get('office_category')
    offices = Office.objects.exclude(Q(district__isnull=True))
    offices = offices.exclude(Q(division__isnull=True))
    offices = offices.exclude(Q(name__isnull=True))
    type = request.GET.get('type')
    division = request.GET.get('division')
    district = request.GET.get('district')
    office_id = request.GET.get('office')
    designation = request.GET.get('designation')

    if organization and organization != 'e-GP LAB':
        offices = offices.filter(organization__icontains=organization)

    if office_category:
        offices = offices.filter(office_category__icontains=office_category)

    data = []
    if offices and type == 'divisions':
        offices = offices.distinct('division__name')
        for office in offices:
            data.append({"id": office.division.id, "name": office.division.name})
        return Response(data=data, status=200)

    if offices and type == 'districts' and division:
        offices = offices.filter(division_id=division)
        offices = offices.distinct('district__name')
        for office in offices:
            data.append({"id": office.district.id, "name": office.district.name})
        return Response(data=data, status=200)

    if division:
        offices = offices.filter(division=division)

    if district:
        offices = offices.filter(district=district)

    if type == 'designation' and office_id:
        profiles = Profile.objects.filter(office_id=office_id)
        profiles = profiles.distinct('designation__designation')
        for profile in profiles:
            data.append({"id": profile.designation.id, "name": profile.designation.designation})
        return Response(data=data, status=200)

    if type == 'users' and office_id and designation:
        users = User.objects.filter(profile__office=office_id, profile__designation=designation)
        users = users.exclude(Q(profile__nid__isnull=True))
        users = users.exclude(Q(first_name__isnull=True))
        for user in users:
            data.append(
                {"id": user.id, "name": user.get_full_name(), 'designation': user.profile.designation.designation,
                 'designation_id': user.profile.designation.id})
        return Response(data=data, status=200)

    if type == 'users' and office_id:
        users = User.objects.filter(profile__office=office_id)
        users = users.exclude(Q(profile__nid__isnull=True))
        users = users.exclude(Q(first_name__isnull=True))
        for user in users:
            data.append(
                {"id": user.id, "name": user.get_full_name(), 'designation': user.profile.designation.designation,
                 'designation_id': user.profile.designation.id})
        return Response(data=data, status=200)

    if type == 'offices':
        for office in offices:
            data.append({"id": office.id, "name": office.name, 'organization': office.organization,
                         'office_category': office.office_category, 'district_id': office.district.id,
                         'district': office.district.name})
        return Response(data=data, status=200)

    return Response(data=[], status=202)


# email send and configuration # Saiful

def send_mail_to_user(user_id, training_id):
    try:
        connection = get_connection(host=settings.EMAIL_HOST, port=settings.EMAIL_PORT,
                                    username=settings.EMAIL_HOST_USER, password=settings.EMAIL_HOST_PASSWORD,
                                    use_tls=settings.EMAIL_USE_TLS)
        try:
            connection.open()
            # send mail to user
            try:
                training_user = TrainingUser.objects.get(user=user_id, training=training_id)
                if training_user and not training_user.status:
                    subject, from_email, to_e, cc = training_user.subject, training_user.from_e, training_user.to, ''
                    text_content = html.unescape(training_user.mail_body)
                    html_content = html.unescape(training_user.mail_body)
                    if to_e:
                        try:
                            to_e = eval(to_e)
                        except Exception as e:
                            to_e = [to_e]
                    else:
                        to_e = []

                    if cc:
                        try:
                            cc = eval(cc)
                        except Exception as e:
                            cc = [cc]
                    else:
                        cc = []

                    msg = EmailMultiAlternatives(subject=subject, body=text_content, from_email=from_email, to=to_e,
                                                 cc=cc,
                                                 connection=connection)

                    msg.attach_alternative(html_content, "text/html")
                    msg.send()
                    training_user.status = True
                    training_user.save()
            except TrainingUser.DoesNotExist or TrainingUser.MultipleObjectsReturned:
                print('Training User is not found')
            connection.close()
        except Exception as e:
            print('Email Error ', e.__str__())
    except Exception as e:
        print('Email Connection Exception is happened ', e.__cause__, e)


# Notify the training Users by EMAIL # Saiful
@api_view(['PUT'])
@permission_classes((permissions.IsAuthenticated,))
def notify_training_batch_participants(request):
    training_batch_id = request.data.get('batch_id')
    try:
        training_batch = TrainingBatch.objects.get(pk=training_batch_id)
        participants = TrainingUser.objects.filter(training=training_batch.id)
        if participants:
            for participant in participants:
                send_mail_to_user(participant.user.id, training_batch_id)
            training_batch.status = 4
            training_batch.save()
        else:
          raise  ValidationError('No participant found!')
    except TrainingBatch.DoesNotExist or TrainingBatch.MultipleObjectsReturned:
        raise ValidationError('Batch can not find')
    except Exception as ex:
        raise ValidationError('Something wrong to notify the participants')
    return Response(status=201)
