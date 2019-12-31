import logging
import os
import profile
from collections import OrderedDict
from itertools import chain

from django.core.paginator import Paginator
from django.db.models import Q, Sum, QuerySet, Count, Value, IntegerField, Case, When, F, ExpressionWrapper
import json
from django.db.models.fields.reverse_related import ForeignObjectRel, ManyToOneRel, ManyToManyRel, OneToOneRel
from django.http import JsonResponse

from rest_framework.decorators import api_view
from rest_framework.utils import json
from sqlite3.dbapi2 import Date

import django_filters
from django.contrib.auth import login
from django.db import transaction
from django.contrib.auth.hashers import make_password
from django.utils.datastructures import MultiValueDictKeyError
import html
from rest_framework import permissions
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
import datetime
from rest_framework import permissions
from lged import views
from conf import settings

from lged.api.v1.filters import CustomSearchFilter, CustomOrderingFilter
from lged.models import Profile, ProcurementRole, User, Designation, Division, Region, District, Upazila, Office, \
    Project, Tender, Inventory, ResourceCenter, TrainingBatch, Publication, Gallery, \
    CityCorporation, TransferHistory, InventoryFile, InventoryStatus, InventoryType, PackageNo, Devices, Source, \
    Supplier, SupportCenter, InventoryFileType, BudgetType, ProcurementNature, TypeOfEmergency, ProcMethod, ProcType, \
    OfficeType, ExternalMember, SourceOfFund, ApprovingAuthority, ContractStatus, APP, Package, Contract, \
    BudgetCommon, Budget, Announcement, IssueTitle, Lot, ContractPayment, Firm, Issue, IssueComment, \
    AnnouncementStatus, TrainingName, BatchNumber, TrainingUser, IssueAttachment, InventoryTypeCategory, \
    AnnouncementAttachment, AuditTrail, FundedBy, TenderCost, NewContract, HomePageImage, ResponsiveBidder, Payment, \
    MonthlyProgress, ExtOrg, PaymentTimeVariation, PaymentAmountVariation, TrainingCategory, InventoryProducts, \
    ColumnCustomization, FromAnnouncement, PublicationType, CommitteeType, FundDisburseFrom, PasswordRequest, \
    HomepageWriting, ImportantLinks, Role, InviteeOffice, Permission, ExtMemberInclusionHistory, \
    ExtMemberTransferHistory, AdminUsers, GovtUsers, ExpiredLink, TemporaryOffice, MultipleAssignHistory
from lged.serializers import UserSerializer, ProcurementRoleSerializer, DesignationSerializer, DivisionSerializer, \
    RegionSerializer, DistrictSerializer, UpazilaSerializer, OfficeSerializer, ProjectSerializer, TenderSerializer, \
    InventorySerializer, ResourceCenterSerializer, TrainingBatchSerializer, \
    PublicationSerializer, GallerySerializer, CityCorporationSerializer, TransferHistorySerializer, \
    InventoryFileSerializer, InventoryStatusSerializer, InventoryTypeSerializer, PackageNoSerializer, DevicesSerializer, \
    SourceSerializer, SupplierSerializer, SupportCenterSerializer, InventoryFileTypeSerializer, BudgetTypeSerializer, \
    ProcurementNatureSerializer, TypeOfEmergencySerializer, ProcMethodSerializer, ProcTypeSerializer, \
    SourceOfFundSerializer, ApprovingAuthoritySerializer, ContractStatusSerializer, APPSerializer, PackageSerializer, \
    ContractSerializer, AnnouncementSerializer, BudgetCommonSerializer, BudgetSerializer, \
    OfficeTypeSerializer, ExternalMemberSerializer, APPReportSerializer, \
    IssueTitleSerializer, LotSerializer, ContractPaymentSerializer, FirmSerializer, IssueSerializer, \
    AnnouncementStatusSerializer, TrainingNameSerializer, BatchNumberSerializer, TrainingUserSerializer, \
    InventoryTypeCategorySerializer, AnnouncementAttachmentSerializer, AuditTrailSerializer, FundedBySerializer, \
    TenderCostSerializer, NewContractSerializer, HomePageImageSerializer, ResponsiveBidderSerializer, PaymentSerializer, \
    MonthlyProgressSerializer, ExtOrgSerializer, PaymentAmountVariationSerializer, \
    PaymentTimeVariationSerializer, TrainingCategorySerializer, InventoryProductsSerializer, \
    ColumnCustomizationSerializer, FromAnnouncementSerializer, PublicationTypeSerializer, CommitteeTypeSerializer, \
    FundDisburseFromSerializer, PasswordRequestSerializer, HomePageWritingSerializer, ImportantLinkSerializer, \
    RoleSerializer, InviteeOfficeSerializer, PermissionSerializer, ExtMemberInclusionHistorySerializer, \
    ExtMemberTransferHistorySerializer, ExpiredLinkSerializer, TemporaryOfficeSerializer, \
    MultipleAssignHistorySerializer
from lged.tokens import CustomPasswordResetTokenGenerator
from lged.views import get_app_filter, get_lot_filter, get_tender_filter, get_inv_filter, get_office_filter, inv_report, \
    get_inv_report_ob, get_package_filter, get_issue_filter, get_budget_filter, get_contract_filter, \
    get_training_filter, get_inv_product_filter, get_user_transfer_data, office_users, designation

from django.template.loader import render_to_string

import conf.settings

error_logger = logging.getLogger('lged.error')
warning_logger = logging.getLogger('lged.warning')
console_logger = logging.getLogger('lged.console')
logger = logging.getLogger(__name__)


class LargeResultsSetPagination(LimitOffsetPagination):
    limit_query_param = 'length'
    offset_query_param = 'start'
    max_limit = 1000000

    def get_paginated_response(self, data):
        try:
            draw = self.request.query_params.get('draw')
        except MultiValueDictKeyError:
            draw = 1

        return Response(OrderedDict([
            ('recordsTotal', self.count),
            ('recordsFiltered', self.count),
            ('draw', draw),
            ('data', data)
        ]))


class BaseViewSet(viewsets.ModelViewSet):
    filter_backends = (CustomSearchFilter, CustomOrderingFilter)

    # def get_queryset(self):
    #     field = self.ordering_fields[int(self.request.GET.get('order[0][column]'))]
    #     if self.request.GET.get('order[0][dir]') == 'desc':
    #         field = '-' + field
    #     return super().get_queryset().order_by(field)

    def perform_create(self, serializer):
        super().perform_create(serializer)
        # # print("seralizer %", serializer)
        return serializer.instance

    def perform_update(self, serializer):
        serializer.save()
        return serializer.instance


class TemporaryOfficeViewSet(BaseViewSet):
    queryset = TemporaryOffice.objects.all()
    serializer_class = TemporaryOfficeSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()

        user_permissions = list(self.request.user.profile.role.permission.values_list('code',
                                                                                      flat=True)) if self.request.user.is_authenticated else [
            'user_admin']

        if 'user_admin' not in user_permissions and self.request.GET.get('office_id'):
            qs = qs.filter(office_id=self.request.GET.get('office_id'))

        return qs
        # return qs.filter(is_superuser=False).order_by('-profile__updated_at')

    def perform_destroy(self, instance):
        profile = Profile.objects.filter(office=instance.office_id, designation=instance.designation,
                                         is_temp_office_assign=True).update(is_temp_office_assign=False)
        instance.delete()


class UserViewSet(BaseViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    search_fields = (
        'id', 'profile__id', 'email', 'first_name', 'profile__personal_email', 'profile__official_email',
        'profile__mobile_no', 'profile__official_mobile_no',
        'profile__e_gp_user_id', 'profile__e_gp_user_id_lgis', 'profile__nid', 'profile__designation__designation',
        'profile__office__name', 'profile__office__division__name', 'profile__office__region__name',
        'profile__office__district__name', 'profile__office__upazila__name',
        'profile__procurement_roles__role', 'profile__procurement_roles_lgis__role', 'profile__gender',
        'profile__date_of_birth', 'profile__bengali_name')
    ordering_fields = (
        '', 'profile__office__name', 'profile__office__division__name', 'profile__office__region__name',
        'profile__office__district__name', 'profile__office__upazila__name', '', 'first_name', 'profile__bengali_name',
        'profile__designation__designation',
        'profile__mobile_no', 'profile__official_mobile_no', 'email', 'profile__official_email',
        'profile__personal_email', 'profile__nid',
        'profile__gender', 'profile__date_of_birth', 'profile__procurement_roles__role',
        'profile__procurement_roles_lgis__role', '', '')

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data.update({'password': make_password('lged1234')})
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        type = self.request.GET.get('type')
        if request.user.is_superuser and type != 'data_entry':
            raise ValidationError(
                {"user": ["You are a superuser. You can not update profile here. Please go to main_url/admin."]})

        data = request.data.copy()
        if 'password' in data.keys():
            if data['password']:
                data.update({'password': make_password(data['password'])})
            else:
                data.pop('password')
        # else:
        #     data.pop('password')

        # if data.get('email') == 'null':
        #     data.update({'email': None})

        # if data.get('stage'):
        #     data.update({'stage': data.get('stage')})
        #     print('stage ========= ', data.get('stage'))
        #
        # if data.get('password_reset'):
        #     data.update({'password_reset': data.get('password_reset')})
        #     print('password_reset ========= ', data.get('password_reset'))

        # print('nid ========= ', data.get('nid'))

        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # if data.get('email') == None:
        #     print('blaaaaaaaaaa')
        #     print('email string ===== ', data.get('email'))
        #     instance.email = None
        #     instance.save()
        #     print('email none ===== ', instance.email)

        if data.get('nid') == '':
            instance.profile.nid = None
            # print('nid_value ========= ', data.get('nid_value'))

        if data.get('trainer'):
            if data['trainer'] == '1':
                instance.profile.trainer = True
                instance.profile.training_under = self.request.user.profile.office
            else:
                instance.profile.trainer = False
                instance.profile.training_under = None
            instance.profile.save()
            serializer = self.get_serializer(instance, data=data, partial=partial)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)
        if data.get('role'):
            instance.profile.role = Role.objects.get(id=data['role'])
            instance.profile.save()
            serializer = self.get_serializer(instance, data=data, partial=partial)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        user = User.objects.get(id=instance.id)
        if 'password' in data and request.user.profile.role.priority > 1:  # TODO: why it is here???
            login(request, user)
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def perform_create(self, serializer):
        with transaction.atomic():
            # print(serializer.validated_data)
            mobile_no = serializer.validated_data.pop('mobile_no')
            official_mobile_no = serializer.validated_data.pop('official_mobile_no')
            designation = serializer.validated_data.pop('designation')
            role_list = serializer.validated_data.pop('procurement_role')
            role_list_lgis = serializer.validated_data.pop('procurement_role_lgis')
            description = serializer.validated_data.pop('description')
            start_date = self.request.data.get('start_date')
            venue = self.request.data.get('venue')
            # e_gp_user_id = serializer.validated_data.pop('e_gp_user_id')
            # e_gp_user_id_lgis = serializer.validated_data.pop('e_gp_user_id_lgis')
            # bengali_name = serializer.validated_data.pop('bengali_name')

            profile_fields = serializer.validated_data.pop('profile')
            nid = profile_fields['nid']
            if nid == '':
                nid = None
            # print('nid ======== ', nid)
            personal_email = profile_fields['personal_email']
            official_email = profile_fields['official_email']
            if 'gender' in profile_fields:
                gender = profile_fields['gender']
            if 'date_of_birth' in profile_fields:
                date_of_birth = profile_fields['date_of_birth']
            if 'get_PPR_training_display' in profile_fields:
                PPR_training = profile_fields['get_PPR_training_display']
            if 'bengali_name' in profile_fields:
                bengali_name = profile_fields['bengali_name']
            else:
                bengali_name = ''
            if 'trainer' in profile_fields:
                trainer = True
            if 'e_gp_user_id_for_govt' in profile_fields:
                e_gp_user_id_for_govt = profile_fields['e_gp_user_id_for_govt']
            if 'e_gp_user_id_lgis_for_govt' in profile_fields:
                e_gp_user_id_lgis_for_govt = profile_fields['e_gp_user_id_lgis_for_govt']
            if 'e_gp_user_id_for_org_admin' in profile_fields:
                e_gp_user_id_for_org_admin = profile_fields['e_gp_user_id_for_org_admin']
            if 'e_gp_user_id_lgis_for_org_admin' in profile_fields:
                e_gp_user_id_lgis_for_org_admin = profile_fields['e_gp_user_id_lgis_for_org_admin']
            if 'e_gp_user_id_for_pe_admin' in profile_fields:
                e_gp_user_id_for_pe_admin = profile_fields['e_gp_user_id_for_pe_admin']
            if 'e_gp_user_id_lgis_for_pe_admin' in profile_fields:
                e_gp_user_id_lgis_for_pe_admin = profile_fields['e_gp_user_id_lgis_for_pe_admin']
            # # print('beng', bengali_name)

            office_id = serializer.validated_data.pop('office')
            if office_id != '':
                office_id = int(office_id)
                office = Office.objects.get(id=office_id)
            else:
                office = ''

            # raise ValidationError({"profile": ["Can not find user profile!"]})

            profile = None
            # try:
            #     profile_with_given_mobile_no = Profile.objects.get(mobile_no=mobile_no)
            # except Exception as e:
            #     profile_with_given_mobile_no = None

            # if profile_with_given_mobile_no is not None:
            #     # print("found_duplicate")
            #     raise ValidationError({"mobile": ["Personal Mobile No already exists"]})
            # else:
            try:
                try:
                    designation_object = Designation.objects.get(id=int(designation))
                except Exception as e:
                    raise ValidationError({"designation": ["Can not find designation"]})

                profile = Profile.objects.create(mobile_no=mobile_no, official_mobile_no=official_mobile_no,
                                                 nid=nid, official_email=official_email,
                                                 designation=designation_object, office=office,
                                                 personal_email=personal_email, bengali_name=bengali_name)
                # profile.e_gp_user_id = e_gp_user_id
                # profile.e_gp_user_id_lgis = e_gp_user_id_lgis
                if 'gender' in locals():
                    profile.gender = gender
                if 'date_of_birth' in locals():
                    profile.date_of_birth = date_of_birth
                if 'PPR_training' in locals() and PPR_training == 'True':
                    profile.PPR_training = True
                if 'trainer' in locals() and trainer:
                    profile.trainer = True
                    profile.training_under = self.request.user.profile.office
                if 'e_gp_user_id_for_govt' in locals():
                    profile.e_gp_user_id_for_govt = e_gp_user_id_for_govt
                if 'e_gp_user_id_lgis_for_govt' in locals():
                    profile.e_gp_user_id_lgis_for_govt = e_gp_user_id_lgis_for_govt
                if 'e_gp_user_id_for_org_admin' in locals():
                    profile.e_gp_user_id_for_org_admin = e_gp_user_id_for_org_admin
                if 'e_gp_user_id_lgis_for_org_admin' in locals():
                    profile.e_gp_user_id_lgis_for_org_admin = e_gp_user_id_lgis_for_org_admin
                if 'e_gp_user_id_for_pe_admin' in locals():
                    profile.e_gp_user_id_for_pe_admin = e_gp_user_id_for_pe_admin
                if 'e_gp_user_id_lgis_for_pe_admin' in locals():
                    profile.e_gp_user_id_lgis_for_pe_admin = e_gp_user_id_lgis_for_pe_admin

                # # print('ashiq', self.request.FILES)
                if 'avatar' in self.request.FILES:
                    serializer.validated_data.pop('avatar')
                # if 'certificate' in self.request.FILES:
                #     serializer.validated_data.pop('certificate')

                # print('insert')
                serializer.validated_data.update({'profile': profile})
                user = super().perform_create(serializer)
                user.is_active = True
                user.save()
                if PPR_training == 'True':
                    # if TrainingBatch.objects.filter(created_by_status=2).count() != 0:
                    #     training_object = TrainingBatch.objects.filter(created_by_status=2)[0]
                    #     training_user = TrainingUser.objects.create(training=training_object, user=user)
                    #     training_object.no_of_participants = training_object.no_of_participants + 1
                    #     training_object.save()
                    # else:
                    try:
                        training_name_object = \
                            TrainingName.objects.filter(training_name='3 weeks PPR Training')[0]
                        funded_by = FundedBy.objects.filter(funded_by='CPTU')[0]
                        venue = ResourceCenter.objects.get(id=venue)
                        try:
                            end_date = datetime.datetime.strptime(start_date, "%Y-%m-%d") + datetime.timedelta(
                                days=21)
                        except Exception:
                            end_date = None
                        training_object = TrainingBatch.objects.create(organization='CPTU',
                                                                       training_name=training_name_object,
                                                                       training_category='Procurement Training',
                                                                       project=funded_by, created_by_status=2,
                                                                       no_of_participants=1, start_date=start_date,
                                                                       venue=venue, end_date=end_date)
                    except Exception as e:
                        raise ValidationError(
                            "There is no Funding Source named CPTU or no training name called 3 weeks"
                            " PPR Training. Create them from settings and try again.")
                    training_user = TrainingUser.objects.create(training=training_object, user=user)
                    if 'certificate' in self.request.FILES:
                        certificate = self.request.FILES['certificate']
                        # fileName, fileExtension = os.path.splitext(certificate.name)
                        # certificate.name = str(user.id) + fileExtension
                        training_user.certificate = certificate
                        training_user.save()

                if 'avatar' in self.request.FILES:
                    avatar = self.request.FILES['avatar']
                    fileName, fileExtension = os.path.splitext(avatar.name)
                    avatar.name = str(user.id) + fileExtension
                    profile.avatar = avatar
                    profile.image_name = avatar.name
                    profile.save()

                if role_list != "":

                    role_list = role_list.split(',')
                    # print(role_list)
                    for role in role_list:
                        id = int(role)
                        pRole = ProcurementRole.objects.get(pk=id)
                        user.profile.procurement_roles.add(pRole)
                        user.profile.save()
                        # print(user)

                if role_list_lgis != "":

                    role_list_lgis = role_list_lgis.split(',')
                    # print(role_list_lgis)
                    for role_lgis in role_list_lgis:
                        id = int(role_lgis)
                        pRole = ProcurementRole.objects.get(pk=id)
                        user.profile.procurement_roles_lgis.add(pRole)
                        user.profile.save()
                        # print(user)

                if designation != "":
                    designationObject = Designation.objects.get(pk=int(designation))
                    user.profile.designation = designationObject
                    user.profile.save()

                views.audit_trail_record(self.request, user, {}, "USER PROFILE", 'CREATE')
            except Exception as e:
                # print(e)
                raise ValidationError({"profile": [e, profile]})

    def perform_update(self, serializer):

        # print(serializer.validated_data)

        # audit trail data here ---------------------------------------------
        prev_data = {}
        Module_prev_object = User.objects.get(pk=serializer.instance.id)
        prev_data = views.get_user_profile_data(serializer.instance.id)
        # audit trail data here ---------------------------------------------

        mobile_no = serializer.validated_data.pop('mobile_no')
        official_mobile_no = serializer.validated_data.pop('official_mobile_no')
        # stage = serializer.validated_data.get('stage')
        # password_reset = serializer.validated_data.get('password_reset')
        # e_gp_user_id = serializer.validated_data.pop('e_gp_user_id')
        # e_gp_user_id_lgis = serializer.validated_data.pop('e_gp_user_id_lgis')
        # bengali_name = serializer.validated_data.pop('bengali_name')
        profile_data = serializer.validated_data.pop('profile')
        personal_email = profile_data['personal_email']
        official_email = profile_data['official_email']
        if serializer.validated_data.get('nid'):
            nid = serializer.validated_data.get('nid')
            temp = Profile.objects.filter(nid=nid)
            if len(temp) > 1:
                raise ValidationError({"message": ["NID can't be duplicate"]})
            if len(temp) == 1 and serializer.instance.profile.id != temp[0].id:
                raise ValidationError({"message": ["NID can't be duplicate"]})
        if 'gender' in profile_data:
            gender = profile_data['gender']
        if 'date_of_birth' in profile_data:
            date_of_birth = profile_data['date_of_birth']
        if 'get_PPR_training_display' in profile_data:
            PPR_training = profile_data['get_PPR_training_display']
        else:
            PPR_training = 'False'
        if 'bengali_name' in profile_data:
            bengali_name = profile_data['bengali_name']
        else:
            bengali_name = ''
        if 'e_gp_user_id_for_govt' in profile_data:
            e_gp_user_id_for_govt = profile_data['e_gp_user_id_for_govt']
        if 'e_gp_user_id_lgis_for_govt' in profile_data:
            e_gp_user_id_lgis_for_govt = profile_data['e_gp_user_id_lgis_for_govt']
        if 'e_gp_user_id_for_org_admin' in profile_data:
            e_gp_user_id_for_org_admin = profile_data['e_gp_user_id_for_org_admin']
        if 'e_gp_user_id_lgis_for_org_admin' in profile_data:
            e_gp_user_id_lgis_for_org_admin = profile_data['e_gp_user_id_lgis_for_org_admin']
        if 'e_gp_user_id_for_pe_admin' in profile_data:
            e_gp_user_id_for_pe_admin = profile_data['e_gp_user_id_for_pe_admin']
        if 'e_gp_user_id_lgis_for_pe_admin' in profile_data:
            e_gp_user_id_lgis_for_pe_admin = profile_data['e_gp_user_id_lgis_for_pe_admin']

        if 'designation' in serializer.validated_data:
            designation = serializer.validated_data.pop('designation')
        if 'procurement_role' in serializer.validated_data:
            role_list = serializer.validated_data.pop('procurement_role')
        if 'description' in serializer.validated_data:
            description = serializer.validated_data.pop('description')
        if 'procurement_role' in serializer.validated_data:
            role_list = serializer.validated_data.pop('procurement_role')
            # print(role_list)
        if 'procurement_role_lgis' in serializer.validated_data:
            role_list_lgis = serializer.validated_data.pop('procurement_role_lgis')
            # print(role_list_lgis)
        if 'office' in serializer.validated_data:
            office = int(serializer.validated_data.pop('office'))
        # if 'start_date' in self.request.GET.get('start_date'):
        #     start_date = self.request.data.pop('start_date')
        # else:
        #     start_date = None
        # print('ashiq', self.request.data)
        start_date = self.request.data.get('start_date')
        venue = self.request.data.get('venue')
        # if 'venue' in self.request.GET.get('venue'):
        #     venue = self.request.data.pop('venue')
        # else:
        #     venue = None

        user = super().perform_update(serializer)
        print('user ====== ', user)
        profile = user.profile
        print('profile ====== ', profile)

        if 'avatar' in self.request.FILES:
            avatar = self.request.FILES['avatar']
            fileName, fileExtension = os.path.splitext(avatar.name)
            if profile.avatar:
                profile.avatar.delete(save=True)

            avatar.name = str(user.id) + fileExtension

        if profile.mobile_no != mobile_no:
            profile_with_provided_mobile_no = None
            try:
                profile_with_given_mobile_no = Profile.objects.get(mobile_no=mobile_no)
            except Exception as e:
                profile_with_given_mobile_no = None

            if profile_with_given_mobile_no is not None:
                print('found duplicate')
                # raise ValidationError({"mobile": ["Personal Mobile No already exists"]})

        if profile:
            if 'designation' in locals():
                if designation != "":
                    designation_object = Designation.objects.get(id=int(designation))
                    profile.designation = designation_object

            profile.mobile_no = mobile_no
            profile.personal_email = personal_email
            profile.official_email = official_email
            profile.official_mobile_no = official_mobile_no
            # profile.e_gp_user_id = e_gp_user_id
            # profile.e_gp_user_id_lgis = e_gp_user_id_lgis
            if serializer.validated_data.get('nid'):
                profile.nid = nid
            profile.bengali_name = bengali_name
            if 'gender' in locals():
                profile.gender = gender
            if 'date_of_birth' in locals():
                profile.date_of_birth = date_of_birth
            else:
                profile.date_of_birth = None
            if PPR_training == 'True':
                profile.PPR_training = True
            else:
                profile.PPR_training = False
            if 'office' in locals():
                profile.office = Office.objects.get(id=office)
            if 'e_gp_user_id_for_govt' in locals():
                profile.e_gp_user_id_for_govt = e_gp_user_id_for_govt
            if 'e_gp_user_id_lgis_for_govt' in locals():
                profile.e_gp_user_id_lgis_for_govt = e_gp_user_id_lgis_for_govt
            if 'e_gp_user_id_for_org_admin' in locals():
                profile.e_gp_user_id_for_org_admin = e_gp_user_id_for_org_admin
            if 'e_gp_user_id_lgis_for_org_admin' in locals():
                profile.e_gp_user_id_lgis_for_org_admin = e_gp_user_id_lgis_for_org_admin
            if 'e_gp_user_id_for_pe_admin' in locals():
                profile.e_gp_user_id_for_pe_admin = e_gp_user_id_for_pe_admin
            if 'e_gp_user_id_lgis_for_pe_admin' in locals():
                profile.e_gp_user_id_lgis_for_pe_admin = e_gp_user_id_lgis_for_pe_admin

            if 'avatar' in locals():
                profile.avatar = avatar
                profile.image_name = avatar.name

            profile.save()
        if 'role_list' in locals():
            user.profile.procurement_roles.clear()
            if 'role_list' in locals():
                if role_list != "":
                    role_list = role_list.split(',')
                    # print(role_list)
                    for role in role_list:
                        id = int(role)
                        pRole = ProcurementRole.objects.get(pk=id)
                        user.profile.procurement_roles.add(pRole)
                        user.profile.save()

        if 'role_list_lgis' in locals():
            user.profile.procurement_roles_lgis.clear()
            if 'role_list_lgis' in locals():
                if role_list_lgis != "":
                    role_list_lgis = role_list_lgis.split(',')
                    # print(role_list_lgis)
                    for role in role_list_lgis:
                        id = int(role)
                        pRole = ProcurementRole.objects.get(pk=id)
                        user.profile.procurement_roles_lgis.add(pRole)
                        user.profile.save()

        if PPR_training == 'True':
            # if TrainingBatch.objects.filter(created_by_status=2).count() != 0:
            #     training_object = TrainingBatch.objects.filter(created_by_status=2)[0]
            #     if TrainingUser.objects.filter(training=training_object, user=user).count() == 0:
            #         training_user = TrainingUser.objects.create(training=training_object, user=user)
            #         training_object.no_of_participants = training_object.no_of_participants + 1
            #         training_object.save()
            #     else:
            #         training_user = TrainingUser.objects.filter(training=training_object, user=user)[0]
            # else:
            try:
                training_name_object = TrainingName.objects.filter(training_name='3 weeks PPR Training')[0]
                funded_by = FundedBy.objects.filter(funded_by='CPTU')[0]
                venue = ResourceCenter.objects.get(id=venue)
                try:
                    end_date = datetime.datetime.strptime(start_date, "%Y-%m-%d") + datetime.timedelta(days=21)
                except Exception:
                    end_date = None
                # print(training_name_object, funded_by, start_date, venue)
                if TrainingUser.objects.filter(training__created_by_status=2, user=user).count() == 0:
                    training_object = TrainingBatch.objects.create(organization='CPTU',
                                                                   training_name=training_name_object,
                                                                   training_category='Procurement Training',
                                                                   project=funded_by, created_by_status=2,
                                                                   no_of_participants=1, start_date=start_date,
                                                                   venue=venue, end_date=end_date)
                else:
                    training_object = TrainingBatch.objects.filter(created_by_status=2, traininguser__user=user)[0]
                    training_object.venue = venue
                    training_object.start_date = start_date
                    training_object.end_date = end_date
                    training_object.save()
                    # training_batch.objects.update(organization='CPTU',
                    #                               training_name=training_name_object,
                    #                               training_category='Procurement Training',
                    #                               project=funded_by, created_by_status=2,
                    #                               no_of_participants=1, start_date=start_date,
                    #                               venue=venue, end_date=end_date)
                    # training_object = TrainingBatch.objects.filter(created_by_status=2, traininguser__user=user)[0]

            except Exception as e:
                raise ValidationError(
                    "There is no Funding Source named CPTU or no training name called 3 weeks"
                    " PPR Training. Create them from settings and try again.")
            if TrainingUser.objects.filter(training=training_object, user=user).count() == 0:
                training_user = TrainingUser.objects.create(training=training_object, user=user)
            else:
                training_user = TrainingUser.objects.filter(training=training_object, user=user)[0]
            if 'certificate' in self.request.FILES:
                certificate = self.request.FILES['certificate']
                # fileName, fileExtension = os.path.splitext(certificate.name)
                # certificate.name = str(user.id) + fileExtension
                training_user.certificate = certificate
                training_user.save()
            # else:
            #     training_user.certificate = None
            #     training_user.save()
        else:
            if TrainingBatch.objects.filter(created_by_status=2, traininguser__user=user).count() != 0:
                training_object = TrainingBatch.objects.filter(created_by_status=2, traininguser__user=user)[0]
                training_object.delete()
        # audit trail action here-----------------------
        views.audit_trail_record(self.request, user, prev_data, "USER PROFILE", 'UPDATE')
        # audit trail action here-----------------------

        return Response({"status": "200", "error_message": ""})

    def perform_destroy(self, instance):
        views.audit_trail_record(self.request, instance, {}, "USER PROFILE", 'DELETE')
        # proc_role = list(Profile.objects.get(user=instance).procurement_roles.all().values_list('id', flat=True))
        # proc_role_lgis = list(Profile.objects.get(user=instance).procurement_roles_lgis.all().values_list('id', flat=True))
        # for role_lged in proc_role:
        #     instance.profile.procurement_roles.remove(role_lged)
        # for role_lgis in proc_role_lgis:
        #     instance.profile.procurement_roles_lgis.remove(role_lgis)
        try:
            profile = Profile.objects.get(user=instance)
            profile.nid = None
            profile.official_email = None
            profile.official_mobile_no = None
            profile.personal_email = None
            profile.mobile_no = None
            profile.date_of_birth = None
            profile.avatar = None
            profile.save()
        except Profile.DoesNotExist or Profile.MultipleObjectsReturned:
            print('')


        instance.delete()

    def get_queryset(self):
        type = self.request.GET.get('type')
        office = self.request.GET.get('office')
        batch_id = self.request.GET.get('batch_id')
        organization = self.request.GET.get('organization')
        office_category = self.request.GET.get('office_category')
        region = self.request.GET.get('region')
        district = self.request.GET.get('district')
        designation = self.request.GET.get('designation')
        proc_role = self.request.GET.get('proc_role')
        proc_role_lgi = self.request.GET.get('proc_role_lgi')
        proc_role_lged = self.request.GET.get('proc_role_lged')
        designation_value = self.request.GET.get('designation_value')
        updated_at_from = self.request.GET.get('updated_at_from')
        updated_at_to = self.request.GET.get('updated_at_to')
        imp_user = self.request.GET.get('imp_user')
        email = self.request.GET.get('email')
        designation_list = self.request.GET.get('designation_list')
        region_list = self.request.GET.get('region_list')
        training_name = self.request.GET.get('training_name')
        floating = self.request.GET.get('floating')
        focal_point = self.request.GET.get('focal_point')
        id_list = self.request.GET.get('id_list')

        name_adv = self.request.GET.get('name_adv')
        bang_name_adv = self.request.GET.get('bang_name_adv')
        designation_adv = self.request.GET.get('designation_adv')
        mobile_no_adv = self.request.GET.get('mobile_no_adv')
        off_mobile_no_adv = self.request.GET.get('off_mobile_no_adv')
        off_email_adv = self.request.GET.get('off_email_adv')
        email_adv = self.request.GET.get('email_adv')
        nid_adv = self.request.GET.get('nid_adv')
        gender_adv = self.request.GET.get('gender_adv')
        ppr_training_adv = self.request.GET.get('ppr_training_adv')
        e_gp_id_lged_adv = self.request.GET.get('e_gp_id_lged_adv')
        e_gp_id_lgi_adv = self.request.GET.get('e_gp_id_lgi_adv')
        transfer = self.request.GET.get('transfer')
        date_of_birth = self.request.GET.get('date_of_birth')
        mobile_no = self.request.GET.get('mobile_no')
        nid = self.request.GET.get('nid')
        name = self.request.GET.get('name')
        trainer = self.request.GET.get('trainer')
        training_under = self.request.GET.get('training_under')
        official_email_adv = self.request.GET.get('official_email')

        qs = super().get_queryset()
        # qs2 = super().get_queryset()

        user_permissions = list(self.request.user.profile.role.permission.values_list('code',
                                                                                      flat=True)) if self.request.user.is_authenticated else [
            'user_admin']

        if self.request.GET.get('fields'):
            return qs

        if 'user_admin' not in user_permissions and type != 'e-GP LAB' and transfer != '1':
            qs = qs.filter(profile__office_id=self.request.user.profile.office.id)

            # temp_offices_users = TemporaryOffice.objects.filter(
            #     office_id=self.request.user.profile.office.id).values_list('user_id', flat=True)
            # temp_offices_users = tuple(temp_offices_users)

            temp_offices_users = TemporaryOffice.objects.filter(
                office_id=self.request.user.profile.office.id)
            temp_offices_users = list(temp_offices_users)

            remove_users = []
            for user in qs:
                if user.profile.nid is None or user.first_name is None:
                    if user.profile.is_temp_office_assign == True:
                        user_property = User.objects.get(id=user.id)
                        permanent_designation = user_property.profile.designation.designation
                        for temp_user in temp_offices_users:
                            if permanent_designation == temp_user.designation.designation:
                                remove_users.append(user.id)
                                temp_offices_users.remove(temp_user)
                                break

            qs = qs.exclude(id__in=remove_users)

        if focal_point:
            proc_role_ob = ProcurementRole.objects.filter(role='Focal Point')[0]
            qs = qs.exclude(profile__procurement_roles_lgis__in=[proc_role_ob]).exclude(profile__procurement_roles__in=
                                                                                        [proc_role_ob])
        if id_list:
            filters = {'id__in': id_list.split(",")}
            qs = qs.filter(**filters)

        if date_of_birth:
            qs = qs.filter(profile__date_of_birth=datetime.datetime.strptime(date_of_birth, "%Y-%m-%d").date())
        if trainer:
            qs = qs.filter(profile__trainer=True)
        if training_under:
            qs = qs.filter(profile__training_under__id=training_under)
        if floating:
            qs = qs.filter(profile__floating=True)
        if name:
            qs = qs.filter(first_name=name)

        if office:
            qs = qs.filter(profile__office_id=office)

        if batch_id:
            qs = qs.filter(trainingbatch=batch_id)
        if organization:
            qs = qs.filter(profile__office__organization__icontains=organization)
        if office_category:
            qs = qs.filter(profile__office__office_category__icontains=office_category)
        if region:
            qs = qs.filter(profile__office__region=region)
        if district:
            qs = qs.filter(profile__office__district=district)
        if designation:
            qs = qs.filter(profile__designation=designation)

        if designation_value:
            qs = qs.filter(profile__designation__designation=designation_value)

        if proc_role:
            proc_role_ob = ProcurementRole.objects.filter(role=proc_role)[0]
            qs_copy = qs
            qs = qs.filter(profile__procurement_roles_lgis__in=[proc_role_ob])
            qs_copy = qs_copy.filter(profile__procurement_roles__in=[proc_role_ob])
            qs = qs | qs_copy
        if proc_role_lgi:
            proc_role_ob = ProcurementRole.objects.filter(role=proc_role_lgi)[0]
            qs = qs.filter(profile__procurement_roles_lgis__in=[proc_role_ob])
        if proc_role_lged:
            proc_role_ob = ProcurementRole.objects.filter(role=proc_role_lged)[0]
            qs = qs.filter(profile__procurement_roles__in=[proc_role_ob])
        if email:
            qs = qs.filter(email=email)
        if region_list:
            qs = qs.filter(profile__office__region__in=region_list.split(',')).order_by('id').distinct()
        if designation_list:
            qs = qs.filter(profile__designation__in=designation_list.split(',')).order_by('id').distinct()

        if training_name:
            # print('training', training_name, training_name[1:])
            if training_name[0] != '!':
                training_users = TrainingBatch.objects.filter(training_name=training_name,
                                                              traininguser__user__isnull=False).values_list(
                    'traininguser__user', flat=True)
                qs = qs.filter(id__in=training_users)

            else:
                training_name = training_name[1:]
                if training_name:
                    training_users = TrainingBatch.objects.filter(training_name=training_name,
                                                                  traininguser__user__isnull=False).values_list(
                        'traininguser__user', flat=True)
                    qs = qs.exclude(id__in=training_users)
                else:
                    # training_users = TrainingBatch.objects.filter().values_list(
                    #     'traininguser__user', flat=True)
                    # qs = qs.filter(~Q(id__in=training_users))
                    qs = User.objects.none()
                    # # print(qs)

        if imp_user == 'admin':
            qs_copy = qs
            qs = qs.filter(profile__procurement_roles_lgis__role__in=['Organization Admin', 'PE Admin'])
            qs_copy = qs_copy.filter(profile__procurement_roles__role__in=['Organization Admin', 'PE Admin'])
            qs = qs | qs_copy
            qs = qs.distinct()
        if imp_user == 'focal_point':
            qs_copy = qs
            qs = qs.filter(profile__procurement_roles_lgis__role__in=['Focal Point'])
            qs_copy = qs_copy.filter(profile__procurement_roles__role__in=['Focal Point'])
            qs = qs | qs_copy
            qs = qs.distinct()
        if imp_user == 'other':
            # and user_office_category != "LGED HQ":
            qs_copy2 = qs
            qs_copy2 = qs_copy2.filter(profile__procurement_roles_lgis__role=None) \
                .filter(profile__procurement_roles__role=None)
            qs_copy = qs
            other_roles = ProcurementRole.objects.filter(
                ~Q(role__in=['Focal Point', 'Organization Admin', 'PE Admin'])).values_list('role', flat=True)
            qs = qs.filter(profile__procurement_roles_lgis__role__in=other_roles)
            qs_copy = qs_copy.filter(profile__procurement_roles__role__in=other_roles)
            qs = qs | qs_copy | qs_copy2
            qs = qs.distinct()
        if imp_user == 'all':
            qs = qs.distinct()
        if imp_user == 'floating':
            qs = qs.filter(profile__floating=True)
        if name_adv:
            qs = qs.filter(first_name__icontains=name_adv)
        if bang_name_adv:
            qs = qs.filter(profile__bengali_name__icontains=bang_name_adv)
        if designation_adv:
            qs = qs.filter(profile__designation__id=designation_adv)

        if mobile_no_adv:
            qs = qs.filter(profile__mobile_no__icontains=mobile_no_adv)
        if mobile_no:
            qs = qs.filter(profile__mobile_no=mobile_no)
        if nid:
            qs = qs.filter(profile__nid=nid)
            print('kkkkkkkkkkkk')
        if off_mobile_no_adv:
            qs = qs.filter(profile__official_mobile_no__icontains=off_mobile_no_adv)
        if off_email_adv:
            qs = qs.filter(profile__official_email__icontains=off_email_adv)
        if email_adv:
            qs = qs.filter(profile__personal_email__icontains=email_adv)
        if official_email_adv:
            qs = qs.filter(profile__official_email__icontains=official_email_adv)
        if nid_adv:
            qs = qs.filter(profile__nid__icontains=nid_adv)
        if gender_adv:
            qs = qs.filter(profile__gender__icontains=gender_adv)
        if ppr_training_adv:
            qs = qs.filter(profile__PPR_training=ppr_training_adv)
        if e_gp_id_lged_adv:
            qs = qs.filter(profile__e_gp_user_id__icontains=e_gp_id_lged_adv)
        if e_gp_id_lgi_adv:
            qs = qs.filter(profile__e_gp_user_id_lgis__icontains=e_gp_id_lgi_adv)

        if updated_at_from:
            updated_from = datetime.datetime.strptime(updated_at_from, "%Y-%m-%d").date()
            qs = qs.filter(profile__updated_at__gte=updated_from)
        if updated_at_to:
            updated_to = datetime.datetime.strptime(updated_at_to, "%Y-%m-%d").date()
            updated_to += datetime.timedelta(days=1)
            qs = qs.filter(profile__updated_at__lte=updated_to)

        if 'user_admin' not in user_permissions:
            # return result_list
            return qs.filter(is_superuser=False).order_by('-profile__designation__weight')
            # return qs.filter(is_superuser=False).order_by('-profile__updated_at')
        else:
            return qs.filter(is_superuser=False).order_by('-profile__updated_at')


class ProcurementRoleViewSet(BaseViewSet):
    queryset = ProcurementRole.objects.all()
    serializer_class = ProcurementRoleSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_fields = ('role',)

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter().order_by('-weight')


class HomePageWritingViewSet(BaseViewSet):
    queryset = HomepageWriting.objects.all()
    serializer_class = HomePageWritingSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter().order_by('id')


class ImportantLinkViewSet(BaseViewSet):
    queryset = ImportantLinks.objects.all()
    serializer_class = ImportantLinkSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter().order_by('id')


class DesignationViewSet(BaseViewSet):
    queryset = Designation.objects.all()
    serializer_class = DesignationSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    # filter_fields = ('designation',)

    def get_queryset(self):
        qs = super().get_queryset()
        id_list = self.request.GET.get('id_list')
        office_id = self.request.GET.get('office_id')
        office_category = self.request.GET.get('office_category')
        not_office_id = self.request.GET.get('not_office_id')
        # temp = ["CE Office (HQ)", "Additional Chief Engineer Office (HQ)", "SE Office (HQ)", "Project Office (HQ)",
        #         "Unit (HQ)", "Division Office (Field)", "Regional Office (Field)", "District Office (Field)",
        #         "Upazila Engineer Office(Field)", "e-GP LAB OFFICES"]
        temp = ["e-GP LAB OFFICES"]
        # print('all_des', qs)
        if id_list:
            filters = {'id__in': id_list.split(",")}
            qs = qs.filter(**filters)
        if office_id:
            users_designation = User.objects.filter(profile__office_id=office_id).values_list('profile__designation',
                                                                                              flat=True)
            qs = qs.filter(id__in=users_designation)

            # Unused but may be needed later ### {{{

            # all_designation = Profile.objects.filter(office_id=office_id).values_list(
            #     'designation__designation', flat=True)
            # all_designation = list(all_designation)
            #
            # unused_designation = Profile.objects.filter(office_id=office_id, nid=None).values(
            #     'designation__designation').annotate(unused=Count('designation'))
            #
            # remove_des1 = []
            # remove_des2 = []
            # flag = 0
            #
            # for x in all_designation:
            #     for y in unused_designation:
            #         # print('yyyyyy ====== ', y['designation__designation'])
            #         if x == y['designation__designation']:
            #             flag = 1
            #             # print('nnnnnnnnnnnnnnnnnnnnnnnnnn', x)
            #             # print('x ======= ', x)
            #     if flag == 0:
            #         remove_des1.append(x)
            #
            #     flag = 0
            #
            #     # flag = 0
            #
            # used_temp_designation = TemporaryOffice.objects.filter(office_id=office_id).values(
            #     'designation__designation').annotate(temp_used=Count('designation'))
            #
            # for curr in unused_designation:
            #     for temp in used_temp_designation:
            #         if curr['designation__designation'] == temp['designation__designation'] and curr['unused'] == temp[
            #             'temp_used']:
            #             remove_des2.append(curr['designation__designation'])
            #             # print(curr['designation__designation'])
            #
            # focal_designation = Profile.objects.filter(office_id=office_id,
            #                                            procurement_roles_lgis__role='Focal Point').values_list(
            #     'designation__designation', flat=True)
            # focal_designation = tuple(focal_designation)
            #
            # for p in focal_designation:
            #     remove_des1.append(p)
            #
            # qs = qs.exclude(designation__in=remove_des1)
            # qs = qs.exclude(designation__in=remove_des2)

            #   }}}

        if not_office_id:
            users_designation = User.objects.filter(profile__office_id=not_office_id).values_list(
                'profile__designation',
                flat=True)
            qs = qs.exclude(id__in=users_designation)
        if office_category:
            if office_category not in temp:
                qs = qs.filter(office_categories__contains=[office_category])
                print('office_categories__contains === ', qs)

        return qs.filter().order_by('id')


class DivisionViewSet(BaseViewSet):
    queryset = Division.objects.all()
    serializer_class = DivisionSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_fields = ('name',)

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.order_by('name')


class CityCorporationViewSet(BaseViewSet):
    queryset = CityCorporation.objects.all()
    serializer_class = CityCorporationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter().order_by('name')


class RegionViewSet(BaseViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_fields = ('name',)

    def get_queryset(self):
        qs = super().get_queryset()
        id = self.request.query_params.get('id')
        division = self.request.query_params.get('division')

        if id:
            qs = qs.filter(division=id)
        if division:
            qs = qs.filter(division=division)
        return qs.order_by('name')


class DistrictViewSet(BaseViewSet):
    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_fields = ('name', 'region')

    def get_queryset(self):
        qs = super().get_queryset()
        id = self.request.query_params.get('id')
        region_list = self.request.GET.get('region_list')
        if id:
            qs = qs.filter(region=id)
        if region_list:
            filters = {'region__in': region_list.split(",")}
            queryset = District.objects.filter(**filters).order_by('name')
            return queryset
        return qs.order_by('name')


class UpazilaViewSet(BaseViewSet):
    queryset = Upazila.objects.all()
    serializer_class = UpazilaSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        id = self.request.query_params.get('id')

        if id:
            qs = qs.filter(district=id)
        return qs.order_by('name')


class OfficeViewSet(BaseViewSet):
    queryset = Office.objects.all()
    serializer_class = OfficeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = LargeResultsSetPagination
    search_fields = (
        'name', 'organization', 'office_category', 'pourashava_class', 'division__name', 'city_corporation__name',
        'region__name', 'district__name', 'upazila__name', 'post_code', 'address', 'email', 'phone_no', 'fax_no',
        'website_link', 'id')
    ordering_fields = (
        '', 'name', 'division__name', 'region__name', 'district__name', 'upazila__name', 'pourashava_class',
        'post_code', 'phone_no', 'fax_no', '', '')

    # 'pourashava_class', 'division', 'city_corporation', 'region', 'district',
    # 'upazila', 'post_code', 'address', 'email', 'phone_no', 'fax_no', 'website_link',)

    # search_fields = ('name', 'organization', )

    def perform_create(self, serializer):

        users = serializer.validated_data.pop('users')
        office_name_dd = serializer.validated_data.get('name')
        organization_dd = serializer.validated_data.get('organization')
        office_category_dd = serializer.validated_data.get('office_category')
        # division_name_dd = serializer.validated_data.get('division')
        # print('serializer validation === ',serializer.validated_data)
        # print('office name === ', office_name_dd)
        # print('organization name === ', organization_dd)
        # print('office_category === ', office_category_dd)
        # print('division name === ', division_name_dd)
        office_data = Office.objects.filter(name=office_name_dd, organization=organization_dd,
                                            office_category=office_category_dd).values_list('id', flat=True)
        # office_data = tuple(office_data)
        # print('office data === ', office_data[0])
        if office_data:
            raise ValidationError(
                {"user": ["This office is exists. So, it can't be created again. But the users are being added."],
                 "office": office_data[0]})

        office = super().perform_create(serializer)

        # audit trail action here-----------------------

        views.audit_trail_record(self.request, office, {}, "OFFICE PROFILE", 'CREATE')

        # audit trail action here-----------------------

        if users != "":
            user_list = users.split(',')
            # # print(user_list)
            for user in user_list:
                email = user
                user_object = User.objects.get(email=email)

                # print(user_object.email)

                profile = user_object.profile
                profile.office = office
                profile.save()

                # print(profile.office.name)

    def get_queryset(self):
        qs = Office.objects.all()
        qs = get_office_filter(self.request, qs)
        # print('qs ===== ', qs)
        user_permissions = list(self.request.user.profile.role.permission.values_list('code', flat=True))
        user_office = self.request.user.profile.office.name

        if 'user_admin' not in user_permissions:
            print('user_office1 ============ ', user_office)
            if (user_office not in ['Dummy Office 1', 'Dummy Office 2']):
                print('user_office2 ============ ', user_office)
                remove_office = []
                testOff1 = Office.objects.filter(name='Dummy Office 1').values_list('name', flat=True)
                for x in testOff1:
                    # print('x off ===== ', x)
                    remove_office.append(x)

                testOff2 = Office.objects.filter(name='Dummy Office 2').values_list('name', flat=True)
                for y in testOff2:
                    # print('y off ===== ', y)
                    remove_office.append(y)
                qs = qs.exclude(name__in=remove_office)
        return qs.order_by('name')

        # page = self.paginate_queryset(queryset)
        # if page is not None:
        #     serializer = self.get_serializer(page, many=True)
        #     data = self.get_paginated_response(serializer.data)
        #     return data
        # serializer = self.get_serializer(queryset, many=True)
        # return Response(serializer.data)

    def perform_update(self, serializer):

        # print(serializer.validated_data)
        if 'users' in serializer.validated_data:
            users = serializer.validated_data.pop('users')
        else:
            users = None

        # audit trail action here-----------------------
        data = {}
        module_object = Office.objects.get(pk=serializer.instance.id)
        data = views.get_office_profile_data(module_object.id)
        # audit trail action here-----------------------

        office = super().perform_update(serializer)
        # print('office ====== ', office)
        if 'profile_pic' in self.request.FILES:
            profile_pic = self.request.FILES['profile_pic']
            office.profile_pic = profile_pic
            office.save()

        # audit trail action here-----------------------
        views.audit_trail_record(self.request, office, data, "OFFICE PROFILE", 'UPDATE')
        # audit trail action here-----------------------

        if users is not None:
            Profile.objects.filter(office=office).update(office="")
            if users != "":
                user_list = users.split(',')
                for user in user_list:
                    email = user
                    user_object = User.objects.get(email=email)
                    profile = user_object.profile
                    profile.office = office
                    profile.save()

        return Response({"status": "200", "error_message": ""})

    def perform_destroy(self, instance):
        id = instance.id
        office = Office.objects.get(pk=id)

        if instance.delete():
            # audit trail action here-----------------------

            views.audit_trail_record(self.request, office, {}, "OFFICE PROFILE", 'DELETE')

            # audit trail action here-----------------------
            profile = Profile.objects.filter(office__id=id).update(office="")

        return Response({"status": "200", "error_message": ""})


# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------- Project ------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class ProjectViewSet(BaseViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ('name', 'full_name', 'code', 'cost', 'start_date', 'end_date',
                     'source_of_fund__source', 'development_partner__funded_by',
                     'director_name', 'floor_no', 'location', 'phone_no',
                     'mobile_no', 'fax_no', 'intercom', 'official_email',
                     )
    ordering_fields = ('', 'name', 'full_name', 'cost', 'code', 'start_date', 'end_date',
                       'development_partner__funded_by',
                       'director_name', 'floor_no', 'location', 'phone_no',
                       'mobile_no', 'fax_no', 'intercom', 'official_email',)

    # def perform_create(self, serializer):
    #     parent = serializer.validated_data['parent_project']
    #
    #     if parent is not None:
    #         sub_projects = Project.objects.filter(parent_project=parent)
    #         total_sub_proj_cost = serializer.validated_data['cost']
    #
    #         for project in sub_projects:
    #             total_sub_proj_cost += project.cost
    #
    #         if total_sub_proj_cost > parent.cost:
    #             raise ValidationError({"cost": ["Total sub project cost must be less than parent project"]})
    #
    #     super().perform_create(serializer)
    #
    # def perform_update(self, serializer):
    #     parent = serializer.validated_data['parent_project']
    #     # print(serializer.validated_data)
    #
    #     if parent is not None:
    #         sub_projects = Project.objects.filter(parent_project=parent)
    #         total_sub_proj_cost = -float(serializer.validated_data['prev_cost']) + serializer.validated_data['cost']
    #
    #         for project in sub_projects:
    #             total_sub_proj_cost += project.cost
    #
    #         # print(parent.cost, " ", total_sub_proj_cost)
    #
    #         if total_sub_proj_cost > parent.cost:
    #             raise ValidationError({"cost": ["Total sub project cost must be less than parent project"]})
    #
    #     super().perform_update(serializer)

    def get_queryset(self):
        # parent_project = self.request.GET.get('parent_project')
        id = self.request.GET.get('id')
        type = self.request.GET.get('type')
        organization = self.request.GET.get('organization')
        office_category = self.request.GET.get('office_category')

        qs = super().get_queryset()
        if id:
            qs = qs.filter(id=int(id))
        if organization:
            qs = qs.filter(office__organization=organization)
        if office_category:
            qs = qs.filter(office__office_category=office_category)

        # if parent_project:
        #     qs = qs.filter(parent_project__id=parent_project)
        # elif type == 'main':
        #     qs = qs.filter(parent_project__isnull=True)

        # if self.request.user.profile.office.office_category != "LGED HQ" and type != 'e-GP LAB':
        #     qs = qs.filter(Q(status='Approved') | Q(status='Pending', office=self.request.user.profile.office))
        return qs.filter().order_by('-updated_at')


# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------- Tender ------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# class TenderViewSet(BaseViewSet):
#     queryset = Tender.objects.all()
#     serializer_class = TenderSerializer
#     pagination_class = LargeResultsSetPagination
#     permission_classes = [permissions.IsAuthenticated]
#     search_fields = ('tender_id',)
#
#     def get_queryset(self):
#         console_logger.info("This is test for debug")
#         qs = super().get_queryset()
#         financial_year = self.request.GET.get('financial_year')
#         status = self.request.GET.get('status')
#         online_offline = self.request.GET.get('online_offline')
#         office = self.request.GET.get('office')
#         organization = self.request.GET.get('organization')
#         office_category = self.request.GET.get('office_category')
#         id = self.request.GET.get('id')
#         development_revenue = self.request.GET.get('development_revenue')
#         city_corporation = self.request.GET.get('city_corporation')
#
#         # print(financial_year, status, online_offline, office)
#
#         user_office_category = self.request.user.profile.office.office_category
#         if user_office_category != "LGED HQ":
#             qs = qs.filter(office=self.request.user.profile.office.id)
#
#         if id:
#             qs = qs.filter(id=id)
#         if financial_year:
#             qs = qs.filter(financial_year=financial_year)
#         if status:
#             qs = qs.filter(status=status)
#         if online_offline:
#             qs = qs.filter(online_offline=online_offline)
#         if organization:
#             qs = qs.filter(office__organization=organization)
#         if office_category:
#             qs = qs.filter(office__office_category=office_category)
#         if office:
#             qs = qs.filter(office=office)
#         if development_revenue:
#             qs = qs.filter(development_revenue=development_revenue)
#         if city_corporation:
#             qs = qs.filter(office__city_corporation=city_corporation)
#         return qs.filter().order_by('-updated_at')
#

# ----------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------- Devices --------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class DevicesViewSet(BaseViewSet):
    queryset = Devices.objects.all()
    serializer_class = DevicesSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_fields = ('id', 'package_no', 'type')

    def get_queryset(self):
        qs = super().get_queryset()
        package_no = self.request.GET.get('package_no')
        if package_no:
            qs = qs.filter(package_no=package_no)
        return qs


# ----------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------- Package No --------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class PackageNoViewSet(BaseViewSet):
    queryset = PackageNo.objects.all()
    serializer_class = PackageNoSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_fields = ('id', 'office', 'package_no',)

    def get_queryset(self):
        type = self.request.GET.get('type')

        qs = super().get_queryset()
        if type == 'global':
            qs = qs.filter(~Q(package_no='Local Purchase'))
        return qs


# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------- Inventory File Type ------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class InventoryFileTypeViewSet(BaseViewSet):
    queryset = InventoryFileType.objects.all()
    serializer_class = InventoryFileTypeSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_fields = ('file_type',)


# ----------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------- Inventory Type --------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class InventoryTypeViewSet(BaseViewSet):
    queryset = InventoryType.objects.all()
    serializer_class = InventoryTypeSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_fields = ('type',)

    def get_queryset(self):
        qs = super().get_queryset()
        type_category = self.request.GET.get('type_category')
        package = self.request.GET.get('package')

        if type_category:
            qs = qs.filter(type_category=type_category)
        if package:
            qs = qs.filter(id__in=PackageNo.objects.get(id=package).devices_set.values_list('type', flat=True))
        return qs.order_by('type')


# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------- Inventory Type Category -----------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class InventoryTypeCategoryViewSet(BaseViewSet):
    queryset = InventoryTypeCategory.objects.all()
    serializer_class = InventoryTypeCategorySerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_fields = ('category',)


# ----------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------- Inventory Status --------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class InventoryStatusViewSet(BaseViewSet):
    queryset = InventoryStatus.objects.all()
    serializer_class = InventoryStatusSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_fields = ('status',)

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.order_by('status')


# ----------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------- Source --------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class SourceViewSet(BaseViewSet):
    queryset = Source.objects.all()
    serializer_class = SourceSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_fields = ('source',)


# ----------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------- Supplier --------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class SupplierViewSet(BaseViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_fields = ('package_no',)

    def get_queryset(self):
        qs = super().get_queryset()
        inventory_id = self.request.GET.get('inventory_id')

        if inventory_id:
            inventory = Inventory.objects.get(id=inventory_id)
            qs = qs.filter(package_no=inventory.package_no)
        return qs.order_by('-updated_at')


# ----------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------- Supplier --------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class SupportCenterViewSet(BaseViewSet):
    queryset = SupportCenter.objects.all()
    serializer_class = SupportCenterSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_fields = ('package_no',)

    def get_queryset(self):
        qs = super().get_queryset()
        inventory_id = self.request.GET.get('inventory_id')

        if inventory_id:
            inventory = Inventory.objects.get(id=inventory_id)
            qs = qs.filter(package_no=inventory.package_no)
        return qs.order_by('updated_at')


# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------ Inventory -----------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class InventoryViewSet(BaseViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ('office__name', 'office__division__name', 'office__region__name', 'office__district__name',
                     'office__upazila__name', 'id', 'device__type__type', 'device__brand_name', 'device__model_no',
                     'package_no__inventory__serial_no', 'date_of_delivery', 'device__validity', 'status__status',
                     'package_no__package_no',
                     'package_no__source__source', 'supplied_quantity', 'package_no__inventory__asset_no')
    ordering_fields = (
        '', 'office__name', 'office__division__name', 'office__region__name', 'office__district__name',
        'office__upazila__name', 'id', 'device__type__type', 'device__brand_name', 'device__model_no', '',
        'date_of_delivery', 'device__validity', 'status__status', 'package_no__package_no',
        'package_no__source__source', 'supplied_quantity', '', '', '')

    def perform_create(self, serializer):
        # print(serializer.validated_data)
        serializer.validated_data.pop('document')
        source = serializer.validated_data.pop('source_value')
        brand_name = serializer.validated_data.pop('brand_name')
        model_no = serializer.validated_data.pop('model_no')
        validity = serializer.validated_data.pop('validity')

        file_name = serializer.validated_data.pop('file_name')
        if serializer.validated_data.get('supplied_quantity'):
            quantity = serializer.validated_data.get('supplied_quantity')
        else:
            quantity = 1

        if source == 'Local Purchase':
            src = Source.objects.filter(source='Local Purchase')
            src = src[0]
            package_object = PackageNo.objects.create(package_no='Local Purchase', source=src)
            package_object.office.add(self.request.user.profile.office)
            package_object.save()

            type = serializer.validated_data['type']
            device = Devices.objects.create(brand_name=brand_name, model_no=model_no, validity=validity, type=type,
                                            package_no=package_object)
            supplier = json.loads(self.request.data['supplier_set'])
            Supplier.objects.create(package_no=package_object,
                                    supplier_name=supplier["supplier_name"],
                                    supplier_mobile_no=supplier["supplier_mobile_no"],
                                    supplier_email_no=supplier["supplier_email_no"],
                                    supplier_address=supplier["supplier_address"],
                                    supplier_district=None if not supplier[
                                        "supplier_district"] else District.objects.get(
                                        id=supplier['supplier_district'])
                                    )
            support_centers = json.loads(self.request.data['supportcenter_set'])
            for key in support_centers.keys():
                support_center = support_centers[key]
                SupportCenter.objects.create(package_no=package_object,
                                             support_center_contact_person=support_center[
                                                 "support_center_contact_person"],
                                             support_center_name=support_center["support_center_name"],
                                             support_mobile_no=support_center["support_mobile_no"],
                                             support_email_no=support_center["support_email_no"],
                                             support_center_address=support_center["support_center_address"],
                                             support_center_district=None if not support_center[
                                                 "support_center_district"] else District.objects.get(
                                                 id=support_center['support_center_district'])
                                             )
            serializer.validated_data.update({'package_no': package_object})
            inventory = super().perform_create(serializer)
            inventory.device = device
            inventory.save()
            for q in range(0, quantity):
                InventoryProducts.objects.create(inventory=inventory)

            # audit trail action here-----------------------
            views.audit_trail_record(self.request, inventory, {}, "INVENTORY RECORDS", 'CREATE')
            # audit trail action here-----------------------

            for file in self.request.FILES.getlist('document[]'):
                InventoryFile.objects.create(inventory=inventory, document=file, file_name=file_name)
            return Response({"status": "200", "error_message": ""})
        else:
            inv_status = InventoryStatus.objects.get(id=1)
            serializer.validated_data.update({'status': inv_status})
            package_no = serializer.validated_data['package_no']
            type = serializer.validated_data['type']
            supplier = json.loads(self.request.data['supplier_set'])
            Supplier.objects.create(package_no=package_no,
                                    supplier_name=supplier["supplier_name"],
                                    supplier_mobile_no=supplier["supplier_mobile_no"],
                                    supplier_email_no=supplier["supplier_email_no"],
                                    supplier_address=supplier["supplier_address"],
                                    supplier_district=None if not supplier[
                                        "supplier_district"] else District.objects.get(
                                        id=supplier['supplier_district'])
                                    )
            support_centers = json.loads(self.request.data['supportcenter_set'])
            for key in support_centers.keys():
                support_center = support_centers[key]
                SupportCenter.objects.create(package_no=package_no,
                                             support_center_contact_person=support_center[
                                                 "support_center_contact_person"],
                                             support_center_name=support_center["support_center_name"],
                                             support_mobile_no=support_center["support_mobile_no"],
                                             support_email_no=support_center["support_email_no"],
                                             support_center_address=support_center["support_center_address"],
                                             support_center_district=None if not support_center[
                                                 "support_center_district"] else District.objects.get(
                                                 id=support_center['support_center_district'])
                                             )
            inv_item = Inventory.objects.filter(package_no=package_no, type=type,
                                                office=self.request.user.profile.office)
            if inv_item:
                # print("Already exists")
                raise ValidationError({"duplicate": ["This item already has been added!"]})

            inventory = super().perform_create(serializer)
            for q in range(0, quantity):
                InventoryProducts.objects.create(inventory=inventory)
            for file in self.request.FILES.getlist('document[]'):
                InventoryFile.objects.create(inventory=inventory, document=file, file_name=file_name)
            return Response({"status": "200", "error_message": ""})

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        inv_id = int(kwargs['pk'])
        inv_instance = Inventory.objects.get(pk=inv_id)
        # self.perform_update(serializer)

        # audit trail data ------------------------------------------
        data = {}
        Module_object = inv_instance
        data = views.get_inventory_data(Module_object.id)
        # audit trail data ------------------------------------------

        # print(serializer.validated_data)
        source = serializer.validated_data.pop('source_value')
        brand_name = serializer.validated_data.pop('brand_name')
        model_no = serializer.validated_data.pop('model_no')
        if serializer.validated_data.get('validity'):
            validity = serializer.validated_data.pop('validity')
        else:
            validity = None

        # file_name = serializer.validated_data.pop('file_name')

        if source == 'Local Purchase':
            type = serializer.validated_data['type']
            Devices.objects.filter(package_no=inv_instance.package_no, type=inv_instance.type).update(
                brand_name=brand_name, model_no=model_no,
                validity=validity, type=type, )
            devices = Devices.objects.filter(package_no=inv_instance.package_no, type=inv_instance.type)
            supplier = json.loads(request.data['supplier_set'])
            Supplier.objects.filter(package_no=inv_instance.package_no).update(
                supplier_name=supplier["supplier_name"],
                supplier_mobile_no=supplier["supplier_mobile_no"],
                supplier_email_no=supplier["supplier_email_no"],
                supplier_address=supplier["supplier_address"],
                supplier_district=None if not supplier["supplier_district"] else District.objects.get(
                    id=supplier['supplier_district'])
            )
            support_centers = json.loads(request.data['supportcenter_set'])
            support_center_ids = []
            for key in support_centers.keys():
                support_center = support_centers[key]
                if support_center['id'] == '-1':
                    support_center_instance = SupportCenter.objects.create(
                        support_center_contact_person=support_center["support_center_contact_person"],
                        support_center_name=support_center["support_center_name"],
                        support_mobile_no=support_center["support_mobile_no"],
                        support_email_no=support_center["support_email_no"],
                        support_center_address=support_center["support_center_address"],
                        package_no=inv_instance.package_no,
                        support_center_district=None if not support_center[
                            "support_center_district"] else District.objects.get(
                            id=support_center['support_center_district'])
                    )
                    support_center_ids.append(support_center_instance.id)
                else:
                    support_center_ids.append(support_center['id'])
                    SupportCenter.objects.filter(id=support_center['id']).update(
                        support_center_contact_person=support_center["support_center_contact_person"],
                        support_center_name=support_center["support_center_name"],
                        support_mobile_no=support_center["support_mobile_no"],
                        support_email_no=support_center["support_email_no"],
                        support_center_address=support_center["support_center_address"],
                        package_no=inv_instance.package_no,
                        support_center_district=None if not support_center[
                            "support_center_district"] else District.objects.get(
                            id=support_center['support_center_district'])
                    )
            # # print(SupportCenter.objects.filter(package_no=inv_instance.package_no).exclude(id__in=support_center_ids))
            SupportCenter.objects.filter(package_no=inv_instance.package_no).exclude(id__in=support_center_ids).delete()
            inventory = self.perform_update(serializer)
            inventory.device = devices[0]
            inventory.save()
            # for file in self.request.FILES.getlist('document[]'):
            #     InventoryFile.objects.create(inventory=inventory, document=file, file_name=file_name)

            # audit trail action here-----------------------
            views.audit_trail_record(self.request, inventory, data, "INVENTORY RECORDS", 'UPDATE')
            # audit trail action here-----------------------

            return Response({"status": "200", "error_message": ""})
        else:
            supplier = json.loads(request.data['supplier_set'])
            Supplier.objects.filter(package_no=inv_instance.package_no).update(
                supplier_name=supplier["supplier_name"],
                supplier_mobile_no=supplier["supplier_mobile_no"],
                supplier_email_no=supplier["supplier_email_no"],
                supplier_address=supplier["supplier_address"],
                supplier_district=None if not supplier["supplier_district"] else District.objects.get(
                    id=supplier['supplier_district'])
            )
            support_centers = json.loads(request.data['supportcenter_set'])
            support_center_ids = []
            for key in support_centers.keys():
                support_center = support_centers[key]
                if support_center['id'] == '-1':
                    support_center_instance = SupportCenter.objects.create(
                        support_center_contact_person=support_center["support_center_contact_person"],
                        support_center_name=support_center["support_center_name"],
                        support_mobile_no=support_center["support_mobile_no"],
                        support_email_no=support_center["support_email_no"],
                        support_center_address=support_center["support_center_address"],
                        package_no=inv_instance.package_no,
                        support_center_district=None if not support_center[
                            "support_center_district"] else District.objects.get(
                            id=support_center['support_center_district'])
                    )
                    support_center_ids.append(support_center_instance.id)
                else:
                    support_center_ids.append(support_center['id'])
                    SupportCenter.objects.filter(id=support_center['id']).update(
                        support_center_contact_person=support_center["support_center_contact_person"],
                        support_center_name=support_center["support_center_name"],
                        support_mobile_no=support_center["support_mobile_no"],
                        support_email_no=support_center["support_email_no"],
                        support_center_address=support_center["support_center_address"],
                        package_no=inv_instance.package_no,
                        support_center_district=None if not support_center[
                            "support_center_district"] else District.objects.get(
                            id=support_center['support_center_district'])
                    )
            # # print(SupportCenter.objects.filter(package_no=inv_instance.package_no).exclude(id__in=support_center_ids))
            SupportCenter.objects.filter(package_no=inv_instance.package_no).exclude(id__in=support_center_ids).delete()
            inventory = self.perform_update(serializer)
            # for file in self.request.FILES.getlist('document[]'):
            #     InventoryFile.objects.create(inventory=inventory, document=file, file_name=file_name)

            # audit trail action here-----------------------
            views.audit_trail_record(self.request, inventory, data, "INVENTORY RECORDS", 'UPDATE')
            # audit trail action here-----------------------

            return Response({"status": "200", "error_message": ""})

    def perform_destroy(self, instance):
        inventory = Inventory.objects.get(pk=instance.id)

        if instance.delete():
            # audit trail action here-----------------------
            views.audit_trail_record(self.request, inventory, {}, "INVENTORY RECORDS", 'DELETE')
            # audit trail action here-----------------------
        return Response({"status": "200", "error_message": ""})

    def get_queryset(self):
        qs = super().get_queryset()
        report_type = self.request.GET.get('report_type')
        if report_type:
            qs = get_inv_report_ob(self.request._request)
        else:
            qs = get_inv_filter(self.request, qs)
        return qs.order_by('-updated_at')


class InventoryProductsViewSet(BaseViewSet):
    queryset = InventoryProducts.objects.all()
    serializer_class = InventoryProductsSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    # filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    # filter_fields = ('file_type',)
    search_fields = (
        'inventory__office__name', 'inventory__office__office_category', 'inventory__office__division__name',
        'inventory__office__region__name',
        'inventory__office__district__name', 'inventory__office__upazila__name', 'inventory__id',
        'inventory__device__type__type', 'inventory__device__brand_name', 'inventory__device__model_no',
        'serial_no', 'asset_no', 'cost', 'user_designation__designation', 'inventory__date_of_delivery',
        'inventory__device__validity', 'inventory__status__status', 'inventory__package_no__package_no',
        'inventory__package_no__source__source', 'inventory__supplied_quantity',
    )
    ordering_fields = ('', 'inventory__office__name', 'inventory__office__office_category',
                       'inventory__office__division__name', 'inventory__office__region__name',
                       'inventory__office__district__name', 'inventory__office__upazila__name', 'inventory__id',
                       'inventory__device__type__type', 'inventory__device__brand_name', 'inventory__device__model_no',
                       'serial_no', 'asset_no', 'cost', 'user_designation__designation', 'inventory__date_of_delivery',
                       'inventory__device__validity', 'inventory__status__status', 'inventory__package_no__package_no',
                       'inventory__package_no__source__source', 'inventory__supplied_quantity', '', '', '',)

    def get_queryset(self):
        qs = super().get_queryset()
        inventory_id = self.request.GET.get('inventory')

        if inventory_id:
            qs = qs.filter(inventory__id=inventory_id)
        qs = get_inv_product_filter(self.request, qs)
        return qs.order_by('-inventory__updated_at', 'id')


# ------------------------------------------------------ ********* -----------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------ Inventory File ------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------


class InventoryFileViewSet(BaseViewSet):
    queryset = InventoryFile.objects.all()
    serializer_class = InventoryFileSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_fields = ('inventory',)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        inventory = self.request.data['inventory']
        Inventory.objects.filter(id=inventory).update(updated_at=datetime.datetime.now())
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        inventory = self.request.data['inventory']
        Inventory.objects.filter(id=inventory).update(updated_at=datetime.datetime.now())
        return Response(serializer.data)


# ----------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------- Resource Center --------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class ResourceCenterViewSet(BaseViewSet):
    queryset = ResourceCenter.objects.all()
    serializer_class = ResourceCenterSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.AllowAny]


# ------------------------------------------------------ ********* -----------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------- Training Batch ---------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class TrainingBatchViewSet(BaseViewSet):
    queryset = TrainingBatch.objects.all()
    serializer_class = TrainingBatchSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]

    search_fields = (
        'end_date', 'financial_year', 'id', 'start_date', 'training_category', 'organization',
        'no_of_participants', 'batch_number', 'updated_at', 'training_name__training_name',
        'venue__name', 'project__funded_by')
    ordering_fields = (
        '', 'id', 'organization', 'training_category', 'project__funded_by', 'training_name__training_name',
        'financial_year', 'batch_number', 'venue__name', 'start_date', 'end_date')

    def create(self, request, *args, **kwargs):
        users = None
        data = request.data.copy()
        if data.get('users'):
            users = data.pop('users')
            # # print(users)
        notify = None
        if data.get('notify'):
            notify = data.pop('notify')
            offices = data.pop('offices')
        serializer = self.get_serializer(data=data)
        serializer.status = 2 if notify else 0
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        training_id = serializer.instance.id

        if notify:
            serializer.instance.status = 2
            serializer.instance.save()

        if users:
            for user_id in users:
                email_to = ''
                user = User.objects.get(id=user_id)
                training = TrainingBatch.objects.get(id=training_id)

                param = {
                    'name': user.get_full_name(),
                    'organization': training.organization,
                    'training_category': training.training_category,
                    'start_date': training.start_date,
                    'end_date': training.end_date,
                    'office': training.office.name,
                    'office_category': training.office.office_category,
                    'batch_number': training.batch_number,
                    'venue': training.venue,
                    'training_name': training.training_name,
                    'header': 'Dear Sir,' if user.profile.gender == 'Male' else 'Dear Madam,'
                }
                if user.profile.personal_email:
                    email_to = user.profile.personal_email
                if not email_to and user.profile.official_email:
                    email_to = user.profile.official_email

                subject = 'You have a training from ' + user.profile.office.office_category + ' # ' + str(training.id)

                html_content = render_to_string('email/training_user_email_notification.html', param)
                html_content = html.escape(html_content)
                TrainingUser.objects.create(user=user, training=training, mail_body=html_content, to=email_to,
                                            from_e=settings.EMAIL_HOST_USER, subject=subject)
                if notify:
                    views.send_mail_to_user(user_id=user_id, training_id=training_id)

            end_date = serializer.instance.end_date
            start_date = serializer.instance.start_date
            if notify:
                announcement = Announcement.objects.create(expired_date=end_date, created_by=self.request.user,
                                                           title='You have a training in ' + start_date.strftime(
                                                               '%d/%m/%y'), training_status=training_id)
                announcement.office = list(map(int, offices))
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        users = None
        data = request.data.copy()
        if request.data.get('users'):
            users = data.pop('users')
        notify = None
        if request.data.get('notify'):
            notify = data.pop('notify')
            offices = data.pop('offices')
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        # Codes are update  Saiful
        try:
            current_training_batch = TrainingBatch.objects.get(pk=instance.id)
            print('current ', current_training_batch)
        except TrainingBatch.DoesNotExist:
            raise ValidationError('Does not exit Training Batch')
        except TrainingBatch.MultipleObjectsReturned:
            raise ValidationError('Multiple Training Batch is found for same Training ID')

        if current_training_batch.status == 3:
            raise ValidationError('Completed training batch can\'t updaate!')

        if request.data.get('finalized'):
            if notify:
                serializer.instance.status = 4
            else:
                if current_training_batch.status == 0:
                    serializer.instance.status = 1
                elif current_training_batch.status == 2:
                    serializer.instance.status = 4

        if current_training_batch.status == 5:
            serializer.instance.status = 0
            participants = TrainingUser.objects.filter(training=instance.id)
            for participant in participants:
                participant.status = False
                participant.save()
        # Saiful
        training_id = instance.id
        training = TrainingBatch.objects.get(id=training_id)
        training_user = list(TrainingUser.objects.filter(training=training).values_list('user', flat=True))
        if users:
            for user_id in users:
                user = User.objects.get(id=user_id)
                param = {
                    'name': user.get_full_name(),
                    'organization': training.organization,
                    'training_category': training.training_category,
                    'start_date': training.start_date,
                    'end_date': training.end_date,
                    'office': training.office.name,
                    'office_category': training.office.office_category,
                    'batch_number': training.batch_number,
                    'venue': training.venue,
                    'training_name': training.training_name,
                    'header': 'Dear Sir,' if user.profile.gender == 'Male' else 'Dear Madam,'
                }

                if user.profile.personal_email:
                    email_to = user.profile.personal_email
                if not email_to and user.profile.official_email:
                    email_to = user.profile.official_email

                subject = 'You have a training from ' + user.profile.office.office_category + ' # ' + str(training.id)

                html_content = render_to_string('email/training_user_email_notification.html', param)
                html_content = html.escape(html_content)
                if not (int(user_id) in training_user):
                    TrainingUser.objects.create(user=user, training=training, mail_body=html_content, to=email_to, from_e=settings.EMAIL_HOST_USER, subject=subject)
                if notify:
                    views.send_mail_to_user(user_id=user_id, training_id=training_id)
                # TrainingUser.objects.create(user=user, training=training)
            new_training_user = list(TrainingUser.objects.filter(training=training).values_list('user', flat=True))
            for user_id in new_training_user:
                if user_id not in list(map(int, users)):
                    TrainingUser.objects.filter(user__id=user_id, training__id=training_id).delete()
        if users:
            for user_id in users:
                training_user = TrainingUser.objects.filter(user__id=user_id, training__id=training_id)[0]
                if data.get('certificates' + user_id):
                    training_user.certificate = data.get('certificates' + user_id)
                    training_user.save()

        self.perform_update(serializer)
        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        if notify:
            announcement = Announcement.objects.filter(training_status=training_id)
            end_date = serializer.instance.end_date
            start_date = serializer.instance.start_date
            if announcement.count() == 0:
                announcement = Announcement.objects.create(expired_date=end_date, created_by=self.request.user,
                                                           title='You have a training in ' + start_date.strftime(
                                                               '%d/%m/%y'), training_status=training_id)
                announcement.office = list(map(int, offices))
            else:
                announcement = announcement[0]
                announcement.expired_date = end_date
                announcement.created_by = self.request.user
                announcement.title = 'You have a training in ' + start_date.strftime('%d/%m/%y')
                announcement.office = list(map(int, offices))
                announcement.save()
        return Response(serializer.data)

    def get_queryset(self):
        # qs = super().get_queryset()
        qs = get_training_filter(self.request)
        return qs.order_by('updated_at').distinct()


# ----------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------- Nominated Official -----------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# class NominatedOfficialViewSet(BaseViewSet):
#     queryset = NominatedOfficial.objects.all()
#     serializer_class = NominatedOfficialSerializer
#     pagination_class = LargeResultsSetPagination
#     permission_classes = [permissions.IsAuthenticated]
#     search_fields = ('external_office',)
#
#     def get_queryset(self):
#         qs = super().get_queryset()
#         return qs.filter().order_by('-updated_at')


# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------- Publication --------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class PublicationViewSet(BaseViewSet):
    queryset = Publication.objects.all()
    serializer_class = PublicationSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.AllowAny]
    search_fields = ('title', 'type__type')

    def get_queryset(self):
        qs = super().get_queryset()
        genre = self.request.GET.get('genre')
        parent = self.request.GET.get('parent')
        organization_list = self.request.GET.get('organization_list')
        office_category_list = self.request.GET.get('office_category_list')
        office_list = self.request.GET.get('office_list')
        all = self.request.GET.get('all')
        filters = {}
        if organization_list:
            filters['office__organization__in'] = organization_list.split(",")
        if office_category_list:
            filters['office__office_category__in'] = office_category_list.split(",")
        if office_list:
            filters['office__in'] = office_list.split(',')
        if all is not None and all:
            filters = {}
        qs = qs.filter(**filters).distinct()
        if genre:
            qs = qs.filter(genre=genre)
        if parent:
            qs = qs.filter(parent=parent) if parent != '-1' else qs.filter(parent__isnull=True)
        return qs.order_by('-genre', '-updated_at')


# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------- Gallery --------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class GalleryViewSet(BaseViewSet):
    queryset = Gallery.objects.all()
    serializer_class = GallerySerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_update(self, serializer):
        if self.request.data.get('value'):
            Gallery.objects.filter(pk=self.request.data['pk']).update(title=self.request.data['value'])
        if self.request.data.get('for_homepage'):
            Gallery.objects.filter(pk=self.request.data['pk']).update(
                for_homepage=int(self.request.data['for_homepage']))
        if self.request.data.get('date'):
            Gallery.objects.filter(pk=self.request.data['pk']).update(
                date=self.request.data.get('date'))

    def get_queryset(self):
        qs = super().get_queryset()
        parent = self.request.GET.get('parent')
        type = self.request.GET.get('type')

        if type:
            qs = qs.filter(type=type)
        if parent:
            qs = qs.filter(parent__id=parent) if parent != '-1' else qs.filter(parent__isnull=True)
        if self.request.user.is_anonymous:
            return qs.filter(Q(for_homepage=1) | Q(type='Folder')).order_by('-type', 'id')
        return qs.order_by('-type', 'id')


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------- Transfer History -----------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
def is_blank_user(obj):
    if obj.profile.mobile_no or obj.profile.date_of_birth or obj.profile.gender or \
            obj.profile.bengali_name or obj.profile.avatar or \
            obj.profile.nid or obj.first_name or obj.profile.personal_email or obj.profile.PPR_training:
        return False
    if TrainingUser.objects.filter(user=obj).count() != 0:
        return False
    return True


def set_personal_info_as_null(user):
    profile = user.profile
    Profile.objects.filter(id=profile.id).update(mobile_no=None, date_of_birth=None, gender=None,
                                                 bengali_name=None, avatar=None, nid=None, personal_email=None,
                                                 PPR_training=None)

    User.objects.filter(id=user.id).update(first_name=None)
    TrainingUser.objects.filter(user=user).update(user=None)


def save_personal_info(user):
    profile = user.profile
    personal_info = {
        "mobile_no": profile.mobile_no,
        "date_of_birth": profile.date_of_birth.isoformat() if profile.date_of_birth else None,
        "gender": profile.gender,
        "bengali_name": profile.bengali_name,
        "avatar": profile.avatar.name if profile.avatar else None,
        "nid": profile.nid,
        "personal_email": profile.personal_email,
        "PPR_training": profile.PPR_training,
        "first_name": user.first_name,
        "training_history": list(TrainingUser.objects.filter(user=user).values_list('id', flat=True)),
        # "external_member_nominee_history": list(ExternalMember.objects.filter(user=user).values_list('id', flat=True)),
        # "audit_trail_history": list(AuditTrail.objects.filter(user=user).values_list('id', flat=True))
    }
    return personal_info


def set_official_info_as_null(user):
    profile = user.profile
    Profile.objects.filter(id=profile.id).update(official_email=None, official_mobile_no=None,
                                                 e_gp_user_id_for_govt=None, e_gp_user_id_lgis_for_govt=None,
                                                 e_gp_user_id_for_org_admin=None, e_gp_user_id_lgis_for_org_admin=None,
                                                 e_gp_user_id_for_pe_admin=None, e_gp_user_id_lgis_for_pe_admin=None,
                                                 designation=None, office=None, floating=True)
    proc_role_list = Profile.objects.get(id=profile.id).procurement_roles.values_list('id', flat=True)
    proc_role_lgis_list = Profile.objects.get(id=profile.id).procurement_roles_lgis.values_list('id', flat=True)
    for role in proc_role_list:
        obj = ProcurementRole.objects.get(id=role)
        Profile.objects.get(id=profile.id).procurement_roles.remove(obj)
    for role in proc_role_lgis_list:
        obj = ProcurementRole.objects.get(id=role)
        Profile.objects.get(id=profile.id).procurement_roles_lgis.remove(obj)
    User.objects.filter(id=user.id).update(email=None)


def save_official_info(user):
    profile = user.profile
    official_info = {
        "official_email": profile.official_email,
        "official_mobile_no": profile.official_mobile_no,
        "e_gp_user_id_for_govt": profile.e_gp_user_id_for_govt,
        "e_gp_user_id_lgis_for_govt": profile.e_gp_user_id_lgis_for_govt,
        "e_gp_user_id_for_org_admin": profile.e_gp_user_id_for_org_admin,
        "e_gp_user_id_lgis_for_org_admin": profile.e_gp_user_id_lgis_for_org_admin,
        "e_gp_user_id_for_pe_admin": profile.e_gp_user_id_for_pe_admin,
        "e_gp_user_id_lgis_for_pe_admin": profile.e_gp_user_id_lgis_for_pe_admin,
        "designation": profile.designation.id,
        "office": profile.office.id,
        "email": user.email,
        "procurement_roles": list(
            Profile.objects.get(id=profile.id).procurement_roles.all().values_list('id', flat=True)),
        "procurement_roles_lgis": list(
            Profile.objects.get(id=profile.id).procurement_roles_lgis.all().values_list('id', flat=True))
    }

    return official_info


def create_blank_user(official_info):
    new_profile = Profile.objects.create(official_email=official_info["official_email"],
                                         official_mobile_no=official_info["official_mobile_no"],
                                         e_gp_user_id_for_govt=official_info["e_gp_user_id_for_govt"],
                                         e_gp_user_id_lgis_for_govt=official_info["e_gp_user_id_lgis_for_govt"],
                                         e_gp_user_id_for_org_admin=official_info["e_gp_user_id_for_org_admin"],
                                         e_gp_user_id_lgis_for_org_admin=official_info[
                                             "e_gp_user_id_lgis_for_org_admin"],
                                         e_gp_user_id_for_pe_admin=official_info["e_gp_user_id_for_pe_admin"],
                                         e_gp_user_id_lgis_for_pe_admin=official_info["e_gp_user_id_lgis_for_pe_admin"],
                                         designation_id=official_info["designation"], office_id=official_info["office"])
    for proc_role in official_info["procurement_roles"]:
        new_profile.procurement_roles.add(ProcurementRole.objects.get(id=proc_role))
    for proc_role_lgis in official_info["procurement_roles_lgis"]:
        new_profile.procurement_roles_lgis.add(ProcurementRole.objects.get(id=proc_role_lgis))
    return User.objects.create(email=official_info["email"], profile=new_profile)


def create_floating_user(personal_info):
    new_profile = Profile.objects.create(mobile_no=personal_info["mobile_no"],
                                         date_of_birth=datetime.datetime.strptime(personal_info["date_of_birth"],
                                                                                  '%Y-%m-%d') if personal_info[
                                             "date_of_birth"] else None,
                                         gender=personal_info["gender"],
                                         bengali_name=personal_info["bengali_name"],
                                         nid=personal_info["nid"],
                                         personal_email=personal_info["personal_email"],
                                         PPR_training=personal_info["PPR_training"], floating=True)
    new_profile.avatar.name = personal_info["avatar"]
    new_profile.save()
    new_user = User.objects.create(first_name=personal_info["first_name"], profile=new_profile)
    TrainingUser.objects.filter(id__in=personal_info["training_history"]).update(user=new_user)
    return new_user


def replace_personal_information(user_to_be_updated, instance):
    # if Arani PS's user is transferred to Akhaura PS, then user's info is in instance.personal_info,
    # user_to_be_updated belongs to
    # Akhaura PS....user_to_be_updated's personal info is going to be replaced by user's personal info
    personal_info = instance.previous_personal_info
    Profile.objects.filter(id=user_to_be_updated.profile.id).update(mobile_no=personal_info["mobile_no"],
                                                                    date_of_birth=datetime.datetime.strptime(
                                                                        personal_info["date_of_birth"], '%Y-%m-%d') if
                                                                    personal_info["date_of_birth"] else None,
                                                                    gender=personal_info["gender"],
                                                                    bengali_name=personal_info["bengali_name"],
                                                                    nid=personal_info["nid"],
                                                                    personal_email=personal_info["personal_email"],
                                                                    PPR_training=personal_info["PPR_training"])

    profile = Profile.objects.get(id=user_to_be_updated.profile.id)
    profile.avatar.name = personal_info["avatar"]
    profile.save()

    User.objects.filter(id=user_to_be_updated.id).update(first_name=personal_info["first_name"])
    TrainingUser.objects.filter(id__in=personal_info["training_history"]).update(user=user_to_be_updated)
    # AuditTrail.objects.filter(id__in=personal_info["audit_trail_history"]).update(user=user_to_be_updated)
    # ExternalMember.objects.filter(id__in=personal_info["external_member_nominee_history"]).update(user=user_to_be_updated)


def restore_official_information(user, instance):
    profile = user.profile
    official_info = instance.previous_official_info
    Profile.objects.filter(id=profile.id).update(official_email=official_info["official_email"],
                                                 official_mobile_no=official_info["official_mobile_no"],
                                                 e_gp_user_id_for_govt=official_info["e_gp_user_id_for_govt"],
                                                 e_gp_user_id_lgis_for_govt=official_info["e_gp_user_id_lgis_for_govt"],
                                                 e_gp_user_id_for_org_admin=official_info["e_gp_user_id_for_org_admin"],
                                                 e_gp_user_id_lgis_for_org_admin=official_info[
                                                     "e_gp_user_id_lgis_for_org_admin"],
                                                 e_gp_user_id_for_pe_admin=official_info["e_gp_user_id_for_pe_admin"],
                                                 e_gp_user_id_lgis_for_pe_admin=official_info[
                                                     "e_gp_user_id_lgis_for_pe_admin"],
                                                 designation=official_info["designation"],
                                                 office=official_info["office"],
                                                 floating=False)
    for proc_role in official_info["procurement_roles"]:
        Profile.objects.get(id=profile.id).procurement_roles.add(ProcurementRole.objects.get(id=proc_role))
    for proc_role_lgis in official_info["procurement_roles_lgis"]:
        Profile.objects.get(id=profile.id).procurement_roles_lgis.add(ProcurementRole.objects.get(id=proc_role_lgis))
    User.objects.filter(id=user.id).update(email=official_info["email"])


def restore_personal_information(user, instance):
    profile = user.profile
    personal_info = instance.previous_personal_info
    Profile.objects.filter(id=profile.id).update(mobile_no=personal_info["mobile_no"],
                                                 date_of_birth=datetime.datetime.strptime(
                                                     personal_info["date_of_birth"], '%Y-%m-%d') if personal_info[
                                                     "date_of_birth"] else None,
                                                 gender=personal_info["gender"],
                                                 bengali_name=personal_info["bengali_name"],
                                                 nid=personal_info["nid"],
                                                 personal_email=personal_info["personal_email"],
                                                 PPR_training=personal_info["PPR_training"])
    profile = Profile.objects.get(user__id=user.id)
    profile.avatar.name = personal_info["avatar"]
    profile.save()

    User.objects.filter(id=user.id).update(first_name=personal_info["first_name"])
    TrainingUser.objects.filter(id__in=personal_info["training_history"]).update(user=user)


class TransferHistoryViewSet(BaseViewSet):
    queryset = TransferHistory.objects.all()
    serializer_class = TransferHistorySerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]

    search_fields = (
        'user__profile__office__name', 'user__profile__designation__designation', 'user__profile__official_mobile_no',
        'user__email', 'transferred_office__name', 'new_designation__designation', 'charge_takeover_date',
        'charge_handover_date', 'transfer_memo_no',)
    ordering_fields = (
        '', '', '', '', '', '', 'transferred_office__name',
        'new_designation__designation', 'charge_takeover_date', 'charge_handover_date',
        'transfer_memo_no', '', '', '', 'updated_at', '')

    def perform_create(self, serializer):
        with transaction.atomic():
            instance = serializer.save()
            user = instance.user

            official_info = save_official_info(user)
            personal_info = save_personal_info(user)
            if not instance.blank_user:
                # transfer to
                set_official_info_as_null(user)
                created_blank_user = create_blank_user(official_info)
                instance.blank_user = created_blank_user
            else:
                # transfer from
                set_personal_info_as_null(user)
                created_floating_user = create_floating_user(personal_info)
                instance.floating_user = created_floating_user

            instance.previous_official_info = official_info
            instance.previous_personal_info = personal_info
            instance.save()
            views.audit_trail_record(self.request, instance, {}, "USER TRANSFER", 'CREATE')

    def perform_update(self, serializer):
        prev_data = get_user_transfer_data(self.get_object().id)
        serializer.save()
        instance = self.get_object()
        if instance.approved_status == 1 and instance.transfer_type == 0:  # transfer to approve
            try:
                with transaction.atomic():
                    user = instance.user
                    # finding user to be updated
                    users_with_same_desg = User.objects.filter(profile__designation=instance.new_designation,
                                                               profile__office=instance.transferred_office)
                    user_to_be_updated = None
                    if users_with_same_desg:
                        for temp in users_with_same_desg:
                            if is_blank_user(temp):
                                user_to_be_updated = temp
                                break
                    else:  # no user found with same designation
                        raise ValueError('No post with the given designation in the new office')

                    if not user_to_be_updated:  # no blank user found with that designation in transferred office
                        raise ValueError('No vacant post found with that designation in the new office')

                    instance.transferred_user = user_to_be_updated
                    instance.save()

                    for c in User._meta.get_fields():
                        if isinstance(c, ManyToOneRel) or isinstance(c, OneToOneRel) or isinstance(c, ManyToManyRel) or \
                                isinstance(c, ForeignObjectRel):
                            variable_column = c.field.name
                            c.related_model.objects.filter(**{variable_column: user}).update(**{variable_column:
                                                                                                    user_to_be_updated})
                    user.profile.delete()
                    user.delete()
                    # replacing user_to_be_updated's personal info with the transferred user's info
                    replace_personal_information(user_to_be_updated, instance)
            except Exception as e:
                instance.approved_status = 0
                instance.save()
                raise ValidationError(e)

        elif instance.approved_status == 1 and instance.transfer_type == 1:  # transfer from approve
            try:
                with transaction.atomic():
                    blank_user = instance.blank_user
                    floating_user = instance.floating_user
                    instance.floating_user = None
                    instance.save()
                    if floating_user:
                        for c in User._meta.get_fields():
                            if isinstance(c, ManyToOneRel) or isinstance(c, OneToOneRel) or isinstance(c,
                                                                                                       ManyToManyRel) or \
                                    isinstance(c, ForeignObjectRel):
                                variable_column = c.field.name
                                c.related_model.objects.filter(**{variable_column: floating_user}) \
                                    .update(**{variable_column: None})
                        floating_user.profile.delete()
                        floating_user.delete()
                    replace_personal_information(blank_user, instance)
            except Exception as e:
                instance.approved_status = 0
                instance.save()
                raise ValidationError(e)

        elif instance.approved_status == 3 and instance.transfer_type == 0:  # transfer to rollback
            try:
                with transaction.atomic():
                    user = instance.user
                    if not is_blank_user(instance.blank_user):
                        raise ValueError('No vacant post found with that designation in the previous office')
                    blank_user = instance.blank_user
                    instance.blank_user = None
                    instance.save()
                    if blank_user:
                        for c in User._meta.get_fields():
                            if isinstance(c, ManyToOneRel) or isinstance(c, OneToOneRel) or isinstance(c,
                                                                                                       ManyToManyRel) or \
                                    isinstance(c, ForeignObjectRel):
                                variable_column = c.field.name
                                c.related_model.objects.filter(**{variable_column: blank_user}).update(
                                    **{variable_column: user})
                        blank_user.profile.delete()
                        blank_user.delete()
                    restore_official_information(user, instance)

            except Exception as e:
                instance.approved_status = 0
                instance.save()
                raise ValidationError(e)

        elif instance.approved_status == 3 and instance.transfer_type == 1:  # transfer from rollback
            try:
                with transaction.atomic():
                    user = instance.user
                    if not is_blank_user(user):
                        raise ValueError('No vacant post found with that designation in the previous office')
                    floating_user = instance.floating_user
                    instance.floating_user = None
                    instance.save()
                    if floating_user:
                        for c in User._meta.get_fields():
                            if isinstance(c, ManyToOneRel) or isinstance(c, OneToOneRel) or isinstance(c,
                                                                                                       ManyToManyRel) or \
                                    isinstance(c, ForeignObjectRel):
                                variable_column = c.field.name
                                c.related_model.objects.filter(**{variable_column: floating_user}) \
                                    .update(**{variable_column: None})
                        floating_user.profile.delete()
                        floating_user.delete()
                    restore_personal_information(user, instance)

            except Exception as e:
                instance.approved_status = 0
                instance.save()
                raise ValidationError(e)
        views.audit_trail_record(self.request, instance, prev_data, "USER TRANSFER", 'UPDATE')

    def perform_destroy(self, instance):
        # instance.user.profile.floating = False
        # instance.user.profile.save()
        instance.delete()

    def get_queryset(self):
        qs = super().get_queryset()
        office = self.request.GET.get('id')
        organization = self.request.GET.get('organization')
        office_category = self.request.GET.get('office_category')
        office_id = self.request.GET.get('office')
        user_id = self.request.GET.get('user')
        name_adv = self.request.GET.get('name_adv')
        mobile_no_adv = self.request.GET.get('mobile_no_adv')
        designation_adv = self.request.GET.get('designation_adv')

        user_permissions = list(self.request.user.profile.role.permission.values_list('code', flat=True))
        user_office_id = self.request.user.profile.office.id
        if 'transfer_admin' not in user_permissions:
            # qs_copy = qs
            # qs = qs.filter(user__profile__office__id=user_office_id)
            # qs_copy = qs_copy.filter(blank_user__id=self.request.user.id)
            # qs = qs | qs_copy
            qs = qs.filter(previous_official_info__office=user_office_id)
        if office:
            qs = qs.filter(transferred_office=office)
        if user_id:
            qs = qs.filter(user__id=user_id)
        if organization:
            qs = qs.filter(transferred_office__organization=organization)
        if office_category:
            qs = qs.filter(transferred_office__office_category=office_category)
        if designation_adv:
            qs = qs.filter(new_designation=designation_adv)
        if mobile_no_adv:
            qs = qs.filter(user__profile__mobile_no__icontains=mobile_no_adv)
        if name_adv:
            qs = qs.filter(user__first_name__icontains=name_adv)
        if office_id:
            qs = qs.filter(transferred_office__id=office_id)

        return qs.order_by('-created_at')


class MultipleAssignHistoryViewSet(BaseViewSet):
    queryset = MultipleAssignHistory.objects.all()
    serializer_class = MultipleAssignHistorySerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]

    search_fields = (
        'user__profile__office__name', 'user__profile__designation__designation', 'user__profile__official_mobile_no',
        'user__email', 'assigned_office__name', 'new_designation__designation', 'charge_takeover_date',
        'charge_handover_date', 'multiassign_memo_no',)
    ordering_fields = (
        '', '', '', '', '', '', 'assigned_office__name',
        'new_designation__designation', 'charge_takeover_date', 'charge_handover_date',
        'multiassign_memo_no', '', '', '', 'updated_at', '')

    def create(self, request, *args, **kwargs):
        instance = request.data
        unassigned_office_info = Profile.objects.filter(id=instance['new_designation'])[0]

        user = User.objects.get(profile=instance['new_designation'])

        if unassigned_office_info:
            temp_office = TemporaryOffice.objects.create(user_id=instance['user'],
                                                         blank_user_id=user.id,
                                                         office_id=instance['assigned_office'],
                                                         designation=unassigned_office_info.designation,
                                                         official_mobile_no=unassigned_office_info.official_mobile_no,
                                                         official_email=unassigned_office_info.official_email,
                                                         e_gp_user_id=unassigned_office_info.e_gp_user_id,
                                                         e_gp_user_id_lgis=unassigned_office_info.e_gp_user_id_lgis,
                                                         e_gp_user_id_for_govt=unassigned_office_info.e_gp_user_id_for_govt,
                                                         e_gp_user_id_lgis_for_govt=unassigned_office_info.e_gp_user_id_lgis_for_govt,
                                                         e_gp_user_id_for_org_admin=unassigned_office_info.e_gp_user_id_for_org_admin,
                                                         e_gp_user_id_lgis_for_org_admin=unassigned_office_info.e_gp_user_id_lgis_for_org_admin,
                                                         e_gp_user_id_for_pe_admin=unassigned_office_info.e_gp_user_id_for_pe_admin,
                                                         e_gp_user_id_lgis_for_pe_admin=unassigned_office_info.e_gp_user_id_lgis_for_pe_admin)
            user_id = instance['user']
            user = User.objects.filter(id=user_id)[0]

            official_info = save_official_info(user)
            personal_info = save_personal_info(user)

            multiple_assign = MultipleAssignHistory.objects.create(user_id=user_id,
                                                                   assigned_office_id=instance['assigned_office'],
                                                                   previous_official_info=official_info,
                                                                   previous_personal_info=personal_info,
                                                                   multiassign_memo_no=instance['multiassign_memo_no'],
                                                                   new_designation=unassigned_office_info.designation)
            if 'charge_handover_date' in instance:
                multiple_assign.charge_handover_date = instance['charge_handover_date']

            multiple_assign.save()

            all_procurement_roles = list(unassigned_office_info.procurement_roles.all())
            all_procurement_roles_lgis = list(unassigned_office_info.procurement_roles_lgis.all())
            if all_procurement_roles:
                temp_office.procurement_roles.add(*all_procurement_roles)
            if all_procurement_roles_lgis:
                temp_office.procurement_roles_lgis.add(*all_procurement_roles_lgis)
            temp_office.save()
            unassigned_office_info.is_temp_office_assign = True
            unassigned_office_info.save()
        return JsonResponse({'success': True}, status=200)

    def get_queryset(self):
        qs = super().get_queryset()
        organization = self.request.GET.get('organization')
        office_category = self.request.GET.get('office_category')
        office_id = self.request.GET.get('office')
        user_id = self.request.GET.get('user')
        designation = self.request.GET.get('designation')
        name = self.request.GET.get('name')
        mobile = self.request.GET.get('mobile')

        user_permissions = list(self.request.user.profile.role.permission.values_list('code', flat=True))
        user_office_id = self.request.user.profile.office.id
        if 'transfer_admin' not in user_permissions:
            # qs_copy = qs
            # qs = qs.filter(user__profile__office__id=user_office_id)
            # qs_copy = qs_copy.filter(blank_user__id=self.request.user.id)
            # qs = qs | qs_copy
            qs = qs.filter(previous_official_info__office=user_office_id)
        if office_id:
            qs = qs.filter(assigned_office=office_id)
        if user_id:
            qs = qs.filter(user__id=user_id)
        if organization:
            qs = qs.filter(assigned_office__organization=organization)
        if office_category:
            qs = qs.filter(assigned_office__office_category=office_category)
        if name:
            qs = qs.filter(user__in=User.objects.filter(first_name__contains=name))
        if designation:
            qs = qs.filter(new_designation__in=Designation.objects.filter(designation__contains=designation))
        if mobile:
            qs = qs.filter(assigned_office__in=Office.objects.filter(phone_no=mobile))
            print(qs)

        return qs.order_by('-created_at')


class BudgetTypeViewSet(BaseViewSet):
    queryset = BudgetType.objects.all()
    serializer_class = BudgetTypeSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_fields = ('type',)

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter().order_by('type')


class ProcurementNatureViewSet(BaseViewSet):
    queryset = ProcurementNature.objects.all()
    serializer_class = ProcurementNatureSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_fields = ('nature',)

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter().order_by('-weight')


class CommitteeTypeViewSet(BaseViewSet):
    queryset = CommitteeType.objects.all()
    serializer_class = CommitteeTypeSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_fields = ('type',)

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter().order_by('type')


class TypeOfEmergencyViewSet(BaseViewSet):
    queryset = TypeOfEmergency.objects.all()
    serializer_class = TypeOfEmergencySerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_fields = ('type',)

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter().order_by('type')


class ProcMethodViewSet(BaseViewSet):
    queryset = ProcMethod.objects.all()
    serializer_class = ProcMethodSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_fields = ('method',)

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter().order_by('-weight')


class ProcTypeViewSet(BaseViewSet):
    queryset = ProcType.objects.all()
    serializer_class = ProcTypeSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_fields = ('type',)

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter().order_by('-weight')


class SourceOfFundViewSet(BaseViewSet):
    queryset = SourceOfFund.objects.all()
    serializer_class = SourceOfFundSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_fields = ('source',)

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter().order_by('-weight')


class FundDisburseFromViewSet(BaseViewSet):
    queryset = FundDisburseFrom.objects.all()
    serializer_class = FundDisburseFromSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_fields = ('source',)

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter().order_by('-weight')


class FundedByViewSet(BaseViewSet):
    queryset = FundedBy.objects.all()
    serializer_class = FundedBySerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_fields = ('funded_by',)

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter().order_by('funded_by')


class ApprovingAuthorityViewSet(BaseViewSet):
    queryset = ApprovingAuthority.objects.all()
    serializer_class = ApprovingAuthoritySerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_fields = ('authority',)

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter().order_by('-weight')


class ContractStatusViewSet(BaseViewSet):
    queryset = ContractStatus.objects.all()
    serializer_class = ContractStatusSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = LargeResultsSetPagination
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_fields = ('status',)

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter().order_by('status')


class APPViewSet(BaseViewSet):
    queryset = APP.objects.all()
    serializer_class = APPSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = LargeResultsSetPagination

    search_fields = (
        'office__name', 'office__division__name', 'office__region__name', 'office__district__name',
        'office__upazila__name', 'budget_type__type', 'proc_nature__nature', 'type_of_emergency__type', 'type',
        'app_id',
        'financial_year', 'project__name')
    ordering_fields = (
        '', 'office__name', 'office__division__name', 'office__region__name', 'office__district__name',
        'office__upazila__name', 'type', 'app_id', 'financial_year', 'budget_type__type', 'project__name',
        'proc_nature__nature', 'type_of_emergency__type')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = json.dumps(request.data)
        data2 = json.loads(data)

        project = data2['project_name']
        create_project = True
        if project.isdigit():
            create_project = False
            project_id = int(project)
            try:
                project_ob = Project.objects.get(pk=project_id)
                serializer.validated_data.update({'project': project_ob})
            except Project.DoesNotExist:
                create_project = True
        if create_project:
            # print('create project')
            project_ob = Project.objects.create(name=project, office=self.request.user.profile.office,
                                                status='Pending')
            serializer.validated_data.update({'project': project_ob})
        serializer.save()

        packages = data2['packages']
        # serializer.validated_data.pop('packages')
        office = serializer.validated_data['office']
        app = self.perform_create(serializer)
        for package in packages:
            package['proc_method'] = ProcMethod.objects.get(pk=int(package['proc_method']))
            package['proc_type'] = ProcType.objects.get(pk=int(package['proc_type']))
            package['type_of_emergency'] = TypeOfEmergency.objects.get(pk=int(package['type_of_emergency']))
            package['approving_authority'] = ApprovingAuthority.objects.get(pk=int(package['approving_authority']))
            package['proc_nature'] = ProcurementNature.objects.get(pk=int(package['proc_nature']))
            # package['proc_type'] = ProcType.objects.get(pk=int(package['proc_type']))
            # package['source_of_fund'] = SourceOfFund.objects.get(pk=int(package['source_of_fund']))
            try:
                package = Package.objects.create(app_id=app, office=office, **package)
                lot = Lot.objects.create(package_no=package, office=office)
            except Exception as e:
                Lot.objects.filter(package_no__app_id=app).delete()
                Package.objects.filter(app_id=app).delete()
                APP.objects.filter(id=app.id).delete()
                raise ValidationError({"package": [package['package_no'] + " Package no already exists"]})

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    # def perform_create(self, serializer):
    # project = serializer.validated_data.pop('project')
    # create_project = True
    # if project['name'].isdigit():
    #     create_project = False
    #     project_id = int(project['name'])
    #     try:
    #         project_ob = Project.objects.get(pk=project_id)
    #         serializer.validated_data.update({'project': project_ob})
    #     except Project.DoesNotExist:
    #         create_project = True
    # if create_project:
    #     # print('create project')
    #     project_ob = Project.objects.create(name=project['name'], office=self.request.user.profile.office,
    #                                         status='Pending')
    #     serializer.validated_data.update({'project': project_ob})
    # serializer.save()
    # app = serializer.instance
    # package = Package.objects.create(app_id=app, office=app.office, lot_no=1)
    # lot = Lot.objects.create(package_no=package, office=app.office)
    # tender = Tender.objects.create(lot=lot, office=app.office)
    # firm = Firm.objects.create(tender=tender)
    # contract = Contract.objects.create(tender_id=tender, office=app.office)

    def perform_update(self, serializer):
        try:
            project = serializer.validated_data.pop('project')
            create_project = True
            if project['name'].isdigit():
                create_project = False
                project_id = int(project['name'])
                try:
                    project_ob = Project.objects.get(pk=project_id)
                    serializer.validated_data.update({'project': project_ob})
                except Project.DoesNotExist:
                    create_project = True
            if create_project:
                # print('create project')
                project_ob = Project.objects.create(name=project['name'], office=self.request.user.profile.office,
                                                    status='Pending')
                serializer.validated_data.update({'project': project_ob})
            serializer.save()
        except  Exception as e:
            serializer.validated_data.update({'status': "Approved"})
            serializer.save()

    def get_queryset(self):
        qs = super().get_queryset()
        qs = get_app_filter(self.request, qs)
        return qs.filter().order_by('app_id')


class APPReportViewSet(viewsets.ViewSet):
    queryset = Package.objects.all()
    # serializer_class = APPReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = LargeResultsSetPagination

    def read_parameters(self, query_dict):
        """ Converts and cleans up the GET parameters. """
        params = {field: int(query_dict[field]) for field
                  in ['draw', 'start', 'length']}

        column_index = 0
        has_finished = False
        details = []
        while not has_finished:
            column_base = 'columns[%d]' % column_index
            try:
                column_name = query_dict[column_base + '[data]']
                if column_name != '':
                    orderable = query_dict.get(column_base + '[orderable]'),
                    searchable = query_dict.get(column_base + '[searchable]')
                    details.append({'index': column_index, 'column_name': column_name,
                                    'searchable': searchable, 'orderable': orderable[0]})
            except KeyError:
                has_finished = True
            column_index += 1

        order_index = 0
        # has_finished = False
        while order_index < column_index:
            try:
                order_base = 'order[%d]' % order_index
                order_column = query_dict[order_base + '[column]']
                order_direction = query_dict[order_base + '[dir]']
                # details[int(order_column) - 1]['order_dir'] = order_direction
                params['order_dir'] = order_direction
                params['order_column'] = order_column
                params['column_name'] = details[int(order_column) - 1]['column_name']
            except KeyError:
                order_index += 1
                continue
            order_index += 1

        search_value = query_dict.get('search[value]')
        if search_value:
            params['search_value'] = search_value

        params.update({'details': details})
        return params

    def to_repr(self, obj):
        office = Office.objects.get(id=obj['app_id__office'])
        data = {
            'e_GP_Packages': obj['e_GP_Packages'],
            'offline_Packages': obj['offline_Packages'],
            'e_GP_percentage': obj['e_GP_percentage'],
            'offline_percentage': obj['offline_percentage'],
            'office': obj['app_id__office'],
            'office_name': office.name,
            'division_name': office.division.name if office.division is not None else '',
            'upazila_name': office.upazila.name if office.upazila is not None else '',
            'region_name': office.region.name if office.region is not None else '',
            'district_name': office.district.name if office.district is not None else '',
        }
        return data

    def get_json_data(self, qs, datatable, records_total):
        json_data = []
        for item in qs:
            item = self.to_repr(item)
            json_data.append(item)
        if not datatable:
            return json_data
        json_dict = {}
        json_dict['draw'] = None
        json_dict['recordsFiltered'] = records_total
        json_dict['recordsTotal'] = records_total
        json_dict['data'] = json_data
        return json_dict

    def list(self, request):
        qs = Package.objects.all()
        qs = get_package_filter(self.request, qs)
        qs = qs.values('app_id__office').annotate(
            e_GP_Packages=Sum(Case(When(app_id__type='e-GP', then=1), output_field=IntegerField(), default=0)),
            offline_Packages=Sum(Case(When(app_id__type='Off-line', then=1), output_field=IntegerField(), default=0)))
        qs = qs.exclude(app_id__office=None)
        qs = qs.annotate(
            e_GP_percentage=F('e_GP_Packages') * 100 / (F('e_GP_Packages') + F('offline_Packages')),
            offline_percentage=F('offline_Packages') * 100 / (F('e_GP_Packages') + F('offline_Packages')),
        )
        datatable = request.GET.get('datatable')
        records_total = len(qs)
        if request.GET.get('draw'):
            data = self.read_parameters(request.query_params)
            # details = data['details']
            # for item in details:
            #     if item.get('order_dir'):
            #         column = item['column_name']
            #         if column == 'office_name':
            #             column = 'office__name'
            #         if column == 'division_name':
            #             column = 'office__division__name'
            #         if column == 'district_name':
            #             column = 'office__district__name'
            #         if column == 'upazila_name':
            #             column = 'office__upazila__name'
            #         if column == 'region_name':
            #             column = 'office__region__name'
            #         # if item['searchable'] == 'true' and data.get('search_value'):
            #         #     variable_column = column
            #         #     search_type = 'icontains'
            #         #     filter = variable_column + '__' + search_type
            #         #     qs = qs.filter(**{filter: data['search_value']})
            #         order_dir = data.get('order_dir')
            #         order_column = data.get('order_column')
            #         if item['orderable'] == 'true':
            #             if item['order_dir'] == 'desc':
            #                 column = '-' + column
            #                 qs = qs.order_by(column)
            #             else:
            #                 qs = qs.order_by(column)
            # qs = qs[data['start']: data['start'] + data['length']]
            order_dir = data.get('order_dir')
            column_name = data.get('column_name')
            if column_name == 'office_name':
                column_name = 'office__name'
            if column_name == 'division_name':
                column_name = 'office__division__name'
            if column_name == 'district_name':
                column_name = 'office__district__name'
            if column_name == 'upazila_name':
                column_name = 'office__upazila__name'
            if column_name == 'region_name':
                column_name = 'office__region__name'
            if order_dir == 'desc':
                column_name = '-' + column_name
                qs = qs.order_by(column_name)
            else:
                qs = qs.order_by(column_name)
        if request.GET.get('draw'):
            paginator = Paginator(qs, data['length'])
            page_id = (data['start'] // paginator.per_page) + 1
            if page_id > paginator.num_pages:
                page_id = paginator.num_pages
            elif page_id < 1:
                page_id = 1
            json_data = self.get_json_data(paginator.page(page_id), datatable, records_total)
        else:
            json_data = self.get_json_data(qs, datatable, records_total)
        # serializer = APPReportSerializer(qs, many=True)
        return Response(json_data)

    # def get_queryset(self):
    #     qs = Package.objects.all()
    #     qs = get_package_filter(self.request, qs)
    #     qs = qs.values('office').annotate(
    #         e_GP_Packages=Sum(Case(When(app_id__type='e-GP', then=1), output_field=IntegerField(), default=0)),
    #         offline_Packages=Sum(Case(When(app_id__type='Off-line', then=1), output_field=IntegerField(), default=0)))
    #     qs = qs.annotate(
    #         e_GP_percentage=F('e_GP_Packages') * 100 / (F('e_GP_Packages') + F('offline_Packages')),
    #         offline_percentage=F('offline_Packages') * 100 / (F('e_GP_Packages') + F('offline_Packages')),
    #     )
    #     datatable = self.request.GET.get('datatable')
    #     if self.request.GET.get('draw'):
    #         data = self.read_parameters(self.request.query_params)
    #         details = data['details']
    #         for item in details:
    #             column = item['column_name']
    #             if column == 'office_name':
    #                 column = 'office__name'
    #             if column == 'division_name':
    #                 column = 'office__division__name'
    #             if column == 'district_name':
    #                 column = 'office__district__name'
    #             if column == 'upazila_name':
    #                 column = 'office__upazila__name'
    #             if column == 'region_name':
    #                 column = 'office__region__name'
    #             # if item['searchable'] == 'true' and data.get('search_value'):
    #             #     variable_column = column
    #             #     search_type = 'icontains'
    #             #     filter = variable_column + '__' + search_type
    #             #     qs = qs.filter(**{filter: data['search_value']})
    #             if item['orderable'] == 'true' and item.get('order_dir'):
    #                 if item['order_dir'] == 'desc':
    #                     column = '-' + column
    #                     qs = qs.order_by(column)
    #                 else:
    #                     qs = qs.order_by(column)
    #         # print('ashiq', data)
    #     # serializer = APPReportSerializer(qs, many=True)
    #     json_data = self.get_json_data(qs, datatable)
    #     return Response(json_data)


class PackageViewSet(BaseViewSet):
    queryset = Package.objects.all()
    serializer_class = PackageSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = LargeResultsSetPagination

    search_fields = (
        'app_id__office__name', 'app_id__office__division__name', 'app_id__office__region__name',
        'app_id__office__district__name',
        'app_id__office__upazila__name', 'app_id__type', 'app_id__app_id', 'app_id__financial_year',
        'app_id__budget_type__type', 'app_id__source_of_fund__source', 'app_id__approval_date', 'app_id__no_of_package',
        'package_no', 'proc_nature__nature', 'type_of_emergency__type', 'approving_authority__authority',
        'package_description', 'proc_method__method', 'proc_type__type', 'app_id__project__name')
    ordering_fields = (
        '', 'app_id__office__name', 'app_id__office__division__name', 'app_id__office__region__name',
        'app_id__office__district__name',
        'app_id__office__upazila__name', 'app_id__type', 'app_id__app_id', 'app_id__financial_year',
        'app_id__budget_type__type', 'app_id__source_of_fund__source', 'app_id__approval_date', 'app_id__no_of_package',
        'package_no', 'proc_nature__nature', 'type_of_emergency__type', 'approving_authority__authority',
        'package_description', 'proc_method__method', 'proc_type__type', 'app_id__project__name', '')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        data = json.dumps(request.data)
        data2 = json.loads(data)
        lots = data2['lots']
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data.get('lots'):
            serializer.validated_data.pop('lots')
        office = serializer.validated_data.get('office')
        package = self.perform_create(serializer)
        if len(lots) == 0:
            lot = Lot.objects.create(package_no=package)
        total_cost = 0
        for lot_data in lots:
            lot_data['proc_method'] = ProcMethod.objects.get(pk=int(lot_data['proc_method']))
            lot_data['proc_type'] = ProcType.objects.get(pk=int(lot_data['proc_type']))
            lot_data['source_of_fund'] = SourceOfFund.objects.get(pk=int(lot_data['source_of_fund']))
            lot = Lot.objects.create(package_no=package, office=office, **lot_data)
            tender = Tender.objects.create(lot=lot, office=package.office)
            firm = Firm.objects.create(tender=tender)
            # contract = Contract.objects.create(tender_id=tender, office=package.office)
            total_cost += int(lot_data['cost'])
        package.app_cost = total_cost
        package.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    # def update(self, request, *args, **kwargs):
    #     partial = kwargs.pop('partial', False)
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance, data=request.data, partial=partial)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.validated_data.pop('lots')
    #     self.perform_update(serializer)
    #
    #     if getattr(instance, '_prefetched_objects_cache', None):
    #         # If 'prefetch_related' has been applied to a queryset, we need to
    #         # forcibly invalidate the prefetch cache on the instance.
    #         instance._prefetched_objects_cache = {}
    #
    #     return Response(serializer.data)

    def get_queryset(self):
        qs = super().get_queryset()
        qs = get_package_filter(self.request, qs)
        return qs.order_by('app_id__app_id')


# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------ Lot no --------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class LotViewSet(BaseViewSet):
    queryset = Lot.objects.all()
    serializer_class = LotSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    # filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    search_fields = (
        'package_no__app_id__office__name', 'package_no__app_id__office__division__name',
        'package_no__app_id__office__region__name', 'package_no__app_id__office__district__name',
        'package_no__app_id__office__upazila__name', 'package_no__app_id__type', 'package_no__app_id__app_id',
        'package_no__app_id__financial_year', 'package_no__app_id__budget_type__type',
        'package_no__app_id__source_of_fund__source', 'package_no__app_id__approval_date',
        'package_no__app_id__no_of_package', 'package_no__package_no',
        'package_no__proc_nature__nature', 'package_no__type_of_emergency__type',
        'package_no__approving_authority__authority', 'package_no__package_description',
        'package_no__proc_method__method', 'package_no__proc_type__type',
        'package_no__app_id__project__name', 'cost', 'lot_description', 'package_no__app_id__status',
        'package_no__app_id__id')
    ordering_fields = (
        '', 'package_no__app_id__office__name', 'package_no__app_id__office__division__name',
        'package_no__app_id__office__region__name', 'package_no__app_id__office__district__name',
        'package_no__app_id__office__upazila__name', 'package_no__app_id__type', 'package_no__app_id__app_id',
        'package_no__app_id__financial_year', 'package_no__app_id__budget_type__type',
        'package_no__app_id__source_of_fund__source', 'package_no__app_id__approval_date',
        'package_no__app_id__no_of_package', 'package_no__package_no',
        'package_no__proc_nature__nature', 'package_no__type_of_emergency__type',
        'package_no__approving_authority__authority', 'package_no__package_description',
        'package_no__proc_method__method', 'package_no__proc_type__type',
        'package_no__app_id__project__name', 'cost', 'lot_description', 'package_no__app_id__status', '', '')

    def perform_create(self, serializer):
        lots = self.request.data['lots']
        package_no = self.request.data['package_no']
        package_ob = Package.objects.get(id=int(package_no))
        prev_lots = Lot.objects.filter(package_no=package_ob)
        if prev_lots.count() == 1 and prev_lots[0].lot_description is None:
            prev_lots[0].delete()
        for lot in lots:
            Lot.objects.create(office=package_ob.office, package_no=package_ob, lot_description=lot['lot_description'],
                               cost=lot['cost'])

        # lot = serializer.save()
        # lot_no = Lot.objects.filter(package_no__package_no=serializer.validated_data['package_no']).count()
        # total_cost = Lot.objects.filter(package_no__package_no=serializer.validated_data['package_no']).aggregate(
        #     Sum('cost'))
        # Package.objects.filter(id=serializer.validated_data['package_no'].id).update(lot_no=lot_no,
        #                                                                              app_cost=total_cost['cost__sum'])
        # tender = Tender.objects.create(lot=lot, office=lot.office)
        # firm = Firm.objects.create(tender=tender)
        # contract = Contract.objects.create(tender_id=tender, office=lot.office)

    # def perform_update(self, serializer):
    #     serializer.save()
    #     total_cost = Lot.objects.filter(package_no__id=self.request.data['package_no']).aggregate(
    #         Sum('cost'))
    #     Package.objects.filter(id=serializer.validated_data['package_no'].id).update(app_cost=total_cost['cost__sum'])

    def get_queryset(self):
        qs = super().get_queryset()
        qs = get_lot_filter(self.request, qs)
        return qs.order_by('package_no__app_id__app_id', 'package_no', 'id')


class TenderCostViewSet(BaseViewSet):
    queryset = TenderCost.objects.all()
    serializer_class = TenderCostSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_fields = ('cost',)

    def get_queryset(self):
        qs = super().get_queryset()
        tender = self.request.GET.get('tender')
        if tender:
            qs = qs.filter(tender_id=tender)
        return qs.filter().order_by('created_at')


# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------ Tender --------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class TenderViewSet(BaseViewSet):
    queryset = Tender.objects.all()
    serializer_class = TenderSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = LargeResultsSetPagination

    search_fields = (
        'package__app_id__office__name', 'package__app_id__office__division__name',
        'package__app_id__office__region__name',
        'package__app_id__office__district__name', 'package__app_id__office__upazila__name', 'package__package_no',
        'approving_authority__authority', 'tender_id',
        'publication_date', 'closing_date', 'tender_validity', 'no_of_tender_doc_sold', 'no_of_tender_doc_received',
        'no_of_responsive_tenderer', 'approval_date', 'approving_authority__authority', 'status',
        'package__package_description')

    ordering_fields = (
        '', 'package__app_id__office__name', 'package__app_id__office__division__name',
        'package__app_id__office__region__name', 'package__app_id__office__district__name',
        'package__app_id__office__upazila__name', 'tender_id', 'package__app_id__app_id', 'package__package_no',
        'package__package_description', '', 'publication_date', 'closing_date', 'tender_validity',
        'no_of_tender_doc_sold',
        'no_of_tender_doc_received', 'no_of_responsive_tenderer',
        'approval_date', 'approving_authority__authority', 'status', '')

    def perform_create(self, serializer):
        data = serializer.validated_data
        tender_status = 'Ongoing'
        if 'approval_date' in data and data['approval_date']:
            tender_status = "Approved"
        elif 'closing_date' in data and data['closing_date']:
            tender_status = "Opening Completed"
        elif 'publication_date' in data and data['publication_date']:
            tender_status = "Published"
        if 'cancel_status' in self.request.data and self.request.data['cancel_status'] != 'False':
            tender_status = "Cancelled"
        serializer.validated_data.update({'status': tender_status})
        if serializer.validated_data['tender_status'] == 'Rejected' or \
                serializer.validated_data['tender_status'] == 'Re-tendered':
            serializer.validated_data.update({'status': serializer.validated_data['tender_status']})
        serializer.save()

    def perform_update(self, serializer):
        costs = json.loads(self.request.data['costs'])
        data = serializer.validated_data
        tender_status = 'Ongoing'
        if 'approval_date' in data and data['approval_date']:
            tender_status = "Approved"
        elif 'closing_date' in data and data['closing_date']:
            tender_status = "Opening Completed"
        elif 'publication_date' in data and data['publication_date']:
            tender_status = "Published"

        serializer.validated_data.update({'status': tender_status})
        if serializer.validated_data['tender_status'] == 'Rejected' or \
                serializer.validated_data['tender_status'] == 'Re-tendered':
            serializer.validated_data.update({'status': serializer.validated_data['tender_status']})
        if 'cancel_status' in self.request.data and self.request.data['cancel_status'] != 'False':
            serializer.validated_data.update({'status': "Cancelled"})
        tender = serializer.save()
        if costs:
            TenderCost.objects.filter(tender=tender).delete()
            for cost in costs:
                TenderCost.objects.create(cost=cost, tender=tender)

    def get_queryset(self):
        qs = super().get_queryset()
        qs = get_tender_filter(self.request, qs)
        return qs.filter().order_by('-updated_at')


# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------ Tender --------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class FirmViewSet(BaseViewSet):
    queryset = Firm.objects.all()
    serializer_class = FirmSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        qs = super().get_queryset()
        contract = self.request.GET.get('contract')

        if contract:
            qs = qs.filter(contract__id=contract)
        return qs.filter().order_by('id')


class NewContractViewSet(BaseViewSet):
    queryset = NewContract.objects.all()
    serializer_class = NewContractSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = LargeResultsSetPagination

    search_fields = (
        'id', 'noa_issuing_date', 'responsive_bidder', 'contract_signing_date', 'contract_amount', 'contractor_name',
        'tender_type', 'no_of_firm', 'tender__id', 'contract_id')
    ordering_fields = (
        '', 'id', 'noa_issuing_date', 'responsive_bidder', 'contract_signing_date', 'contract_amount', 'contract_id',
        'contractor_name', 'tender_type', 'no_of_firm', 'tender__id')

    def get_queryset(self):
        qs = super().get_queryset()
        qs = get_contract_filter(qs, self.request)
        return qs.order_by('-updated_at')


class ContractViewSet(BaseViewSet):
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = LargeResultsSetPagination

    search_fields = (
        'office__name', 'office__division__name', 'office__region__name', 'office__district__name',
        'office__upazila__name', 'status', 'tender_id__tender_id', 'physical_progress', 'amount_paid',
        'start_date', 'completion_date', 'revise_contract_amount', 'actual_completion_date')
    ordering_fields = (
        '', 'office__name', 'office__division__name', 'office__region__name', 'office__district__name',
        'office__upazila__name', 'tender_id__tender_id', 'physical_progress', 'amount_paid', 'start_date',
        'completion_date', 'revise_contract_amount', 'actual_completion_date', 'status')

    def perform_create(self, serializer):
        data = serializer.validated_data
        contract_status = 'Ongoing'
        if data['completion_date']:
            contract_status = "Completed"
        elif data['start_date']:
            contract_status = "Started"
        serializer.validated_data.update({'status': contract_status})
        serializer.save()

    def perform_update(self, serializer):
        data = serializer.validated_data
        contract_status = 'Ongoing'
        if data['completion_date']:
            contract_status = "Completed"
        elif data['start_date']:
            contract_status = "Started"
        serializer.validated_data.update({'status': contract_status})
        serializer.save()

    def get_queryset(self):
        qs = super().get_queryset()
        organization = self.request.GET.get('organization')
        office_category = self.request.GET.get('office_category')
        region = self.request.GET.get('region')
        district = self.request.GET.get('district')
        office = self.request.GET.get('office')
        updated_at_from = self.request.GET.get('updated_at_from')
        updated_at_to = self.request.GET.get('updated_at_to')
        tender = self.request.GET.get('tender')

        user_permissions = list(self.request.user.profile.role.permission.values_list('code', flat=True))
        if 'tender_admin' not in user_permissions:
            qs = qs.filter(office=self.request.user.profile.office.id)

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
        if tender:
            qs = qs.filter(tender_id__id=tender)
        return qs.filter().order_by('tender_id')


class ContractPaymentViewSet(BaseViewSet):
    queryset = ContractPayment.objects.all()
    serializer_class = ContractPaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = LargeResultsSetPagination

    search_fields = ('id', 'amount_paid', 'payment_date')

    def perform_create(self, serializer):
        serializer.save()
        payments = ContractPayment.objects.filter(contract=serializer.validated_data['contract'])
        amount_paid = 0
        for payment in payments:
            amount_paid += payment.amount_paid
        Contract.objects.filter(id=serializer.validated_data['contract'].id).update(amount_paid=amount_paid)

    def perform_update(self, serializer):
        serializer.save()
        payments = ContractPayment.objects.filter(contract=serializer.data['contract'])
        amount_paid = 0
        for payment in payments:
            amount_paid += payment.amount_paid
        Contract.objects.filter(id=serializer.data['contract']).update(amount_paid=amount_paid)

    def get_queryset(self):
        qs = super().get_queryset()
        contract = self.request.GET.get('contract')
        if contract:
            qs = qs.filter(contract=contract)

        return qs.filter().order_by('-updated_at')


class BudgetCommonViewSet(BaseViewSet):
    queryset = BudgetCommon.objects.all()
    serializer_class = BudgetCommonSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = LargeResultsSetPagination

    search_fields = (
        'fund_disburse_from', 'memo_no', 'financial_year', 'installment_no', 'issue_date', 'subject', 'total_provision'
        , 'released_budget')

    ordering_fields = (
        '', 'fund_disburse_from', 'memo_no', 'financial_year', 'installment_no', 'issue_date', 'subject',
        'total_provision', 'released_budget')

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter().order_by('-updated_at', '-issue_date')


class BudgetViewSet(BaseViewSet):
    queryset = Budget.objects.all()
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = LargeResultsSetPagination

    search_fields = (
        'office__name', 'office__division__name', 'office__region__name', 'office__district__name',
        'office__upazila__name', 'fund_disburse_from', 'memo_no', 'financial_year', 'installment_no', 'issue_date',
        'subject', 'total_provision', 'budget_amount', 'type', 'released_budget', 'comments'
    )
    ordering_fields = (
        '', 'office__name', 'office__division__name', 'office__region__name', 'office__district__name',
        'office__upazila__name', 'fund_disburse_from', 'memo_no', 'financial_year', 'installment_no', 'issue_date',
        'subject', 'total_provision', 'budget_amount', 'type', 'released_budget', 'comments'
    )

    def perform_create(self, serializer):
        # print(serializer.validated_data)
        office = serializer.validated_data.pop('office')
        budget_amount = serializer.validated_data.pop('budget_amount')
        comments = ''
        if serializer.validated_data.get('comments'):
            comments = serializer.validated_data.pop('comments')
        if 'budget_common' in serializer.validated_data:
            id = serializer.validated_data.pop('budget_common')['id']
            budget_common = BudgetCommon.objects.get(pk=id)

            Budget.objects.create(budget_amount=budget_amount, budget_common=budget_common, office=office,
                                  fund_disburse_from=budget_common.fund_disburse_from, memo_no=budget_common.memo_no,
                                  financial_year=budget_common.financial_year,
                                  installment_no=budget_common.installment_no,
                                  released_budget=budget_common.released_budget,
                                  subject=budget_common.subject, issue_date=budget_common.issue_date,
                                  total_provision=budget_common.total_provision, type='National', comments=comments)
        else:
            memo_no = serializer.validated_data.pop('memo_no')
            fund_disburse_from = serializer.validated_data.pop('fund_disburse_from')
            issue_date = serializer.validated_data.pop('issue_date')
            financial_year = serializer.validated_data.pop('financial_year')
            total_provision = serializer.validated_data.pop('total_provision') if serializer.validated_data.get(
                'total_provision') else 0
            installment_no = serializer.validated_data.pop('installment_no')
            subject = serializer.validated_data.pop('subject')
            released_budget = serializer.validated_data.pop('released_budget') if serializer.validated_data.get(
                'released_budget') else 0
            Budget.objects.create(budget_amount=budget_amount, office=office, fund_disburse_from=fund_disburse_from,
                                  memo_no=memo_no, financial_year=financial_year, installment_no=installment_no,
                                  subject=subject, issue_date=issue_date, total_provision=total_provision, type='Local',
                                  comments=comments, released_budget=released_budget)
        return Response({"status": "200", "error_message": ""})

    def perform_update(self, serializer):
        # print(serializer.validated_data)
        if 'budget_common' in serializer.validated_data and serializer.validated_data['budget_common']['id'] == '':
            serializer.validated_data.pop('budget_common')['id']
        # id = serializer.validated_data.pop('memo_no')
        # office = serializer.validated_data.pop('office')
        # budget_amount = serializer.validated_data.pop('budget_amount')

        # fund_disburse_from = serializer.validated_data.pop('fund_disburse_from')
        # issue_date = serializer.validated_data.pop('issue_date')
        # financial_year = serializer.validated_data.pop('financial_year')
        # total_provision = serializer.validated_data.pop('total_provision')
        # installment_no = serializer.validated_data.pop('installment_no')
        # subject = serializer.validated_data.pop('subject')

        budget = super().perform_update(serializer)
        return Response({"status": "200", "error_message": ""})

    def get_queryset(self):
        return get_budget_filter(self.request).order_by('-updated_at', 'office__office_category',
                                                        # 'fund_disburse_from',
                                                        'financial_year', 'installment_no')


class OfficeTypeViewSet(BaseViewSet):
    queryset = OfficeType.objects.all()
    serializer_class = OfficeTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter().order_by('type')


class ExternalMemberViewSet(BaseViewSet):
    queryset = ExternalMember.objects.all()
    serializer_class = ExternalMemberSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = LargeResultsSetPagination

    search_fields = (
        'organization__name', 'address', 'contact_no', 'org_email',
        'user__first_name', 'user__profile__office__name', 'user__profile__gender',
        'user__profile__nid', 'user__profile__date_of_birth', 'user__profile__designation__designation',
        'user__profile__mobile_no',
        'memo', 'office_order_date', 'comments', 'invitee_office__name', 'invitee_name', 'invitee_designation'
    )
    ordering_fields = (
        '', 'organization__name', 'address', '', 'user__profile__designation__designation', 'user__first_name',
        'user__profile__office__name', 'user__profile__gender', 'contact_no', 'office_order_date',
        'invitee_name', 'invitee_designation', 'invitee_office__name', ''
    )

    def get_queryset(self):
        qs = super().get_queryset()

        organization = self.request.GET.get('organization')
        office_category = self.request.GET.get('office_category')
        # region = self.request.GET.get('region')
        # district = self.request.GET.get('district')
        office = self.request.GET.get('office')
        updated_at_from = self.request.GET.get('updated_at_from')
        updated_at_to = self.request.GET.get('updated_at_to')
        contact_no = self.request.GET.get('contact_no_adv')
        office_order_date = self.request.GET.get('office_order_date_adv')
        email = self.request.GET.get('email_adv')
        invitee_office = self.request.GET.get('invitee_office_adv')
        invitee_name = self.request.GET.get('inv_name_adv')
        invitee_designation = self.request.GET.get('inv_designation_adv')
        com_type = self.request.GET.get('com_type_adv')
        memo_no = self.request.GET.get('memo_no_adv')
        nominee_name = self.request.GET.get('nominee_name_adv')
        nominee_designation = self.request.GET.get('nominee_designation_adv')
        nominee_office = self.request.GET.get('nominee_office_adv')
        org_name = self.request.GET.get('org_name_adv')

        if organization:
            qs = qs.filter(user__profile__office__organization=organization)
        if office_category:
            qs = qs.filter(user__profile__office__office_category=office_category)
        # if region:
        #     qs = qs.filter(user__profile__office__region__id=region)
        # if district:
        #     qs = qs.filter(user__profile__office__district__id=district)
        if office:
            qs = qs.filter(user__profile__office__id=office)
        if org_name:
            qs = qs.filter(organization__id=org_name)
        if updated_at_from:
            updated_from = datetime.datetime.strptime(updated_at_from, "%Y-%m-%d").date()
            qs = qs.filter(updated_at__gte=updated_from)
        if updated_at_to:
            updated_to = datetime.datetime.strptime(updated_at_to, "%Y-%m-%d").date()
            updated_to += datetime.timedelta(days=1)
            qs = qs.filter(updated_at__lte=updated_to)
        if contact_no:
            qs = qs.filter(user__profile__mobile_no__icontains=contact_no)
        if office_order_date:
            office_order_date = datetime.datetime.strptime(office_order_date, "%Y-%m-%d").date()
            qs = qs.filter(office_order_date=office_order_date)
        if email:
            qs = qs.filter(org_email__icontains=email)
        if invitee_office:
            qs = qs.filter(invitee_office=invitee_office)
        if invitee_designation:
            qs = qs.filter(invitee_designation__icontains=invitee_designation)
        if invitee_name:
            qs = qs.filter(invitee_name__icontains=invitee_name)
        if nominee_office:
            qs = qs.filter(user__profile__office=nominee_office)
        if nominee_designation:
            qs = qs.filter(user__profile__designation=nominee_designation)
        if nominee_name:
            qs = qs.filter(user__first_name__icontains=nominee_name)
        if com_type:
            com_type_list = com_type.split(",")
            qs = qs.filter(committee_type__in=com_type_list).distinct()
        if memo_no:
            qs = qs.filter(memo=memo_no)

        return qs.filter().order_by('-updated_at')


# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------ Audit Trail --------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class AuditTrailViewSet(BaseViewSet):
    queryset = AuditTrail.objects.all()
    serializer_class = AuditTrailSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = LargeResultsSetPagination

    search_fields = (
        'module_name', 'module_id', 'time', 'action', 'user__first_name', 'user__profile__office__name',
        'ip_address', 'detail', 'created_at', 'updated_at'
    )

    ordering_fields = (
        '', 'module_name', 'user__email', 'user__first_name', 'user__profile__office__name', 'ip_address', 'time',
        'action', ''
    )

    def get_queryset(self):
        qs = super().get_queryset()

        organization = self.request.GET.get('organization')
        office_category = self.request.GET.get('office_category')
        region = self.request.GET.get('region')
        district = self.request.GET.get('district')
        office = self.request.GET.get('office')
        module = self.request.GET.get('module')
        module_id = self.request.GET.get('module_id')
        updated_at_from = self.request.GET.get('updated_at_from')
        updated_at_to = self.request.GET.get('updated_at_to')

        if organization:
            qs = qs.filter(user__profile__office__organization=organization)
        if office_category:
            qs = qs.filter(user__profile__office__office_category=organization)
        if region:
            qs = qs.filter(user__profile__office__region=region)
        if district:
            qs = qs.filter(user__profile__office__district=district)
        if office:
            qs = qs.filter(user__profile__office=office)
        if module:
            qs = qs.filter(module_name=module)
        if module_id:
            qs = qs.filter(module_id=module_id)
        if updated_at_from:
            updated_from = datetime.datetime.strptime(updated_at_from, "%Y-%m-%d").date()
            qs = qs.filter(updated_at__gte=updated_from)
        if updated_at_to:
            updated_to = datetime.datetime.strptime(updated_at_to, "%Y-%m-%d").date()
            updated_to += datetime.timedelta(days=1)
            qs = qs.filter(updated_at__lte=updated_to)

        return qs.filter().order_by('-time')


# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------ Announcement --------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class IsOfficeAdminOrNone(permissions.BasePermission):
    """
    Custom permission to only allow office members to view it.
    """

    def has_object_permission(self, request, view, obj):
        user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
        if request.user.is_anonymous and obj.for_homepage == 1:
            return True
        if 'notice_admin' in user_permissions:
            return True
        if request.user.is_authenticated and obj.for_homepage == 1:
            return True
        return request.user.profile.office.id in list(obj.office.all().values_list('id', flat=True))


class AnnouncementViewSet(BaseViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOfficeAdminOrNone,)
    pagination_class = LargeResultsSetPagination
    search_fields = (
        'updated_at', 'id', 'expired_date', 'title', 'description', 'from_announcement__from_announcement')
    ordering_fields = (
        '', 'id', 'title', 'expired_date', 'updated_at', 'weight', 'from_announcement__from_announcement', '', '', '')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
        if self.request.data.get('attachment'):
            attachments = self.request.data.pop('attachment')
            attachments_name = self.request.data.pop('attachment_name')
            for attachment, name in zip(attachments, attachments_name):
                AnnouncementAttachment.objects.create(
                    announcement=serializer.instance, attachment=attachment, attachment_name=name)

    def perform_update(self, serializer):
        serializer.save(created_by=self.request.user)
        if self.request.data.get('attachment'):
            attachments = self.request.data.pop('attachment')
            attachments_name = self.request.data.pop('attachment_name')
            for attachment, name in zip(attachments, attachments_name):
                AnnouncementAttachment.objects.create(
                    announcement=serializer.instance, attachment=attachment, attachment_name=name)

    def perform_destroy(self, instance):
        instance.draft = 2
        instance.save()

    def get_queryset(self):
        qs = super().get_queryset()
        organization = self.request.GET.get('organization')
        office_category = self.request.GET.get('office_category')
        region = self.request.GET.get('region')
        expired = self.request.GET.get('expired')
        pending = self.request.GET.get('pending')
        attachments = self.request.GET.get('attachments')
        length = self.request.GET.get('limit')

        organization_list = self.request.GET.get('organization_list')
        office_category_list = self.request.GET.get('office_category_list')
        region_list = self.request.GET.get('region_list')
        district_list = self.request.GET.get('district_list')
        office_list = self.request.GET.get('office_list')
        draft = self.request.GET.get('draft')
        updated_at_from = self.request.GET.get('updated_at_from')
        updated_at_to = self.request.GET.get('updated_at_to')
        homepage = self.request.GET.get('homepage')
        current_datetime = datetime.datetime.today() + datetime.timedelta(hours=6)

        if self.request.user.is_anonymous and pending:
            qs_copy = qs
            qs = qs.filter(expired_date__gt=current_datetime).distinct()
            qs = qs | qs_copy.filter(expired_date__isnull=True).distinct()
            qs = qs.filter(for_homepage=1)
            if length:
                length = int(length)
                return qs.filter(draft=1).order_by(F('weight').desc(nulls_last=True))[: length]
            else:
                return qs.filter(draft=1).order_by(F('weight').desc(nulls_last=True))

        elif self.request.user.is_anonymous and expired:
            qs = qs.filter(expired_date__lt=current_datetime).distinct()
            qs = qs.filter(for_homepage=1)
            return qs.filter(draft=1).order_by(F('weight').desc(nulls_last=True))

        user_permissions = list(self.request.user.profile.role.permission.values_list('code', flat=True))
        if 'notice_admin' not in user_permissions:
            qs_copy2 = qs
            qs_copy2 = qs_copy2.filter(for_homepage=1)
            qs = qs.filter(office=self.request.user.profile.office.id)
            qs = qs | qs_copy2

        if organization:
            qs = qs.filter(office__organization=organization)
        if office_category:
            qs = qs.filter(office__office_category=office_category)
        if region:
            qs = qs.filter(office__region=region)

        if expired:
            qs = qs.filter(expired_date__lt=current_datetime)
        if pending:
            qs_copy = qs
            qs = qs.filter(expired_date__gt=current_datetime)
            qs = qs | qs_copy.filter(expired_date__isnull=True)

        if attachments:
            attachments = int(attachments)
        if attachments:
            qs = qs.filter(attachment__isnull=False).exclude(attachment='')
        if draft:
            draft = int(draft)
        if draft == 0:
            qs = qs.filter(draft=0)
        if draft == 1:
            qs = qs.filter(draft=1)
        if draft == 2:
            return Announcement.objects.filter(draft=2).order_by(F('weight').desc(nulls_last=True)).distinct()
        if homepage:
            qs = qs.filter(for_homepage=homepage)

        filters = {}
        if organization_list:
            filters['office__organization__in'] = organization_list.split(",")
            qs = qs.filter(**filters)
        if office_category_list:
            filters['office__office_category__in'] = office_category_list.split(",")
            qs = qs.filter(**filters)
        if region_list:
            filters['office__region__in'] = region_list.split(",")
            qs = qs.filter(**filters)
        if district_list:
            filters['office__district__in'] = district_list.split(",")
            qs = qs.filter(**filters)
        if office_list:
            filters['office__in'] = office_list.split(",")
            qs = qs.filter(**filters).order_by('id').distinct()
        # if updated_at_from:
        #     # updated_from = datetime.datetime.strptime(updated_at_from, "%Y-%m-%d").date()
        #     qs = qs.filter(updated_at__gte=updated_from)
        # if updated_at_to:
        #     # updated_to = datetime.datetime.strptime(updated_at_to, "%Y-%m-%d").date()
        #     updated_to = updated_at_to + datetime.timedelta(days=1)
        #     qs = qs.filter(updated_at__lte=updated_to)

        if length:
            length = int(length)
            return qs.filter(draft__in=[0, 1]).order_by(F('weight').desc(nulls_last=True), '-updated_at').distinct()[
                   : length]
        return qs.filter(draft__in=[0, 1]).order_by(F('weight').desc(nulls_last=True), '-updated_at').distinct()


class AnnouncementStatusViewSet(BaseViewSet):
    queryset = AnnouncementStatus.objects.all()
    serializer_class = AnnouncementStatusSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = LargeResultsSetPagination

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data.update({'password': make_password('lged1234')})
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter().order_by('id')


class AnnouncementAttachmentViewSet(BaseViewSet):
    queryset = AnnouncementAttachment.objects.all()
    serializer_class = AnnouncementAttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        qs = super().get_queryset()
        notice = self.request.GET.get('announcement_id')
        if notice:
            qs = qs.filter(announcement__id=notice)
        return qs.filter().order_by('id')


# ----------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------- Issue Category ----------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------


class IssueTitleViewSet(BaseViewSet):
    queryset = IssueTitle.objects.all()
    serializer_class = IssueTitleSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]

    search_fields = (
        'title', 'category'
    )
    ordering_fields = (
        '', 'title', 'category'
    )

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.GET.get('category'):
            qs = qs.filter(category=self.request.GET.get('category'))

        return qs.filter().order_by('id')


# ----------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------- Issue -------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class IssueViewSet(BaseViewSet):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    # filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)

    search_fields = (
        'id', 'title__title', 'description', 'raised_by__first_name', 'raised_by__last_name',
        'raised_by__profile__office__name', 'created_at',
    )
    ordering_fields = (
        '', 'id', 'title', 'description', 'raised_by__first_name', 'raised_by__last_name',
        'raised_by__profile__office__name', 'created_at',
    )

    # def create(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)
    #     headers = self.get_success_headers(serializer.data)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    # def perform_create(self, serializer):
    #     serializer.save()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        # change status if (action or comment or attachment is changed)
        user_permissions = list(request.user.profile.role.permission.values_list('code', flat=True))
        if 'issue_update' in user_permissions and 'issue_admin' in user_permissions:
            if request.data.get('issue_comment') or request.data.get('admin_end_action') != str(
                    instance.admin_end_action) or \
                    request.data.get('attachment'):
                instance.seen_status = False
                instance.seen_time = None
                instance.save()
        elif 'issue_update' in user_permissions and 'issue_admin' not in user_permissions:
            if request.data.get('issue_comment') or request.data.get('user_end_action') != str(
                    instance.user_end_action) or \
                    request.data.get('attachment'):
                instance.seen_status = False
                instance.seen_time = None
                instance.save()
        if request.data.get('issue_comment'):
            IssueComment(comment=request.data.get('issue_comment'), commented_by=self.request.user,
                         issue=instance).save()
        if request.data.get('attachment'):
            attachment = IssueAttachment(attachment=request.data.get('attachment'), created_by=self.request.user,
                                         issue=instance)
            if request.data.get('attachment_type'):
                attachment.attachment_type = request.data.get('attachment_type')
            attachment.save()
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def get_queryset(self):
        user_permissions = list(self.request.user.profile.role.permission.values_list('code', flat=True))
        if 'issue_admin' in user_permissions:
            self.ordering_fields = self.ordering_fields + ('user_end_action',)
        else:
            self.ordering_fields = self.ordering_fields + ('admin_end_action',)

        # qs = super().get_queryset()
        #
        # updated_at_from = self.request.GET.get('updated_at_from')
        # updated_at_to = self.request.GET.get('updated_at_to')
        #
        # if self.request.GET.get('status') and self.request.GET.get('status') == 'pending':
        #     if self.request.user.profile.office.office_category == "LGED HQ":
        #         qs = qs.exclude(user_end_action=2)
        #     else:
        #         qs = qs.exclude(user_end_action=2)
        # if self.request.GET.get('status') and self.request.GET.get('status') == 'solved':
        #     qs = qs.filter(user_end_action=2)
        # if self.request.GET.get('item_id') and self.request.GET.get('category'):
        #     qs = qs.filter(item_id=self.request.GET.get('item_id'))
        #     qs_copy = qs
        #     qs = qs.filter(title__category=self.request.GET.get('category'))
        #     qs_copy = qs_copy.filter(other_category=self.request.GET.get('category'))
        #     qs = qs | qs_copy
        # # if self.request.GET.get('search_action'):
        # #     qs = qs.filter(user_end_action=self.request.GET.get('search_action'))
        # if self.request.GET.get('search_category'):
        #     qs_copy = qs
        #     qs = qs.filter(title__category=self.request.GET.get('search_category'))
        #     qs_copy = qs_copy.filter(other_category=self.request.GET.get('search_category'))
        #     qs = qs | qs_copy
        # if self.request.user.profile.office.office_category != "LGED HQ":
        #     qs = qs.filter(raised_by=self.request.user)
        #
        # if updated_at_from:
        #     updated_from = datetime.datetime.strptime(updated_at_from, "%Y-%m-%d").date()
        #     qs = qs.filter(updated_at__gte=updated_from)
        # if updated_at_to:
        #     updated_to = datetime.datetime.strptime(updated_at_to, "%Y-%m-%d").date()
        #     updated_to += datetime.timedelta(days=1)
        #     qs = qs.filter(updated_at__lte=updated_to)
        # return qs.filter().order_by('-created_at')
        return get_issue_filter(self.request)


# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------ Training Helper ----------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class TrainingNameViewSet(BaseViewSet):
    queryset = TrainingName.objects.all()
    serializer_class = TrainingNameSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]

    search_fields = (
        'training_name',
    )
    ordering_fields = (
        '', 'training_name'
    )


class TrainingCategoryViewSet(BaseViewSet):
    queryset = TrainingCategory.objects.all()
    serializer_class = TrainingCategorySerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]

    search_fields = (
        'category',
    )
    ordering_fields = (
        '', 'category'
    )


class BatchNumberViewSet(BaseViewSet):
    queryset = BatchNumber.objects.all()
    serializer_class = BatchNumberSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]

    search_fields = (
        'batch_no',
    )
    ordering_fields = (
        '', 'batch_no'
    )


class FromAnnouncementViewSet(BaseViewSet):
    queryset = FromAnnouncement.objects.all()
    serializer_class = FromAnnouncementSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    search_fields = (
        'from_announcement',
    )
    ordering_fields = (
        '', 'from_announcement'
    )


class TrainingUserViewSet(BaseViewSet):
    queryset = TrainingUser.objects.all()
    serializer_class = TrainingUserSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        training_id = self.request.GET.get('training_id')
        user_id = self.request.GET.get('user_id')

        user_permissions = list(self.request.user.profile.role.permission.values_list('code', flat=True))
        if 'training_admin' not in user_permissions:
            qs = qs.filter(user__profile__office=self.request.user.profile.office)
        if training_id:
            qs = qs.filter(training=TrainingBatch.objects.get(id=training_id))
        if user_id:
            qs = qs.filter(user__id=user_id)
        return qs.filter().order_by('id')


class HomePageImageViewSet(BaseViewSet):
    queryset = HomePageImage.objects.all()
    serializer_class = HomePageImageSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]


class ResponsiveBidderViewSet(BaseViewSet):
    queryset = ResponsiveBidder.objects.all()
    serializer_class = ResponsiveBidderSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]


class PublicationTypeViewSet(BaseViewSet):
    queryset = PublicationType.objects.all()
    serializer_class = PublicationTypeSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]


class PaymentViewSet(BaseViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]

    search_fields = (
        'id', 'contract__id', 'commencement_date', 'start_date', 'completion_date', 'contract__contract_amount',
    )
    ordering_fields = (
        'id', 'contract__id', 'commencement_date', 'start_date', 'completion_date', 'contract__contract_amount',
    )

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.order_by('updated_at')


class MonthlyProgressViewSet(BaseViewSet):
    queryset = MonthlyProgress.objects.all()
    serializer_class = MonthlyProgressSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        payment = self.request.GET.get('payment')

        if payment:
            qs = qs.filter(payment__id=payment)

        return qs


class PaymentAmountVariationViewSet(BaseViewSet):
    queryset = PaymentAmountVariation.objects.all()
    serializer_class = PaymentAmountVariationSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        payment = self.request.GET.get('payment')

        if payment:
            qs = qs.filter(payment__id=payment)

        return qs


class PaymentTimeVariationViewSet(BaseViewSet):
    queryset = PaymentTimeVariation.objects.all()
    serializer_class = PaymentTimeVariationSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        payment = self.request.GET.get('payment')

        if payment:
            qs = qs.filter(payment__id=payment)

        return qs


class ExtOrgViewSet(BaseViewSet):
    queryset = ExtOrg.objects.all()
    serializer_class = ExtOrgSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_fields = ('name',)

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.order_by('name')


class InviteeOfficeViewSet(BaseViewSet):
    queryset = InviteeOffice.objects.all()
    serializer_class = InviteeOfficeSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_fields = ('name',)

    def get_queryset(self):
        qs = super().get_queryset()
        ext_org = self.request.query_params.get('ext_org')
        if ext_org:
            qs = qs.filter(external_organization=ext_org)
        return qs.order_by('name')


class ColumnCustomizationViewSet(BaseViewSet):
    queryset = ColumnCustomization.objects.all()
    serializer_class = ColumnCustomizationSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]

    # filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    # filter_fields = ('report_for', 'columns')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.order_by('report_for')


class PasswordRequestViewSet(BaseViewSet):
    queryset = PasswordRequest.objects.all()
    serializer_class = PasswordRequestSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]

    search_fields = ('id', 'comment', 'user_comment', 'user__first_name', 'e_gp_id', 'new_password',
                     'user__profile__designation__designation')

    def create(self, request, *args, **kwargs):
        user_id = request.data['user']
        e_gp_id = request.data['e_gp_id']

        mutable = request.POST._mutable
        request.POST._mutable = True
        request.POST['type'] = 'Main Domain'
        try:
            user_data = User.objects.get(
                Q(profile__e_gp_user_id__icontains=e_gp_id) | Q(profile__e_gp_user_id_lgis__icontains=e_gp_id) | Q(
                    profile__e_gp_user_id_for_govt__icontains=e_gp_id) |
                Q(profile__e_gp_user_id_lgis_for_govt__icontains=e_gp_id) |
                Q(profile__e_gp_user_id_for_org_admin__icontains=e_gp_id) |
                Q(profile__e_gp_user_id_lgis_for_org_admin__icontains=e_gp_id) |
                Q(profile__e_gp_user_id_for_pe_admin__icontains=e_gp_id) |
                Q(profile__e_gp_user_id_lgis_for_pe_admin__icontains=e_gp_id))
            if not user_data.profile.nid or not user_data.get_full_name() or not user_data.profile.personal_email or not user_data.profile.mobile_no:
                raise ValidationError('Please, Fill up NID, name, personal Email ,mobile number for the ID.')
            user_id = user_data.id
        except User.MultipleObjectsReturned:
            raise ValidationError('Multiuple time found same user id')

        except User.DoesNotExist:
            request.POST['type'] = 'Other Domain'

        request.POST['user'] = user_id
        request.POST._mutable = mutable

        serializer = self.get_serializer(data=request.data)

        temp = PasswordRequest.objects.filter(e_gp_id=request.data['e_gp_id']).order_by('-updated_at')

        if temp.count() != 0 and temp.first().status == 'Pending':
            raise ValidationError(
                "You can't request for password until your last request gets solved.")
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_update(self, serializer):
        # if self.request.data.get('value'):
        #     if self.request.data.get('name') == 'new_password':
        #         PasswordRequest.objects.filter(pk=self.request.data['pk']).update(new_password=self.request.data['value'])
        #     if self.request.data.get('name') == 'comment':
        #         PasswordRequest.objects.filter(pk=self.request.data['pk']).update(comment=self.request.data['value'])
        #     PasswordRequest.objects.filter(pk=self.request.data['pk']).update(status='Solved')
        serializer.save()

    def get_queryset(self) -> QuerySet:
        qs = super().get_queryset()
        organization = self.request.GET.get('organization')
        office_category = self.request.GET.get('office_category')
        division = self.request.GET.get('division')
        region = self.request.GET.get('region')
        district = self.request.GET.get('district')
        upazilla = self.request.GET.get('upazilla')
        p_class = self.request.GET.get('class')
        user = self.request.GET.get('user')
        e_gp_id = self.request.GET.get('e_gp_id')
        office = self.request.GET.get('office')
        status = self.request.GET.get('status')
        domain_type = self.request.GET.get('type')
        number_of_requests = self.request.GET.get('number_of_requests')
        number_of_requests_gt = self.request.GET.get('number_of_requests_gt')
        number_of_requests_lt = self.request.GET.get('number_of_requests_lt')
        number_of_requests_gte = self.request.GET.get('number_of_requests_gte')
        number_of_requests_lte = self.request.GET.get('number_of_requests_lte')
        designation = self.request.GET.get('designation')
        updated_at_from = self.request.GET.get('updated_from')
        updated_at_to = self.request.GET.get('updated_to')
        day = self.request.GET.get('day')

        if organization:
            qs = qs.filter(user__profile__office__organization=organization)
        if office_category:
            qs = qs.filter(user__profile__office__office_category=office_category)
        if division:
            qs = qs.filter(user__profile__office__division=division)
        if region:
            qs = qs.filter(user__profile__office__region=region)
        if district:
            qs = qs.filter(user__profile__office__district=district)
        if upazilla:
            qs = qs.filter(user__profile__office__upazila=upazilla)
        if p_class:
            qs = qs.filter(user__profile__office__pourashava_class=p_class)
        if user:
            qs = qs.filter(user=user)
        if office:
            qs = qs.filter(user__profile__office=office)
        if designation:
            qs = qs.filter(user__profile__designation=designation)
        if e_gp_id:
            qs = qs.filter(e_gp_id__icontains=e_gp_id)
        if number_of_requests:
            ids = []
            for q in qs:
                if int(number_of_requests) == qs.filter(e_gp_id=q.e_gp_id).count():
                    ids.append(q.id)
            qs = qs.filter(id__in=ids)
        if number_of_requests_gt:
            ids = []
            for q in qs:
                if int(number_of_requests_gt) > qs.filter(e_gp_id=q.e_gp_id).count():
                    ids.append(q.id)
            qs = qs.filter(id__in=ids)
        if number_of_requests_gte:
            ids = []
            for q in qs:
                if int(number_of_requests_gte) >= qs.filter(e_gp_id=q.e_gp_id).count():
                    ids.append(q.id)
            qs = qs.filter(id__in=ids)
        if number_of_requests_lt:
            ids = []
            for q in qs:
                if int(number_of_requests_lt) < qs.filter(e_gp_id=q.e_gp_id).count():
                    ids.append(q.id)
            qs = qs.filter(id__in=ids)
        if number_of_requests_lte:
            ids = []
            for q in qs:
                if int(number_of_requests_lte) <= qs.filter(e_gp_id=q.e_gp_id).count():
                    ids.append(q.id)
            qs = qs.filter(id__in=ids)
        if status and domain_type and domain_type != 'All Domain':
            qs = qs.filter(status=status, type=domain_type).order_by('updated_at')
        if status and domain_type and domain_type == 'All Domain':
            qs = qs.filter(status=status).order_by('updated_at')

        if not status and domain_type and domain_type != 'All Domain':
            qs = qs.filter(type=domain_type).order_by('updated_at')
        if not status and domain_type and domain_type == 'All Domain':
            qs = qs.filter().order_by('updated_at')

        if updated_at_from:
            updated_from = datetime.datetime.strptime(updated_at_from, "%Y-%m-%d").date()
            qs = qs.filter(updated_at__gte=updated_from)
        if updated_at_to:
            updated_to = datetime.datetime.strptime(updated_at_to, "%Y-%m-%d").date()
            updated_to += datetime.timedelta(days=1)
            qs = qs.filter(updated_at__lte=updated_to)

        if day == 'today':
            qs = qs.filter(Q(created_at__gte=datetime.date.today()))

        return qs.order_by('-updated_at')


class RoleViewSet(BaseViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]


class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.order_by('id')


class ExtMemberInclusionHistoryViewSet(viewsets.ModelViewSet):
    queryset = ExtMemberInclusionHistory.objects.all()
    serializer_class = ExtMemberInclusionHistorySerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.AllowAny]

    # ordering_fields = ('created_at')

    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            serializer = self.get_serializer(data=request.data)
            print('serializer ========= ', serializer)
            serializer.is_valid(raise_exception=True)
            proc_roll = serializer.validated_data.get('procurement_roles')
            print('proc_roll ========== ', proc_roll)
            proc_roll2 = self.request.data.get('procurement_roles')
            print('proc_roll2 ========= ', proc_roll2)

            self.perform_create(serializer)
            inclusion_object = serializer.instance
            # if self.request.data.get('admin_users'):
            #     admin_users = json.loads(self.request.data['admin_users'])
            #     for i in range(0, len(admin_users.keys())):
            #         key = 'admin_user' + str(i + 1)
            #         user_data = admin_users[key]
            #         designation = Designation.objects.get(id=user_data['designation'])
            #         adm_user = AdminUsers.objects.create(ext_member_history=inclusion_object, designation=designation)
            #         for role in user_data['procurement_roles']:
            #             role_obj = ProcurementRole.objects.get(id=role)
            #             adm_user.procurement_roles.add(role_obj)
            if self.request.data.get('govt_users'):
                govt_users = json.loads(self.request.data['govt_users'])
                for i in range(0, len(govt_users.keys())):
                    key = 'govt_user' + str(i + 1)
                    user_data = govt_users[key]
                    designation = Designation.objects.get(id=user_data['designation'])
                    govt_user = GovtUsers.objects.create(ext_member_history=inclusion_object, designation=designation)
                    for role in user_data['procurement_roles']:
                        role_obj = ProcurementRole.objects.get(id=role)
                        govt_user.procurement_roles.add(role_obj)
            url = request.data.get('url')
            ExpiredLink.objects.filter(link=url).update(expired=True)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_update(self, serializer):
        with transaction.atomic():
            procurement_roles2 = serializer.validated_data.get('procurement_roles')
            if procurement_roles2 is None:
                procurement_roles3 = serializer.validated_data.update({'procurement_roles': []})

            module_object = ExtMemberInclusionHistory.objects.get(pk=serializer.instance.id)
            extid = serializer.instance.id

            extm = super().perform_update(serializer)

            inclusion_object = serializer.instance

            # govt_users = json.loads(self.request.data.get('govt_users'))

            govt_us = GovtUsers.objects.filter(ext_member_history=extid)
            govt_us.delete()
            if self.request.data.get('govt_users'):
                govt_users = json.loads(self.request.data['govt_users'])
                for i in range(0, len(govt_users.keys())):
                    key = 'govt_user' + str(i + 1)
                    user_data = govt_users[key]
                    designation = Designation.objects.get(id=user_data['designation'])
                    govt_user = GovtUsers.objects.create(ext_member_history=inclusion_object, designation=designation)
                    for role in user_data['procurement_roles']:
                        role_obj = ProcurementRole.objects.get(id=role)
                        govt_user.procurement_roles.add(role_obj)

        return Response({"status": "200", "error_message": ""})

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.order_by('-created_at')


class ExtMemberTransferHistoryViewSet(viewsets.ModelViewSet):
    queryset = ExtMemberTransferHistory.objects.all()
    serializer_class = ExtMemberTransferHistorySerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            self.perform_create(serializer)
            inclusion_object = serializer.instance
            url = request.data.get('url')
            ExpiredLink.objects.filter(link=url).update(expired=True)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ExtMemberUsertransfer(viewsets.ModelViewSet):
    queryset = ExtMemberTransferHistory.objects.all()
    serializer_class = ExtMemberTransferHistorySerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.AllowAny]

    def perform_create(self, request, *args, **kwargs):
        with transaction.atomic():
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            user = self.request.data['user']
            # user_name = self.request.data['user_name']
            new_designation = self.request.data['new_designation']
            new_designation_name = self.request.data['new_designation_name']
            transferred_office = self.request.data['transferred_office']
            transferred_office_name = self.request.data['transferred_office_name']
            nid = self.request.data['nid']
            transfertableid = self.request.data['transferred_db_table']

            print('table id ====== ', transfertableid)

            userdata = User.objects.filter(id=user, profile__nid=nid).values('first_name', 'profile',
                                                                             'profile__mobile_no',
                                                                             'profile__PPR_training', 'profile__nid',
                                                                             'profile__personal_email',
                                                                             'profile__gender',
                                                                             'profile__date_of_birth',
                                                                             'profile__training_under_id')
            userdata = list(userdata)
            if userdata == []:
                raise ValidationError("This user is already transfered or this user is not exits !")
            else:
                newOfficeUserData = User.objects.filter(profile__designation=new_designation,
                                                        profile__office=transferred_office, profile__nid=None).values(
                    'id', 'profile')
                newOfficeUserData = list(newOfficeUserData)
                print('new user ID ====== ', newOfficeUserData)
                if newOfficeUserData == []:
                    print('Nooooonnnnnnnnnnneeeeeeeeeee !')
                    raise ValidationError(
                        "This position of the transferred office is not blank ! Already one employee is settled for this position.")


                else:
                    usrdt = userdata[0]
                    print('userdata ====== ', usrdt)
                    User.objects.filter(id=user, profile__nid=nid).update(first_name=None)
                    Profile.objects.filter(id=usrdt['profile']).update(mobile_no='', PPR_training=None, nid=None,
                                                                       personal_email=None, gender=None,
                                                                       date_of_birth=None, training_under_id=None)

                    # Profile.objects.filter(id=usrdt['profile']).update(mobile_no='01222222222', nid=7777666656565,
                    #                                                    personal_email='cdf@gmail.com')
                    print('again userdata ====== ', usrdt)

                    User.objects.filter(id=newOfficeUserData[0]['id']).update(first_name=usrdt['first_name'])
                    Profile.objects.filter(id=newOfficeUserData[0]['profile']).update(
                        mobile_no=usrdt['profile__mobile_no'], PPR_training=usrdt['profile__PPR_training'],
                        nid=usrdt['profile__nid'],
                        personal_email=usrdt['profile__personal_email'], gender=usrdt['profile__gender'],
                        date_of_birth=usrdt['profile__date_of_birth'],
                        training_under_id=usrdt['profile__training_under_id'])

                    ExtMemberTransferHistory.objects.filter(id=transfertableid).update(approved_status=1,
                                                                                       user=newOfficeUserData[0]['id'])

            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            # return Response(status=status.HTTP_201_CREATED)


class ExpiredLinkViewSet(viewsets.ModelViewSet):
    queryset = ExpiredLink.objects.all()
    serializer_class = ExpiredLinkSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        default_token_generator = CustomPasswordResetTokenGenerator()
        token = default_token_generator.make_token()
        if self.request.data.get('id'):
            print("id ==== id === id")
            link = '&token=' + token
        elif self.request.data.get('office_name'):
            print('sdfgzxcv ==== zxcvbn')
            link = '&token=' + token
        else:
            link = '?token=' + token
        if ExpiredLink.objects.filter(link=link).count() != 0:
            raise ValidationError("This link already exists. Please try again.")
        serializer.save()
        serializer.instance.link += link
        serializer.instance.save()
