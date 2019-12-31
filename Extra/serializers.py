import json
import os

from django.db.models import Q, Max
from rest_framework import serializers
from rest_framework.utils import model_meta
from django.db import transaction
from datetime import date

from lged.models import ProcurementRole, Designation, Division, Region, District, Upazila, Office, Project, Tender, \
    Inventory, ResourceCenter, TrainingBatch, Publication, Gallery, CityCorporation, TransferHistory, \
    InventoryFile, InventoryStatus, InventoryType, ExternalMember, IssueTitle, Lot, ContractPayment, Firm, Issue, \
    IssueComment, BatchNumber, IssueAttachment, TrainingName, TrainingUser, InventoryTypeCategory, AuditTrail, \
    TenderCost, NewContract, HomePageImage, ResponsiveBidder, Payment, MonthlyProgress, ExtOrg, \
    PaymentAmountVariation, PaymentTimeVariation, TrainingCategory, InventoryProducts, Profile, FromAnnouncement, \
    PublicationType, CommitteeType, FundDisburseFrom, PasswordRequest, HomepageWriting, ImportantLinks, InviteeOffice, \
    ExtMemberTransferHistory, ExtMemberInclusionHistory, AdminUsers, GovtUsers, ExpiredLink, TemporaryOffice, \
    MultipleAssignHistory
from lged.models import User, PackageNo, Devices, Source, Supplier, SupportCenter, InventoryFileType, BudgetType, \
    ProcurementNature, TypeOfEmergency, ProcMethod, ProcType, SourceOfFund, ApprovingAuthority, ContractStatus, APP, \
    Package, Contract, BudgetCommon, Budget, OfficeType, Announcement, AnnouncementStatus, AnnouncementAttachment, \
    FundedBy, ColumnCustomization, Role, Permission


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        fields = self.context['request'].query_params.get('fields')
        if fields:
            fields = fields.split(',')
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class ProcurementRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcurementRole
        fields = '__all__'


class TrainingUserSerializer(serializers.ModelSerializer):
    office = serializers.CharField(source='user.profile.office.name', allow_blank=True, allow_null=True, required=False,
                                   read_only=True)
    office_id = serializers.CharField(source='user.profile.office.id', allow_blank=True, allow_null=True, required=False
                                      , read_only=True)
    designation_id = serializers.CharField(source='user.profile.designation.id', allow_blank=True, allow_null=True,
                                           required=False, read_only=True)
    district_id = serializers.CharField(source='user.profile.office.district.id', allow_blank=True, allow_null=True,
                                        required=False, read_only=True)
    first_name = serializers.CharField(source='user.first_name', allow_blank=True, allow_null=True, required=False,
                                       read_only=True)
    email = serializers.CharField(source='user.profile.official_email', allow_blank=True, allow_null=True,
                                  required=False, read_only=True)
    designation = serializers.CharField(source='user.profile.designation.designation', allow_blank=True,
                                        allow_null=True, required=False, read_only=True)
    district = serializers.CharField(source='user.profile.office.district', allow_blank=True, allow_null=True,
                                     required=False, read_only=True)
    personal_mobile_no = serializers.CharField(source='user.profile.mobile_no', allow_blank=True, allow_null=True,
                                               required=False,
                                               read_only=True)
    official_mobile_no = serializers.CharField(source='user.profile.official_mobile_no', allow_blank=True,
                                               allow_null=True,
                                               required=False, read_only=True)
    gender = serializers.CharField(source='user.profile.gender', allow_null=True, allow_blank=True, required=False,
                                   read_only=True)
    end_date = serializers.CharField(source='training.end_date', allow_null=True, allow_blank=True, required=False,
                                     read_only=True)
    training_status = serializers.SerializerMethodField('get_trainging_status')
    training_name = serializers.CharField(source='training.training_name', allow_null=True, allow_blank=True,
                                          required=False,
                                          read_only=True)

    class Meta:
        model = TrainingUser
        fields = '__all__'

    @classmethod
    def get_trainging_status(cls, instancce):
        if instancce.evaluation_marks and instancce.evaluation_marks > 33 or instancce.certificate:
            return 'pass'
        if instancce.comment:
            return instancce.comment
        return 'No Attendant'


class TemporaryOfficeSerializer(serializers.ModelSerializer):
    office_name = serializers.CharField(source='office.name', allow_blank=True, allow_null=True, required=False)
    first_name = serializers.CharField(source='user.first_name', allow_blank=True, allow_null=True, required=False)
    designation_name = serializers.CharField(source='designation.designation', allow_blank=True, allow_null=True,
                                             required=False)
    personal_mobile_no = serializers.CharField(source='user.profile.mobile_no', allow_blank=True, allow_null=True,
                                               required=False)
    personal_email = serializers.CharField(source='user.profile.personal_email', allow_blank=True, allow_null=True,
                                           required=False)
    profile_avatar = serializers.ImageField(source='user.profile.avatar', allow_null=True, allow_empty_file=True,
                                            required=False)
    division = serializers.CharField(source='office.division', allow_blank=True, allow_null=True,
                                     required=False)
    region = serializers.CharField(source='office.region', allow_blank=True, allow_null=True, required=False)
    district = serializers.CharField(source='office.district', allow_blank=True, allow_null=True,
                                     required=False)
    upazila = serializers.CharField(source='office.upazila', allow_blank=True, allow_null=True, required=False)
    bengali_name = serializers.CharField(source='user.profile.bengali_name', allow_null=True, allow_blank=True,
                                         required=False)
    official_email = serializers.CharField(allow_blank=True, allow_null=True,
                                           required=False)
    official_mobile_no = serializers.CharField(allow_blank=True,
                                               allow_null=True, required=False)
    nid_value = serializers.CharField(source='user.profile.nid', allow_blank=True, allow_null=True,
                                      required=False)
    gender = serializers.CharField(source='user.profile.gender', allow_blank=True, allow_null=True, required=False)
    date_of_birth = serializers.CharField(source='user.profile.date_of_birth', allow_blank=True, allow_null=True,
                                          required=False)
    PPR_training = serializers.CharField(source='user.profile.get_PPR_training_display', allow_blank=True,
                                         allow_null=True,
                                         required=False)

    # procurement_roles = serializers.StringRelatedField(many=True)
    # procurement_roles_lgis = serializers.StringRelatedField(many=True)

    procurement_role = serializers.CharField(max_length=300, allow_null=True, allow_blank=True, required=False)
    procurement_role_lgis = serializers.CharField(max_length=300, allow_null=True, allow_blank=True, required=False)
    procurement_role_list = ProcurementRoleSerializer(source='procurement_roles', read_only=True,
                                                      many=True)
    procurement_role_list_lgis = ProcurementRoleSerializer(source='procurement_roles_lgis', read_only=True,
                                                           many=True)

    training_start_date = serializers.SerializerMethodField('get_temp_training_start_date')
    training_venue = serializers.SerializerMethodField('get_temp_training_venue')
    user_id = serializers.CharField(allow_null=True, allow_blank=True)

    e_gp_user_id_for_govt = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    e_gp_user_id_lgis_for_govt = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    e_gp_user_id_for_org_admin = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    e_gp_user_id_lgis_for_org_admin = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    e_gp_user_id_for_pe_admin = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    e_gp_user_id_lgis_for_pe_admin = serializers.CharField(allow_null=True, allow_blank=True, required=False)

    @classmethod
    def get_temp_training_start_date(cls, obj):
        tb = TrainingUser.objects.filter(user=obj.user, training__created_by_status=2)
        #  print(tb)
        if tb:
            return tb[0].training.start_date
        else:
            return None

    @classmethod
    def get_temp_training_venue(cls, obj):
        tb = TrainingUser.objects.filter(user=obj.user, training__created_by_status=2)
        if tb and tb[0].training.venue:
            return tb[0].training.venue.id
        else:
            return None

    class Meta:
        model = TemporaryOffice
        fields = '__all__'


class TrainingBatchSerializer(serializers.ModelSerializer):
    # userList = serializers.CharField(source='users.email', allow_null=True, allow_blank=True, required=False, read_only=True)
    # users = serializers.CharField(required=False)
    venue_name = serializers.CharField(source='venue.name', allow_blank=True, allow_null=True, required=False,
                                       read_only=True)
    # batch_number = serializers.CharField(source='batch_no.batch_no', allow_blank=True, allow_null=True,
    # required=False,read_only=True)
    project_name = serializers.CharField(source='project.funded_by', allow_blank=True, allow_null=True, required=False,
                                         read_only=True)
    training = serializers.CharField(source='training_name.training_name', allow_blank=True, allow_null=True,
                                     required=False, read_only=True)
    traininguser = TrainingUserSerializer(many=True, read_only=True)

    status_tag = serializers.SerializerMethodField('get_training_status')

    class Meta:
        model = TrainingBatch
        fields = '__all__'

    @classmethod
    def get_training_status(cls, instance):
        end_date = instance.end_date
        if end_date and end_date < date.today():
            if instance.status == 4:
                instance.status = 3
                instance.save()
            elif instance.status != 3:
                instance.status = 5
                instance.save()
        if instance.status == 1:
            return 'Finalized'
        if instance.status == 2:
            return 'Notified'
        if instance.status == 3:
            return 'completed'
        if instance.status == 4:
            return 'Notified and Finalized'
        if instance.status == 5:
            return 'Time out'
        return 'draft'


class UserSerializer(DynamicFieldsModelSerializer, serializers.ModelSerializer):
    role = serializers.CharField(source='profile.role.id', allow_null=True, allow_blank=True, required=False)
    mobile_no = serializers.CharField(max_length=30, allow_null=True, allow_blank=True, required=False)
    nid = serializers.CharField(max_length=30, allow_null=True, allow_blank=True, required=False)
    office = serializers.CharField(max_length=30, allow_null=True, allow_blank=True, required=False)
    organization = serializers.CharField(source='profile.office.organization', max_length=30, allow_null=True,
                                         allow_blank=True, required=False)
    office_category = serializers.CharField(source='profile.office.office_category', max_length=30, allow_null=True,
                                            allow_blank=True, required=False)
    official_mobile_no = serializers.CharField(max_length=30, allow_null=True, allow_blank=True, required=False)
    designation = serializers.CharField(max_length=50, allow_blank=True, allow_null=True, required=False)
    # e_gp_user_id = serializers.CharField(max_length=50, allow_blank=True, allow_null=True, required=False)
    # e_gp_user_id_lgis = serializers.CharField(max_length=50, allow_blank=True, allow_null=True, required=False)
    avatar = serializers.ImageField(allow_null=True, allow_empty_file=True, required=False)
    procurement_role = serializers.CharField(max_length=300, allow_null=True, allow_blank=True, required=False)
    procurement_role_lgis = serializers.CharField(max_length=300, allow_null=True, allow_blank=True, required=False)

    description = serializers.CharField(max_length=255, allow_null=True, allow_blank=True, required=False)
    designation_name = serializers.CharField(source='profile.designation.designation', allow_blank=True,
                                             allow_null=True, required=False)
    # designation_name = serializers.SerializerMethodField('getdesignationname')
    designation_id = serializers.CharField(source='profile.designation.id', allow_blank=True, allow_null=True,
                                           required=False)
    personal_mobile_no = serializers.CharField(source='profile.mobile_no', allow_blank=True, allow_null=True,
                                               required=False)
    profile_official_mobile_no = serializers.CharField(source='profile.official_mobile_no', allow_blank=True,
                                                       allow_null=True, required=False)
    # e_gp_user_id_value = serializers.CharField(source='profile.e_gp_user_id', allow_blank=True, allow_null=True,
    #                                            required=False)
    # e_gp_user_id_lgis_value = serializers.CharField(source='profile.e_gp_user_id_lgis', allow_blank=True,
    #                                                allow_null=True, required=False)
    nid_value = serializers.CharField(source='profile.nid', allow_blank=True, allow_null=True,
                                      required=False)
    personal_email = serializers.CharField(source='profile.personal_email', allow_blank=True, allow_null=True,
                                           required=False)
    official_email = serializers.CharField(source='profile.official_email', allow_blank=True, allow_null=True,
                                           required=False)
    procurement_role_list = ProcurementRoleSerializer(source='profile.procurement_roles', read_only=True, many=True)
    procurement_role_list_lgis = ProcurementRoleSerializer(source='profile.procurement_roles_lgis', read_only=True,
                                                           many=True)
    user_training_list = TrainingBatchSerializer(source='trainingbatch_set', read_only=True, many=True)
    office_id = serializers.CharField(source='profile.office_id', allow_blank=True, allow_null=True, required=False)

    office_name = serializers.CharField(source='profile.office.name', allow_blank=True, allow_null=True, required=False)

    division = serializers.CharField(source='profile.office.division', allow_blank=True, allow_null=True,
                                     required=False)

    region = serializers.CharField(source='profile.office.region', allow_blank=True, allow_null=True, required=False)
    district = serializers.CharField(source='profile.office.district', allow_blank=True, allow_null=True,
                                     required=False)
    upazila = serializers.CharField(source='profile.office.upazila', allow_blank=True, allow_null=True, required=False)
    profile_avatar = serializers.ImageField(source='profile.avatar', allow_null=True, allow_empty_file=True,
                                            required=False)
    gender = serializers.CharField(source='profile.gender', allow_blank=True, allow_null=True, required=False)
    date_of_birth = serializers.CharField(source='profile.date_of_birth', allow_blank=True, allow_null=True,
                                          required=False)
    PPR_training = serializers.CharField(source='profile.get_PPR_training_display', allow_blank=True, allow_null=True,
                                         required=False)
    bengali_name = serializers.CharField(source='profile.bengali_name', allow_null=True, allow_blank=True,
                                         required=False)
    trainer = serializers.CharField(source='profile.trainer', allow_blank=True, allow_null=True,
                                    required=False)

    e_gp_user_id_for_govt = serializers.CharField(source='profile.e_gp_user_id_for_govt', allow_null=True,
                                                  allow_blank=True, required=False)
    e_gp_user_id_lgis_for_govt = serializers.CharField(source='profile.e_gp_user_id_lgis_for_govt', allow_null=True,
                                                       allow_blank=True, required=False)
    e_gp_user_id_for_org_admin = serializers.CharField(source='profile.e_gp_user_id_for_org_admin', allow_null=True,
                                                       allow_blank=True, required=False)
    e_gp_user_id_lgis_for_org_admin = serializers.CharField(source='profile.e_gp_user_id_lgis_for_org_admin',
                                                            allow_null=True, allow_blank=True, required=False)
    e_gp_user_id_for_pe_admin = serializers.CharField(source='profile.e_gp_user_id_for_pe_admin', allow_null=True,
                                                      allow_blank=True, required=False)
    e_gp_user_id_lgis_for_pe_admin = serializers.CharField(source='profile.e_gp_user_id_lgis_for_pe_admin',
                                                           allow_null=True, allow_blank=True, required=False)
    floating = serializers.BooleanField(source='profile.floating', required=False)
    existing_user = serializers.SerializerMethodField()
    training_start_date = serializers.SerializerMethodField()
    training_venue = serializers.SerializerMethodField()

    temp_office = serializers.SerializerMethodField('getTempOffice')

    # @classmethod
    # def getdesignationname(cls, obj):
    #     print(obj.profile.office)
    #     user_data = User.objects.get(id=obj.id)
    #     temp_designation = TemporaryOffice.objects.get(user_id=user_data.profile).values_list('designation_id', flat=True)
    #     return obj.first_name

    @classmethod
    def getTempOffice(cls, obj):

        profileid = Profile.objects.filter(id=obj.profile_id)
        proid = profileid[0].office_id

        temp_offices_users = TemporaryOffice.objects.filter(office_id=proid).values_list('user_id', flat=True)
        temp_offices_users = tuple(temp_offices_users)
        # print(temp_offices_users)
        # print(self)
        # print(obj.profile_id)

        temp_users_list = []

        for x in temp_offices_users:
            # print(x)
            temp_users = {}
            temp_user = User.objects.get(profile_id=x)

            temp_users['id'] = temp_user.id

            if temp_user.first_name is not None:
                temp_users['first_name'] = temp_user.first_name
            else:
                temp_users['first_name'] = ""

            if temp_user.profile.mobile_no is not None:
                temp_users['mobile_no'] = temp_user.profile.mobile_no
            else:
                temp_users['mobile_no'] = ""

            if temp_user.profile.nid is not None:
                temp_users['nid'] = temp_user.profile.nid
            else:
                temp_users['nid'] = ""

            temp_users_list.append(temp_users)

        return temp_users_list

    @classmethod
    def getTempOfficeuser(cls, obj):

        # profile_id = Profile.objects.get(id=obj.profile_id)
        temp_offices_users = TemporaryOffice.objects.filter(office_id=office_id).values_list('user_id', flat=True)
        temp_offices_users = tuple(temp_offices_users)

        offices = []

        for x in temp_offices_users:
            office_data = {}
            temp_office = Office.objects.get(id=x)

            office_data['id'] = temp_office.id

            if temp_office.name is not None:
                office_data['name'] = temp_office.name
            else:
                office_data['name'] = ""

            if temp_office.division is not None:
                office_data['division'] = temp_office.division.name
            else:
                office_data['division'] = ""

            if temp_office.region is not None:
                office_data['region'] = temp_office.region.name
            else:
                office_data['region'] = ""

            if temp_office.district is not None:
                office_data['district'] = temp_office.district.name
            else:
                office_data['district'] = ""

            if temp_office.upazila is not None:
                office_data['upazila'] = temp_office.upazila.name
            else:
                office_data['upazila'] = ""

            if temp_office.organization is not None:
                office_data['organization'] = temp_office.organization
            else:
                office_data['organization'] = ""

            if temp_office.office_category is not None:
                office_data['office_category'] = temp_office.office_category
            else:
                office_data['office_category'] = ""

            offices.append(office_data)
            # office_data_row = Office.objects.filter(id=x).values_list('name', 'division', 'region', 'district', 'upazila', 'organization', 'office_category')
            # office_data_row = list(office_data_row)
            # temp = {"id" : x, "name" : office_data_row[0][0], "division" : office_data_row[0][1], "region" : office_data_row[0][2], "district" : office_data_row[0][3], "upazila" : office_data_row[0][4], "organization" : office_data_row[0][5], "office_category" : office_data_row[0][6]}
            # temp = dict(temp)
            # office_data[i] = temp
            # i = i + 1
        # print(office_data)

        return offices

    @staticmethod
    def get_training_start_date(obj):
        tb = TrainingUser.objects.filter(user=obj, training__created_by_status=2)
        #  print(tb)
        if tb:
            return tb[0].training.start_date
        else:
            return None

    @staticmethod
    def get_training_venue(obj):
        tb = TrainingUser.objects.filter(user=obj, training__created_by_status=2)
        if tb and tb[0].training.venue:
            return tb[0].training.venue.id
        else:
            return None

    @staticmethod
    def get_existing_user(obj):  # procurement role, procurement_roles_lgis, trainer, ppr_training
        # or obj.profile.e_gp_user_id_for_govt or\
        #         obj.profile.e_gp_user_id_lgis_for_govt or obj.profile.e_gp_user_id_for_org_admin or \
        #         obj.profile.e_gp_user_id_lgis_for_org_admin or obj.profile.e_gp_user_id_for_pe_admin or \
        #         obj.profile.e_gp_user_id_lgis_for_pe_admin
        if obj.profile.mobile_no or obj.profile.date_of_birth or obj.profile.gender or \
                obj.profile.bengali_name or obj.profile.avatar or \
                obj.profile.nid or obj.first_name or obj.profile.personal_email or obj.profile.PPR_training:
            return True
        if TrainingUser.objects.filter(user=obj).count() != 0:
            return True

        if obj.profile.is_temp_office_assign == True:
            return True

        return False

    class Meta:
        model = User
        fields = '__all__'
        # ('username','password','email','first_name','last_name','mobile_no','designation','avatar','procurement_role','description')


class DesignationSerializer(DynamicFieldsModelSerializer, serializers.ModelSerializer):
    office_categories = serializers.ListField(
        child=serializers.CharField()
    )

    class Meta:
        model = Designation
        fields = '__all__'


class DivisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Division
        fields = '__all__'


class CityCorporationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CityCorporation
        fields = '__all__'


class RegionSerializer(serializers.ModelSerializer):
    division_value = serializers.CharField(source='division.name', allow_blank=True, allow_null=True,
                                           required=False)

    class Meta:
        model = Region
        fields = '__all__'


class DistrictSerializer(DynamicFieldsModelSerializer, serializers.ModelSerializer):
    region_value = serializers.CharField(source='region.name', allow_blank=True, allow_null=True,
                                         required=False)

    class Meta:
        model = District
        fields = '__all__'


class UpazilaSerializer(serializers.ModelSerializer):
    district_value = serializers.CharField(source='district.name', allow_blank=True, allow_null=True,
                                           required=False)

    class Meta:
        model = Upazila
        fields = '__all__'


class OfficeSerializer(DynamicFieldsModelSerializer, serializers.ModelSerializer):
    users = serializers.CharField(max_length=5000, allow_null=True, allow_blank=True, required=False)
    division_name = serializers.CharField(source='division.name', allow_blank=True, allow_null=True, required=False)
    region_name = serializers.CharField(source='region.name', allow_blank=True, allow_null=True, required=False)
    district_name = serializers.CharField(source='district.name', allow_blank=True, allow_null=True, required=False)
    upazila_name = serializers.CharField(source='upazila.name', allow_blank=True, allow_null=True, required=False)
    role_exist = serializers.SerializerMethodField()
    number_of_trainers = serializers.SerializerMethodField()
    last_update = serializers.SerializerMethodField()
    mayor_name = serializers.SerializerMethodField()

    @staticmethod
    def get_role_exist(obj):
        role_dict = {'focal_point': False, 'org_admin': False, 'pe_admin': False}
        # if obj.office_category != 'LGED HQ':
        users = User.objects.filter(profile__office=obj)
        roles = ProcurementRole.objects.all()
        for user in users:
            procurement_role_lged = user.profile.procurement_roles.values_list('role', flat=True)
            procurement_role_lgis = user.profile.procurement_roles_lgis.values_list('role', flat=True)
            if 'Focal Point' in procurement_role_lged or 'Focal Point' in procurement_role_lgis:
                role_dict['focal_point'] = roles.filter(role='Focal Point')[0].id
            if 'Organization Admin' in procurement_role_lged or 'Organization Admin' in procurement_role_lgis:
                role_dict['org_admin'] = roles.filter(role='Organization Admin')[0].id
            if 'PE Admin' in procurement_role_lged or 'PE Admin' in procurement_role_lgis:
                role_dict['pe_admin'] = roles.filter(role='PE Admin')[0].id
        return role_dict
        # else:
        #    return role_dict

    @staticmethod
    def get_number_of_trainers(obj):
        # print(obj.profile_set.filter(trainer=True).count())
        return Profile.objects.filter(trainer=True, training_under=obj).count()

    @staticmethod
    def get_last_update(obj):
        return Profile.objects.filter(training_under__id=obj.id, trainer=True).aggregate(Max('updated_at'))[
            'updated_at__max']

    @staticmethod
    def get_mayor_name(obj):
        if obj.office_category == 'UPAZILA PARISHAD OFFICES':
            if obj.profile_set.filter(designation__designation='Chairman (Upazila Parishad)'):
                try:
                    return obj.profile_set.filter(designation__designation='Chairman (Upazila Parishad)')[
                        0].user.first_name
                except Exception as e:
                    return ''
            else:
                return ''
        else:
            if obj.profile_set.filter(designation__designation='Mayor'):
                try:
                    return obj.profile_set.filter(designation__designation='Mayor')[0].user.first_name
                except Exception as e:
                    return ''
            else:
                return ''

    class Meta:
        model = Office
        fields = '__all__'


class PackageNoSerializer(serializers.ModelSerializer):
    source_value = serializers.CharField(source='source.source', allow_blank=True, allow_null=True, required=False)

    class Meta:
        model = PackageNo
        fields = '__all__'


class DevicesSerializer(serializers.ModelSerializer):
    type_value = serializers.CharField(source='type.type', allow_blank=True, allow_null=True, required=False)

    class Meta:
        model = Devices
        fields = '__all__'


class InventoryFileTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryFileType
        fields = '__all__'


class InventoryTypeSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='type_category.category', read_only=True, allow_null=True, allow_blank=True)

    class Meta:
        model = InventoryType
        fields = '__all__'


class InventoryTypeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryTypeCategory
        fields = '__all__'


class InventoryStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryStatus
        fields = '__all__'


class InventoryFileSerializer(serializers.ModelSerializer):
    file_size = serializers.SerializerMethodField()

    class Meta:
        model = InventoryFile
        fields = '__all__'

    @staticmethod
    def get_file_size(ob):
        try:
            return ob.document.size
        except Exception as e:
            return 0


class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = '__all__'


class SupplierSerializer(serializers.ModelSerializer):
    supplier_district_name = serializers.CharField(source='supplier_district.name', allow_blank=True,
                                                   allow_null=True, required=False)

    class Meta:
        model = Supplier
        fields = '__all__'


class SupportCenterSerializer(serializers.ModelSerializer):
    support_center_district_name = serializers.CharField(source='support_center_district.name', allow_blank=True,
                                                         allow_null=True, required=False)

    class Meta:
        model = SupportCenter
        fields = '__all__'


class InventorySerializer(serializers.ModelSerializer):
    office_category = serializers.CharField(source='office.office_category', allow_blank=True, allow_null=True,
                                            required=False)
    office_name = serializers.CharField(source='office.name', allow_blank=True, allow_null=True, required=False)
    division = serializers.CharField(source='office.division', allow_blank=True, allow_null=True, required=False)
    region = serializers.CharField(source='office.region', allow_blank=True, allow_null=True, required=False)
    district = serializers.CharField(source='office.district', allow_blank=True, allow_null=True, required=False)
    upazila = serializers.CharField(source='office.upazila', allow_blank=True, allow_null=True, required=False)
    office_district = serializers.CharField(source='office.district.name', allow_blank=True, allow_null=True,
                                            required=False)
    document = serializers.ListField(
        child=serializers.FileField(max_length=100000,
                                    allow_empty_file=False,
                                    use_url=False), required=False
    )
    document_list = InventoryFileSerializer(source='inventoryfile_set', read_only=True, many=True)
    status_value = serializers.CharField(source='status.status', allow_blank=True,
                                         allow_null=True, required=False)
    type_value = serializers.CharField(source='type.type', allow_blank=True,
                                       allow_null=True, required=False)
    type_category_value = serializers.CharField(source='type.type_category.category', allow_blank=True,
                                                allow_null=True, required=False)
    type_category_id = serializers.CharField(source='type.type_category.id', allow_blank=True,
                                             allow_null=True, required=False)
    source_value = serializers.CharField(max_length=100, allow_null=True, allow_blank=True,
                                         required=False)
    procured_by = serializers.CharField(source='package_no.source', max_length=100, allow_null=True, allow_blank=True,
                                        required=False)
    # device_id = serializers.SerializerMethodField()
    # brand_name_value = serializers.SerializerMethodField()
    # model_no_value = serializers.SerializerMethodField()
    # validity_value = serializers.SerializerMethodField()
    device_id = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    brand_name_value = serializers.CharField(source='device.brand_name', allow_blank=True, allow_null=True,
                                             required=False)
    model_no_value = serializers.CharField(source='device.model_no', allow_null=True, allow_blank=True,
                                           required=False)
    validity_value = serializers.CharField(source='device.validity', allow_null=True, allow_blank=True,
                                           required=False)

    package_no_value = serializers.CharField(source='package_no.package_no', allow_blank=True,
                                             allow_null=True, required=False)
    package_spec_value = serializers.CharField(source='package_no.document', allow_blank=True,
                                               allow_null=True, required=False)
    file_name = serializers.CharField(allow_blank=True, allow_null=True, required=False)

    # supplier = SupplierSerializer(source='package_no.supplier_set', allow_null=True, many=True, required=False)
    # support_center = SupportCenterSerializer(source='package_no.supportcenter_set', allow_null=True, many=True,
    #                                          required=False)

    class Meta:
        model = Inventory
        exclude = []

    @staticmethod
    def get_device_id(ob):
        try:
            return ob.package_no.devices_set.get(type=ob.type).id if ob.package_no else None
        except Exception as e:
            return None

    @staticmethod
    def get_brand_name_value(ob):
        try:
            return ob.package_no.devices_set.get(type=ob.type).brand_name if ob.package_no else None
        except Exception as e:
            return None

    @staticmethod
    def get_model_no_value(ob):
        try:
            return ob.package_no.devices_set.get(type=ob.type).model_no if ob.package_no else None
        except Exception as e:
            return None

    @staticmethod
    def get_validity_value(ob):
        try:
            return ob.package_no.devices_set.get(type=ob.type).validity if ob.package_no else None
        except Exception as e:
            return None


class InventoryProductsSerializer(serializers.ModelSerializer):
    user_designation_name = serializers.CharField(source='user_designation.designation', allow_null=True,
                                                  allow_blank=True,
                                                  required=False)
    inv_object = InventorySerializer(source="inventory", allow_null=True, read_only=True)

    class Meta:
        model = InventoryProducts
        fields = '__all__'


class ResourceCenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourceCenter
        fields = '__all__'


# class NominatedOfficialSerializer(serializers.ModelSerializer):
#     first_name = serializers.CharField(source='user.first_name', allow_blank=True, allow_null=True, required=False)
#     last_name = serializers.CharField(source='user.last_name', allow_blank=True, allow_null=True, required=False)
#     designation = serializers.CharField(source='user.profile.designation.designation', allow_blank=True,
#                                         allow_null=True, required=False)
#     office_id = serializers.CharField(source='user.profile.office.id', allow_blank=True, allow_null=True,
#                                       required=False)
#     office_name = serializers.CharField(source='user.profile.office.name', allow_blank=True, allow_null=True,
#                                         required=False)
#     mobile_no = serializers.CharField(source='user.profile.official_mobile_no', allow_blank=True, allow_null=True,
#                                       required=False)
#     email = serializers.CharField(source='user.email', allow_blank=True, allow_null=True, required=False)
#
#     class Meta:
#         model = NominatedOfficial
#         fields = '__all__'


class PublicationSerializer(serializers.ModelSerializer):
    publication_type = serializers.CharField(source='type.type', allow_null=True, allow_blank=True, required=False)

    office_categories = serializers.SerializerMethodField('get_office_categories_method')

    class Meta:
        model = Publication
        fields = '__all__'

    @classmethod
    def get_office_categories_method(cls, instance):
        all_offices = instance.office.all()
        categories = []
        short_codes = ''
        for office in all_offices:
            category = office.office_category
            if category in categories:
                continue
            categories.append(category)
            if category == 'ZILA PARISHAD OFFICES':
                short_codes += 'ZP,'
                continue
            if category == 'UPAZILA PARISHAD OFFICES':
                short_codes += 'UZP,'
                continue
            if category == 'PAURASHAVA OFFICES':
                short_codes += 'PS,'
                continue
            if category == 'CITY CORPORATION OFFICES':
                short_codes += 'CC,'
                continue
            if category == 'CE Office (HQ)':
                short_codes += 'CE,'
                continue
            if category == 'Additional Chief Engineer Office (HQ)':
                short_codes += 'ACE (HQ),'
                continue
            if category == 'SE Office (HQ)':
                short_codes += 'SE (HQ),'
                continue
            if category == 'Project Office (HQ)':
                short_codes += 'PD (HQ),'
                continue
            if category == 'Division Office (Field)':
                short_codes += 'ACE (Div),'
                continue
            if category == 'Regional Office (Field)':
                short_codes += 'SE (Region),'
                continue
            if category == 'District Office (Field)':
                short_codes += 'XEN (Dist),'
                continue
            if category == 'Upazila Engineer Office(Field)':
                short_codes += 'UE,'
                continue
            short_codes += category + ','
        return short_codes




class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = '__all__'


class TransferHistorySerializer(serializers.ModelSerializer):
    # prev_office_name = serializers.CharField(source='user.profile.office.name', allow_null=True, allow_blank=True,
    #                                          required=False, read_only=True)
    # prev_designation = serializers.CharField(source='user.profile.designation.designation', allow_null=True, allow_blank=True,
    #                                          required=False, read_only=True)
    # prev_official_mobile_no = serializers.CharField(source='user.profile.official_mobile_no', allow_null=True, allow_blank=True,
    #                                                 required=False, read_only=True)
    # prev_official_email = serializers.CharField(source='user.email', allow_null=True, allow_blank=True,
    #                                             required=False, read_only=True)
    prev_office_name = serializers.SerializerMethodField()
    prev_designation = serializers.SerializerMethodField()
    prev_official_mobile_no = serializers.SerializerMethodField()
    prev_official_email = serializers.SerializerMethodField()
    transferred_office_org = serializers.CharField(source='transferred_office.organization', allow_null=True,
                                                   allow_blank=True, required=False)
    transferred_office_off_cat = serializers.CharField(source='transferred_office.office_category', allow_null=True,
                                                       allow_blank=True, required=False)
    transferred_office_name = serializers.CharField(source='transferred_office.name', allow_null=True, allow_blank=True,
                                                    required=False, read_only=True)
    new_designation_name = serializers.CharField(source='new_designation.designation', allow_null=True,
                                                 allow_blank=True, required=False, read_only=True)
    status_display = serializers.CharField(source='get_status_display', allow_null=True, allow_blank=True,
                                           required=False, read_only=True)
    type_display = serializers.CharField(source='get_transfer_type_display', allow_null=True, allow_blank=True,
                                         required=False, read_only=True)

    class Meta:
        model = TransferHistory
        fields = '__all__'
        # exclude = ('previous_official_info', 'previous_personal_info')

    @staticmethod
    def get_prev_office_name(obj):
        if obj.previous_official_info:
            return Office.objects.get(id=obj.previous_official_info['office']).name
        else:
            return ''

    @staticmethod
    def get_prev_designation(obj):
        if obj.previous_official_info:
            return Designation.objects.get(id=obj.previous_official_info['designation']).designation
        else:
            return ''

    @staticmethod
    def get_prev_official_mobile_no(obj):
        if obj.previous_official_info:
            return obj.previous_official_info['official_mobile_no']
        else:
            return ''

    @staticmethod
    def get_prev_official_email(obj):
        if obj.previous_official_info:
            return obj.previous_official_info['official_email']
        else:
            return ''


class MultipleAssignHistorySerializer(serializers.ModelSerializer):
    prev_office_name = serializers.SerializerMethodField()
    prev_designation = serializers.SerializerMethodField()
    prev_official_mobile_no = serializers.SerializerMethodField()
    prev_official_email = serializers.SerializerMethodField()
    assigned_office_org = serializers.CharField(source='assigned_office.organization', allow_null=True,
                                                allow_blank=True, required=False)
    assigned_office_off_cat = serializers.CharField(source='assigned_office.office_category', allow_null=True,
                                                    allow_blank=True, required=False)
    assigned_office_name = serializers.CharField(source='assigned_office.name', allow_null=True, allow_blank=True,
                                                 required=False, read_only=True)
    new_designation_name = serializers.CharField(source='new_designation.designation', allow_null=True,
                                                 allow_blank=True, required=False, read_only=True)
    status_display = serializers.CharField(source='get_status_display', allow_null=True, allow_blank=True,
                                           required=False, read_only=True)
    type_display = serializers.CharField(source='get_multiassign_type_display', allow_null=True, allow_blank=True,
                                         required=False, read_only=True)

    class Meta:
        model = MultipleAssignHistory
        fields = '__all__'
        # exclude = ('previous_official_info', 'previous_personal_info')

    @staticmethod
    def get_prev_office_name(obj):
        if obj.previous_official_info:
            return Office.objects.get(id=obj.previous_official_info['office']).name
        else:
            return ''

    @staticmethod
    def get_prev_designation(obj):
        if obj.previous_official_info:
            return Designation.objects.get(id=obj.previous_official_info['designation']).designation
        else:
            return ''

    @staticmethod
    def get_prev_official_mobile_no(obj):
        if obj.previous_official_info:
            return obj.previous_official_info['official_mobile_no']
        else:
            return ''

    @staticmethod
    def get_prev_official_email(obj):
        if obj.previous_official_info:
            return obj.previous_official_info['official_email']
        else:
            return ''


class BudgetTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetType
        fields = '__all__'


class ProcurementNatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcurementNature
        fields = '__all__'


class CommitteeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommitteeType
        fields = '__all__'


class TypeOfEmergencySerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeOfEmergency
        fields = '__all__'


class ProcMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcMethod
        fields = '__all__'


class ProcTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcType
        fields = '__all__'


class ApprovingAuthoritySerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovingAuthority
        fields = '__all__'


class SourceOfFundSerializer(serializers.ModelSerializer):
    class Meta:
        model = SourceOfFund
        fields = '__all__'


class FundDisburseFromSerializer(serializers.ModelSerializer):
    class Meta:
        model = FundDisburseFrom
        fields = '__all__'


class FundedBySerializer(serializers.ModelSerializer):
    class Meta:
        model = FundedBy
        fields = '__all__'


class ContractStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractStatus
        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):
    # pd_office_name = serializers.CharField(source='pd_office.name', allow_blank=True, allow_null=True, required=False)
    # prev_cost = serializers.CharField(max_length=20, allow_null=True, allow_blank=True, required=False)
    # source_of_fund = serializers.SlugRelatedField(many=True, slug_field='source', read_only=True, allow_null=True)
    partner = serializers.CharField(source='development_partner.funded_by', allow_null=True, allow_blank=True,
                                    required=False)

    class Meta:
        model = Project
        fields = '__all__'


class APPSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='office.organization', allow_blank=True, allow_null=True,
                                              required=False)
    office_category = serializers.CharField(source='office.office_category', allow_blank=True, allow_null=True,
                                            required=False)
    office_name = serializers.CharField(source='office.name', allow_blank=True, allow_null=True, required=False)
    division_name = serializers.CharField(source='office.division.name', allow_blank=True, allow_null=True,
                                          required=False)
    region_name = serializers.CharField(source='office.region.name', allow_blank=True, allow_null=True, required=False)
    district_name = serializers.CharField(source='office.district.name', allow_blank=True, allow_null=True,
                                          required=False)
    upazila_name = serializers.CharField(source='office.upazila.name', allow_blank=True, allow_null=True,
                                         required=False)
    budget_type_value = serializers.CharField(source='budget_type.type', allow_blank=True, allow_null=True,
                                              required=False)
    project_name = serializers.CharField(source='project.name', allow_blank=True, allow_null=True,
                                         required=False)
    source_of_fund_value = serializers.CharField(source='source_of_fund.source', allow_blank=True, allow_null=True,
                                                 required=False)
    no_of_package = serializers.SerializerMethodField()
    is_editable = serializers.SerializerMethodField()

    @staticmethod
    def get_no_of_package(obj):
        try:
            return obj.package_set.count()
        except Exception as e:
            return 0

    @staticmethod
    def get_is_editable(obj):
        if APP.objects.filter(id=obj.id, package__approval_date__isnull=False).count() == 0:
            return True
        else:
            return False

    class Meta:
        model = APP
        fields = '__all__'


class PackageSerializer(serializers.ModelSerializer):
    organization = serializers.CharField(source='app_id.office.organization', allow_blank=True, allow_null=True,
                                         required=False)
    office_category = serializers.CharField(source='app_id.office.office_category', allow_blank=True, allow_null=True,
                                            required=False)
    office_name = serializers.CharField(source='app_id.office.name', allow_blank=True, allow_null=True, required=False)
    division_name = serializers.CharField(source='app_id.office.division.name', allow_blank=True, allow_null=True,
                                          required=False)
    region_name = serializers.CharField(source='app_id.office.region.name', allow_blank=True, allow_null=True,
                                        required=False)
    district_name = serializers.CharField(source='app_id.office.district.name', allow_blank=True, allow_null=True,
                                          required=False)
    upazila_name = serializers.CharField(source='app_id.office.upazila.name', allow_blank=True, allow_null=True,
                                         required=False)
    app_id_value = serializers.CharField(source='app_id.app_id', allow_blank=True, allow_null=True,
                                         required=False)
    proc_nature_value = serializers.CharField(source='proc_nature.nature', allow_blank=True, allow_null=True,
                                              required=False)
    type_of_emergency_value = serializers.CharField(source='type_of_emergency.type', allow_blank=True, allow_null=True,
                                                    required=False)
    approving_authority_value = serializers.CharField(source='approving_authority.authority', allow_blank=True,
                                                      allow_null=True, required=False)
    proc_method_value = serializers.CharField(source='proc_method.method', allow_blank=True, allow_null=True,
                                              required=False)
    proc_type_value = serializers.CharField(source='proc_type.type', allow_blank=True, allow_null=True,
                                            required=False)
    apps = APPSerializer(source="app_id", allow_null=True, required=False)
    lot_no = serializers.SerializerMethodField()

    @staticmethod
    def get_lot_no(ob):
        try:
            return Lot.objects.filter(package_no=ob, lot_description__isnull=False).count()
        except Exception as e:
            return 0

    # lots = LotSerializer(many=True, allow_null=True)

    class Meta:
        model = Package
        fields = '__all__'

    #
    # def create(self, validated_data):
    #     lots_data = validated_data.pop('lots')
    #     print(lots_data)
    #     office = validated_data['office']
    #     package = Package.objects.create(**validated_data)
    #     for lot_data in lots_data:
    #         Lot.objects.create(package_no=package, office=office, **lot_data)
    #     return package
    def update(self, instance, validated_data):
        info = model_meta.get_field_info(instance)

        # Simply set each attribute on the instance, and then save it.
        # Note that unlike `.create()` we don't need to treat many-to-many
        # relationships as being a special case. During updates we already
        # have an instance pk for the relationships to be associated with.
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                field = getattr(instance, attr)
                field.set(value)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance


class APPReportSerializer(serializers.BaseSerializer):

    def to_representation(self, obj):
        office = Office.objects.get(id=obj['office'])
        data = {
            'e_GP_Packages': obj['e_GP_Packages'],
            'offline_Packages': obj['offline_Packages'],
            'e_GP_percentage': obj['e_GP_percentage'],
            'offline_percentage': obj['offline_percentage'],
            'office': obj['office'],
            'office_name': office.name,
            'division_name': office.division.name if office.division is not None else '',
            'upazila_name': office.upazila.name if office.upazila is not None else '',
            'region_name': office.region.name if office.region is not None else '',
            'district_name': office.district.name if office.district is not None else '',
        }
        return data


class LotSerializer(serializers.ModelSerializer):
    office_name = serializers.CharField(source='package_no.app_id.office.name', allow_blank=True, allow_null=True,
                                        required=False)
    division_name = serializers.CharField(source='package_no.app_id.office.division.name', allow_blank=True,
                                          allow_null=True,
                                          required=False)
    region_name = serializers.CharField(source='package_no.app_id.office.region.name', allow_blank=True,
                                        allow_null=True, required=False)
    district_name = serializers.CharField(source='package_no.app_id.office.district.name', allow_blank=True,
                                          allow_null=True,
                                          required=False)
    upazila_name = serializers.CharField(source='package_no.app_id.office.upazila.name', allow_blank=True,
                                         allow_null=True,
                                         required=False)
    source_of_fund_value = serializers.CharField(source='source_of_fund.source', allow_blank=True, allow_null=True,
                                                 required=False)
    package_no_value = serializers.CharField(source='package_no.package_no', allow_blank=True, allow_null=True,
                                             required=False)
    app_id_value = serializers.CharField(source='package_no.app_id.app_id', allow_blank=True, allow_null=True,
                                         required=False)
    package = PackageSerializer(source="package_no", allow_null=True, read_only=True)
    # package_no = serializers.CharField(source="package_no.id", allow_null=True, allow_blank=True)
    blank_lot = serializers.SerializerMethodField()
    package_blank_lot = serializers.SerializerMethodField()
    tender_no = serializers.SerializerMethodField()

    class Meta:
        model = Lot
        fields = '__all__'

    @staticmethod
    def get_blank_lot(ob):
        try:
            lots = Lot.objects.filter(package_no__app_id=ob.package_no.app_id, lot_description=None)
            if lots:
                return 1
            else:
                return 0
        except Exception as e:
            return 1

    @staticmethod
    def get_package_blank_lot(ob):
        try:
            lots = Lot.objects.filter(lot_description=None, package_no=ob.package_no)
            if lots:
                return 1
            else:
                return 0
        except Exception as e:
            return 1

    @staticmethod
    def get_tender_no(ob):
        try:
            tenders = Tender.objects.filter(package=ob.package_no)
            return tenders.count()
        except Exception as e:
            return 0


class FirmSerializer(serializers.ModelSerializer):
    is_lead_firm = serializers.SerializerMethodField()

    class Meta:
        model = Firm
        fields = '__all__'

    @staticmethod
    def get_is_lead_firm(obj):
        if obj.contract and obj.contract.lead_firm_id == obj:
            return True
        else:
            return False


class TenderCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenderCost
        fields = '__all__'


class TenderSerializer(DynamicFieldsModelSerializer, serializers.ModelSerializer):
    organization_name = serializers.CharField(source='package.app_id.office.organization', allow_blank=True,
                                              allow_null=True,
                                              required=False)
    office_category = serializers.CharField(source='package.app_id.office.office_category', allow_blank=True,
                                            allow_null=True,
                                            required=False)
    office_name = serializers.CharField(source='package.app_id.office.name', allow_blank=True, allow_null=True,
                                        required=False)
    division_name = serializers.CharField(source='package.app_id.office.division.name', allow_blank=True,
                                          allow_null=True,
                                          required=False)
    region_name = serializers.CharField(source='package.app_id.office.region.name', allow_blank=True, allow_null=True,
                                        required=False)
    district_name = serializers.CharField(source='package.app_id.office.district.name', allow_blank=True,
                                          allow_null=True,
                                          required=False)
    upazila_name = serializers.CharField(source='package.app_id.office.upazila.name', allow_blank=True, allow_null=True,
                                         required=False)
    package_no_value = serializers.CharField(source='package.package_no', allow_blank=True, allow_null=True,
                                             required=False)
    package_description = serializers.CharField(source='package.package_description', allow_blank=True, allow_null=True,
                                                required=False)
    approving_authority_value = serializers.CharField(source='approving_authority.authority', allow_blank=True,
                                                      allow_null=True, required=False)
    no_of_lot = serializers.SerializerMethodField()

    contract_no = serializers.SerializerMethodField()
    app_id = serializers.CharField(source='package.app_id.app_id', allow_blank=True, allow_null=True, required=False)
    is_retender_possible = serializers.SerializerMethodField()

    # package_value = PackageSerializer(source="package", allow_null=True, read_only=True)

    # firms_list = FirmSerializer(source='firms', read_only=True, many=True)

    class Meta:
        model = Tender
        fields = '__all__'

    @staticmethod
    def get_no_of_lot(ob):
        try:
            return Lot.objects.filter(package_no=ob.package).count()
        except Exception as e:
            return 0

    @staticmethod
    def get_contract_no(obj):
        try:
            contract = NewContract.objects.filter(tender=obj.id)
            return obj.package.lots.count() - contract.count()
        except Exception as e:
            return 0

    @staticmethod
    def get_is_retender_possible(obj):
        if Tender.objects.filter(previous_tender=obj.tender_id).count() != 0:
            return False
        return True


class NewContractSerializer(serializers.ModelSerializer):
    # organization_name = serializers.CharField(source='tender.office.organization', allow_blank=True, allow_null=True,
    #                                           required=False)
    # office_category = serializers.CharField(source='tender.office.office_category', allow_blank=True, allow_null=True,
    #                                         required=False)
    office_name = serializers.CharField(source='tender.office.name', allow_blank=True, allow_null=True, required=False)
    division_name = serializers.CharField(source='tender.office.division.name', allow_blank=True, allow_null=True,
                                          required=False)
    region_name = serializers.CharField(source='tender.office.region.name', allow_blank=True, allow_null=True,
                                        required=False)
    district_name = serializers.CharField(source='tender.office.district.name', allow_blank=True, allow_null=True,
                                          required=False)
    upazila_name = serializers.CharField(source='tender.office.upazila.name', allow_blank=True, allow_null=True,
                                         required=False)
    firms = FirmSerializer(many=True, read_only=True)
    noa_no = serializers.SerializerMethodField()
    tender_id = serializers.IntegerField(source='tender.tender_id', allow_null=True, read_only=True)
    type = serializers.CharField(source='tender.package.app_id.type', allow_null=True, read_only=True)
    payment_no = serializers.SerializerMethodField()

    class Meta:
        model = NewContract
        fields = '__all__'

    @staticmethod
    def get_noa_no(obj):
        try:
            return obj.tender.package.lots.count() - obj.tender.contract_set.count()
        except Exception as e:
            return 0

    @staticmethod
    def get_payment_no(obj):
        try:
            if obj.payment_set:
                return obj.payment_set.id
        except Exception as e:
            return False

    def create(self, validated_data):
        with transaction.atomic():
            firms_data = json.loads(self.context['request'].data['firms'])
            contract = NewContract.objects.create(**validated_data)
            firm_no = len(firms_data.keys())
            # for key in firms_data.keys():
            for i in range(0, firm_no):
                key = 'firm' + str(i + 1)
                firm_data = firms_data[key]
                lead_firm_id = firm_data.pop('lead_firm_id')
                firm_instance = Firm.objects.create(contract=contract, **firm_data)
                if lead_firm_id == 'on':
                    contract.lead_firm_id = firm_instance
                    contract.save()
            return contract

    def update(self, instance, validated_data):
        with transaction.atomic():
            info = model_meta.get_field_info(instance)
            firms_data = json.loads(self.context['request'].data['firms'])
            current_firms = []
            firm_no = len(firms_data.keys())
            # for key in firms_data.keys():
            for i in range(0, firm_no):
                key = 'firm' + str(i + 1)
                firm_data = firms_data[key]
                if firm_data['firm_id'] and firm_data['firm_id'] != '' and firm_data['firm_id'] != 'null':
                    current_firms.append(firm_data['firm_id'])
                    firm_instance = Firm.objects.filter(id=firm_data['firm_id'])
                    firm_data.pop('firm_id')
                    lead_firm_id = firm_data.pop('lead_firm_id')
                    firm_instance.update(**firm_data)
                    if lead_firm_id == 'on':
                        firm_instance[0].contract.lead_firm_id = firm_instance[0]
                        firm_instance[0].contract.save()
                else:
                    if firm_data['firm_id'] is not None:
                        firm_data.pop('firm_id')
                    lead_firm_id = firm_data.pop('lead_firm_id')
                    new = Firm.objects.create(contract=instance, **firm_data)
                    if lead_firm_id == 'on':
                        new.contract.lead_firm_id = new
                        new.contract.save()
                    current_firms.append(new.id)
            Firm.objects.filter(~Q(id__in=current_firms), contract=instance).delete()

            for attr, value in validated_data.items():
                if attr in info.relations and info.relations[attr].to_many:
                    field = getattr(instance, attr)
                    field.set(value)
                else:
                    setattr(instance, attr, value)
            instance.save()
            return instance


class ContractSerializer(serializers.ModelSerializer):
    office_name = serializers.CharField(source='office.name', allow_blank=True, allow_null=True, required=False)
    division_name = serializers.CharField(source='office.division.name', allow_blank=True, allow_null=True,
                                          required=False)
    region_name = serializers.CharField(source='office.region.name', allow_blank=True, allow_null=True, required=False)
    district_name = serializers.CharField(source='office.district.name', allow_blank=True, allow_null=True,
                                          required=False)
    upazila_name = serializers.CharField(source='office.upazila.name', allow_blank=True, allow_null=True,
                                         required=False)
    # status_value = serializers.CharField(source='status.status', allow_blank=True, allow_null=True, required=False)
    tender_id_value = serializers.CharField(source='tender_id.tender_id', allow_blank=True, allow_null=True,
                                            required=False)

    class Meta:
        model = Contract
        fields = '__all__'


class ContractPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractPayment
        fields = '__all__'


class BudgetCommonSerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetCommon
        fields = '__all__'


class BudgetSerializer(serializers.ModelSerializer):
    organization = serializers.CharField(source='office.organization', allow_blank=True, allow_null=True,
                                         required=False)
    office_category = serializers.CharField(source='office.office_category', allow_blank=True, allow_null=True,
                                            required=False)
    office_id = serializers.CharField(source='office.id', allow_blank=True, allow_null=True,
                                      required=False)
    office_name = serializers.CharField(source='office.name', allow_blank=True, allow_null=True, required=False)
    division_name = serializers.CharField(source='office.division.name', allow_blank=True, allow_null=True,
                                          required=False)
    region_name = serializers.CharField(source='office.region.name', allow_blank=True, allow_null=True, required=False)
    district_name = serializers.CharField(source='office.district.name', allow_blank=True, allow_null=True,
                                          required=False)
    upazila_name = serializers.CharField(source='office.upazila.name', allow_blank=True, allow_null=True,
                                         required=False)

    # memo_no = serializers.CharField(max_length=500, allow_blank=True, allow_null=True, required=False)
    # fund_disburse_from = serializers.CharField(max_length=100, allow_blank=True, allow_null=True, required=False)
    # issue_date = serializers.DateField(allow_null=True, required=False)
    # financial_year = serializers.CharField(max_length=100, allow_blank=True, allow_null=True, required=False)
    # total_provision = serializers.FloatField(allow_null=True, required=False)
    # installment_no = serializers.CharField(max_length=300, allow_blank=True, allow_null=True, required=False)
    # subject = serializers.CharField(max_length=1000, allow_blank=True, allow_null=True, required=False)
    #
    memo_no_id = serializers.CharField(source='budget_common.id', allow_blank=True, allow_null=True, required=False)

    # memo_no_value = serializers.CharField(source='budget_common.memo_no', allow_blank=True, allow_null=True, required=False)
    # fund_disburse_from_value = serializers.CharField(source='budget_common.fund_disburse_from', allow_blank=True, allow_null=True, required=False)
    # issue_date_value = serializers.DateField(source='budget_common.issue_date', allow_null=True, required=False)
    # financial_year_value = serializers.CharField(source='budget_common.financial_year', allow_blank=True, allow_null=True, required=False)
    # total_provision_value = serializers.FloatField(source='budget_common.total_provision', allow_null=True, required=False)
    # installment_no_value = serializers.CharField(source='budget_common.installment_no', allow_blank=True, allow_null=True, required=False)
    # subject_value = serializers.CharField(source='budget_common.subject', allow_blank=True, allow_null=True, required=False)

    class Meta:
        model = Budget
        fields = '__all__'


class OfficeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfficeType
        fields = '__all__'


class ExternalMemberSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', allow_null=True, allow_blank=True,
                                              required=False)
    committee_type_value = serializers.SerializerMethodField()
    # office_type_value = serializers.CharField(source='office_type.type', allow_blank=True, allow_null=True,
    #                                           required=False)
    # nominee_office_value = serializers.CharField(source='nominee_office.name', allow_blank=True, allow_null=True,
    #                                              required=False)
    # nominee_organization = serializers.CharField(source='nominee_office.organization', allow_blank=True,
    #                                              allow_null=True, required=False)
    # nominee_office_category = serializers.CharField(source='nominee_office.office_category', allow_blank=True,
    #                                                 allow_null=True, required=False)
    nominee_name = serializers.CharField(source='user.first_name', allow_null=True, required=False)
    nominee_office_name = serializers.CharField(source='user.profile.office.name', allow_null=True, required=False)
    nominee_gender = serializers.CharField(source='user.profile.gender', allow_null=True, required=False)
    nominee_nid = serializers.CharField(source='user.profile.nid', allow_null=True, required=False)
    nominee_date_of_birth = serializers.CharField(source='user.profile.date_of_birth', allow_null=True, required=False)
    nominee_designation = serializers.CharField(source='user.profile.designation.designation', allow_null=True,
                                                required=False)
    nominee_contact_no = serializers.CharField(source='user.profile.mobile_no', allow_null=True, required=False)
    nominee_office_id = serializers.CharField(source='user.profile.office.id', allow_null=True, required=False)
    nominee_designation_id = serializers.CharField(source='user.profile.designation.id', allow_null=True,
                                                   required=False)
    nominee_organization = serializers.CharField(source='user.profile.office.organization', allow_null=True,
                                                 required=False)
    nominee_office_category = serializers.CharField(source='user.profile.office.office_category', allow_null=True,
                                                    required=False)
    nominee_email = serializers.CharField(source='user.email', allow_null=True, required=False)
    invitee_office_name = serializers.CharField(source='invitee_office.name', allow_blank=True, allow_null=True,
                                                required=False)

    @staticmethod
    def get_committee_type_value(obj):
        return ", ".join(obj.committee_type.values_list('type', flat=True))

    class Meta:
        model = ExternalMember
        fields = '__all__'


class AnnouncementStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnnouncementStatus
        fields = '__all__'


class AnnouncementAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnnouncementAttachment
        fields = '__all__'


class AnnouncementSerializer(serializers.ModelSerializer):
    announcement_attachment = AnnouncementAttachmentSerializer(many=True, read_only=True)
    offices_seen_by = AnnouncementStatusSerializer(many=True, read_only=True)
    from_announcement_name = serializers.CharField(source='from_announcement.from_announcement', allow_null=True,
                                                   allow_blank=True,
                                                   read_only=True)
    office_categories = serializers.SerializerMethodField('get_office_categories_method')

    class Meta:
        model = Announcement
        fields = '__all__'
        read_only_fields = ['created_by']

    @classmethod
    def get_office_categories_method(cls, instance):
        all_offices = instance.office.all()
        categories =[]
        short_codes = ''
        for office in all_offices:
            category = office.office_category
            if category in categories:
                continue
            categories.append(category)
            if category == 'ZILA PARISHAD OFFICES':
                short_codes += 'ZP,'
                continue
            if category == 'UPAZILA PARISHAD OFFICES':
                short_codes += 'UZP,'
                continue
            if category == 'PAURASHAVA OFFICES':
                short_codes += 'PS,'
                continue
            if category == 'CITY CORPORATION OFFICES':
                short_codes += 'CC,'
                continue
            if category == 'CE Office (HQ)':
                short_codes += 'CE,'
                continue
            if category == 'Additional Chief Engineer Office (HQ)':
                short_codes += 'ACE (HQ),'
                continue
            if category == 'SE Office (HQ)':
                short_codes += 'SE (HQ),'
                continue
            if category == 'Project Office (HQ)':
                short_codes += 'PD (HQ),'
                continue
            if category == 'Division Office (Field)':
                short_codes +='ACE (Div),'
                continue
            if category == 'Regional Office (Field)':
                short_codes+='SE (Region),'
                continue
            if category == 'District Office (Field)':
                short_codes += 'XEN (Dist),'
                continue
            if category == 'Upazila Engineer Office(Field)':
                short_codes += 'UE,'
                continue
            short_codes += category + ','
        return short_codes


class IssueTitleSerializer(serializers.ModelSerializer):
    category_name = serializers.StringRelatedField(source='get_category_display')

    class Meta:
        model = IssueTitle
        fields = '__all__'


class IssueCommentSerializer(serializers.ModelSerializer):
    commented_by = serializers.StringRelatedField(source='commented_by.get_full_name')
    commented_by_admin = serializers.SerializerMethodField()
    commented_by_id = serializers.StringRelatedField(source='commented_by.id')

    @staticmethod
    def get_commented_by_admin(obj):
        if 'issue_update' in obj.commented_by.profile.role.permission.values_list('code', flat=True):
            return True
        return False

    class Meta:
        model = IssueComment
        fields = '__all__'


class IssueAttachmentSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(source='created_by.get_full_name')

    class Meta:
        model = IssueAttachment
        fields = '__all__'


class IssueSerializer(DynamicFieldsModelSerializer, serializers.ModelSerializer):
    raised_by_name = serializers.StringRelatedField(source='raised_by.get_full_name')
    raised_by_office_name = serializers.StringRelatedField(source='raised_by.profile.office.name')
    last_modified_by_role = serializers.StringRelatedField(source='last_modified_by.profile.office.office_category')
    raised_by_email = serializers.SerializerMethodField()
    raised_by_phone = serializers.SerializerMethodField()
    title_name = serializers.StringRelatedField(source='title.title')
    category = serializers.StringRelatedField(source='title.category')
    category_name = serializers.StringRelatedField(source='title.get_category_display')
    action_name = serializers.SerializerMethodField()
    # attachment_name = serializers.SerializerMethodField()

    comments = IssueCommentSerializer(many=True, read_only=True)
    issue_attachment = IssueAttachmentSerializer(many=True, read_only=True)

    def get_action_name(self, obj):
        user_permissions = list(self.context['request'].user.profile.role.permission.values_list('code', flat=True))
        if 'issue_admin' in user_permissions:
            return obj.get_admin_end_action_display()
        else:
            return obj.get_user_end_action_display()

    # @staticmethod
    # def get_attachment_name(ob):
    #     if ob.attachment:
    #         return os.path.basename(ob.attachment.name)
    #     else:
    #         return ''

    @staticmethod
    def get_raised_by_email(ob):
        # return ob.raised_by.email + (
        #         ', ' + ob.raised_by.profile.personal_email) if ob.raised_by.profile.personal_email else ''
        return (ob.raised_by.email + ', ') if ob.raised_by.email else '' + ob.raised_by.profile.personal_email if \
            ob.raised_by.profile.personal_email else ''

    @staticmethod
    def get_raised_by_phone(ob):
        # return ""
        return (ob.raised_by.profile.official_mobile_no + ', ') if ob.raised_by.profile.official_mobile_no else \
            '' + ob.raised_by.profile.mobile_no if ob.raised_by.profile.mobile_no else ''

    def create(self, validated_data):
        created_issue = Issue.objects.create(**validated_data)
        re_attachment = self.context['request'].data.get('attachment')
        re_attachment_type = self.context['request'].data.get('attachment_type')
        if re_attachment:
            attachment = IssueAttachment(attachment=re_attachment, created_by=self.context['request'].user,
                                         issue=created_issue)
            if re_attachment_type:
                attachment.attachment_type = re_attachment_type
            attachment.save()
        return created_issue

    class Meta:
        model = Issue
        fields = '__all__'


class TrainingNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingName
        fields = '__all__'


class TrainingCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingCategory
        fields = '__all__'


class BatchNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = BatchNumber
        fields = '__all__'


class FromAnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = FromAnnouncement
        fields = '__all__'


class PublicationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicationType
        fields = '__all__'


class AuditTrailSerializer(serializers.ModelSerializer):
    user_login_id = serializers.CharField(source='user.email', allow_null=True, allow_blank=True, required=False)
    user_name = serializers.CharField(source='user.first_name', allow_null=True, allow_blank=True, required=False)
    user_office_name = serializers.CharField(source='user.profile.office.name', allow_null=True,
                                             allow_blank=True, required=False)

    class Meta:
        model = AuditTrail
        fields = '__all__'


class HomePageImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomePageImage
        fields = '__all__'


class HomePageWritingSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomepageWriting
        fields = '__all__'


class ImportantLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImportantLinks
        fields = '__all__'


class ResponsiveBidderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResponsiveBidder
        fields = '__all__'


class MonthlyProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthlyProgress
        fields = '__all__'


class PaymentAmountVariationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentAmountVariation
        fields = '__all__'


class PaymentTimeVariationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTimeVariation
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    contract_amount = serializers.CharField(source='contract.contract_amount', allow_null=True, allow_blank=True,
                                            required=False)
    contract_id = serializers.CharField(source='contract.id', allow_null=True, allow_blank=True,
                                        required=False)
    monthly_progress = MonthlyProgressSerializer(many=True, read_only=True)
    payment_amount_variation = PaymentAmountVariationSerializer(many=True, read_only=True)
    payment_time_variation = PaymentTimeVariationSerializer(many=True, read_only=True)
    contract_signing_date = serializers.CharField(source='contract.contract_signing_date', allow_null=True,
                                                  allow_blank=True, required=False)

    def create(self, validated_data):
        with transaction.atomic():
            monthly_progress = json.loads(self.context['request'].data['monthly_progress'])
            payment = Payment.objects.create(**validated_data)
            months = len(monthly_progress.keys())
            for i in range(0, months):
                key = 'month' + str(i + 1)
                month = monthly_progress[key]
                MonthlyProgress.objects.create(payment=payment, **month)

            time_variation = json.loads(self.context['request'].data['time_variation'])
            time_variations = len(time_variation.keys())
            for i in range(0, time_variations):
                key = 'time_variation' + str(i + 1)
                var = time_variation[key]
                PaymentTimeVariation.objects.create(payment=payment, **var)

            amount_variation = json.loads(self.context['request'].data['amount_variation'])
            amount_variations = len(amount_variation.keys())
            for i in range(0, amount_variations):
                key = 'amount_variation' + str(i + 1)
                var = amount_variation[key]
                PaymentAmountVariation.objects.create(payment=payment, **var)
            return payment

    def update(self, instance, validated_data):
        with transaction.atomic():
            info = model_meta.get_field_info(instance)
            monthly_progress = json.loads(self.context['request'].data['monthly_progress'])
            current_progresses = []
            months = len(monthly_progress.keys())
            for i in range(0, months):
                key = 'month' + str(i + 1)
                progress_data = monthly_progress[key]
                if progress_data['progress_id'] and progress_data['progress_id'] != '' and progress_data[
                    'progress_id'] != 'null':
                    current_progresses.append(progress_data['progress_id'])
                    progress_instance = MonthlyProgress.objects.filter(id=progress_data['progress_id'])
                    progress_data.pop('progress_id')
                    progress_instance.update(**progress_data)
                else:
                    if progress_data['progress_id'] is not None:
                        progress_data.pop('progress_id')
                    new = MonthlyProgress.objects.create(payment=instance, **progress_data)
                    current_progresses.append(new.id)
            MonthlyProgress.objects.filter(~Q(id__in=current_progresses), payment=instance).delete()

            time_variation = json.loads(self.context['request'].data['time_variation'])
            for key in time_variation:
                var = time_variation[key]
                PaymentTimeVariation.objects.create(payment=instance, **var)

            amount_variation = json.loads(self.context['request'].data['amount_variation'])
            for key in amount_variation:
                var = amount_variation[key]
                PaymentAmountVariation.objects.create(payment=instance, **var)

            for attr, value in validated_data.items():
                if attr in info.relations and info.relations[attr].to_many:
                    field = getattr(instance, attr)
                    field.set(value)
                else:
                    setattr(instance, attr, value)
            instance.save()
            return instance

    class Meta:
        model = Payment
        fields = '__all__'


class MonthlyProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthlyProgress
        fields = '__all__'


class ExtOrgSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtOrg
        fields = '__all__'


class InviteeOfficeSerializer(serializers.ModelSerializer):
    external_organization_name = serializers.CharField(source='external_organization.name', allow_null=True,
                                                       allow_blank=True, required=False)

    class Meta:
        model = InviteeOffice
        fields = '__all__'


class ColumnCustomizationSerializer(serializers.ModelSerializer):
    columns = serializers.ListField(
        child=serializers.IntegerField()
    )

    class Meta:
        model = ColumnCustomization
        fields = '__all__'


class PasswordRequestSerializer(serializers.ModelSerializer):
    number_of_requests = serializers.SerializerMethodField()
    organization = serializers.CharField(source='user.profile.office.organization', allow_null=True, allow_blank=True,
                                         required=False)
    office_category = serializers.CharField(source='user.profile.office.office_category', allow_null=True,
                                            allow_blank=True, required=False)
    division = serializers.CharField(source='user.profile.office.division.name', allow_null=True,
                                     allow_blank=True, required=False)
    region = serializers.CharField(source='user.profile.office.region.name', allow_null=True,
                                   allow_blank=True, required=False)
    district = serializers.CharField(source='user.profile.office.district.name', allow_null=True,
                                     allow_blank=True, required=False)
    upazila = serializers.CharField(source='user.profile.office.upazila.name', allow_null=True,
                                    allow_blank=True, required=False)
    office_name = serializers.CharField(source='user.profile.office.name', allow_null=True, allow_blank=True,
                                        required=False)
    user_name = serializers.SerializerMethodField('get_user_actual_name')
    user_contact_no = serializers.SerializerMethodField('get_actual_user_contact_no')
    user_designation = serializers.CharField(source='user.profile.designation.designation', allow_null=True,
                                             allow_blank=True, required=False)

    @classmethod
    def get_actual_user_contact_no(cls, instance):
        user = User.objects.get(id=instance.user.id)
        if user.profile.nid is None or user.first_name is None or user.last_name is None:
            user = TemporaryOffice.objects.filter(blank_user_id=instance.user.id)
            if user:
                user = user[0].user.profile.mobile_no
                return user

        return instance.user.profile.mobile_no

    @classmethod
    def get_user_actual_name(cls, instance):

        user = User.objects.get(id=instance.user.id)
        if user.profile.nid is None or user.first_name is None or user.last_name is None:
            user = TemporaryOffice.objects.filter(blank_user_id=instance.user.id)
            if user:
                user = user[0].user.first_name
                return user

        return instance.user.first_name

    @staticmethod
    def get_number_of_requests(obj):
        return PasswordRequest.objects.filter(e_gp_id=obj.e_gp_id).count()

    class Meta:
        model = PasswordRequest
        fields = '__all__'


class RoleSerializer(serializers.ModelSerializer):
    permission_names = serializers.SerializerMethodField()

    @staticmethod
    def get_permission_names(obj):
        return obj.permission.values_list('name', flat=True)

    class Meta:
        model = Role
        fields = '__all__'


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'


class ExtMemberTransferHistorySerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.first_name', allow_null=True, allow_blank=True,
                                      required=False)
    transferred_office_name = serializers.CharField(source='transferred_office.name', allow_null=True, allow_blank=True,
                                                    required=False)
    new_designation_name = serializers.CharField(source='new_designation.designation', allow_blank=True,
                                                 allow_null=True,
                                                 required=False)

    class Meta:
        model = ExtMemberTransferHistory
        fields = '__all__'


class AdminUserSerializer(serializers.ModelSerializer):
    designation_name = serializers.CharField(source='designation.designation', allow_null=True, allow_blank=True,
                                             required=False)
    procurement_roles_list = serializers.SerializerMethodField()

    @staticmethod
    def get_procurement_roles_list(obj):
        return ', '.join(obj.procurement_roles.values_list('role', flat=True))

    class Meta:
        model = AdminUsers
        fields = '__all__'


class GovtUserSerializer(serializers.ModelSerializer):
    designation_name = serializers.CharField(source='designation.designation', allow_null=True, allow_blank=True,
                                             required=False)
    procurement_roles_list = serializers.SerializerMethodField()

    @staticmethod
    def get_procurement_roles_list(obj):
        return ', '.join(obj.procurement_roles.values_list('role', flat=True))

    class Meta:
        model = GovtUsers
        fields = '__all__'


class ExtMemberInclusionHistorySerializer(serializers.ModelSerializer):
    focal_designation_name = serializers.CharField(source='focal_designation.designation', allow_null=True,
                                                   allow_blank=True, required=False)
    # admin_users = AdminUserSerializer(many=True, read_only=True)
    govt_users = GovtUserSerializer(many=True, read_only=True)
    designation_name = serializers.CharField(source='designation.designation', allow_null=True,
                                             allow_blank=True, required=False)
    procurement_roles_list = serializers.SerializerMethodField()
    venue_name = serializers.CharField(source='venue.name', allow_null=True, allow_blank=True, required=False)

    @staticmethod
    def get_procurement_roles_list(obj):
        return ', '.join(obj.procurement_roles.values_list('role', flat=True))

    class Meta:
        model = ExtMemberInclusionHistory
        fields = '__all__'


class ExpiredLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpiredLink
        fields = '__all__'


class ProfileSerializer(serializers.ModelSerializer):
    designation_name = serializers.StringRelatedField(source='designation.designation')
    procurement_roles = serializers.StringRelatedField(many=True)
    procurement_roles_lgis = serializers.StringRelatedField(many=True)

    procurement_roles_egp_id = serializers.SerializerMethodField('get_procurement_roles_egp_user_id')
    procurement_roles_lgis_egp_id = serializers.SerializerMethodField('get_procurement_roles_lgis_egp_user_id')

    @classmethod
    def get_procurement_roles_egp_user_id(self, instance):
        roles = list(instance.procurement_roles.all().values_list('role', flat=True))

        if 'Organization Admin' in roles:
            return instance.e_gp_user_id_for_org_admin

        if 'PE Admin' in roles:
            return instance.e_gp_user_id_for_pe_admin

        return instance.e_gp_user_id_for_govt

    @classmethod
    def get_procurement_roles_lgis_egp_user_id(self, instance):
        roles = list(instance.procurement_roles_lgis.all().values_list('role', flat=True))

        if 'Organization Admin' in roles:
            return instance.e_gp_user_id_lgis_for_org_admin

        if 'PE Admin' in roles:
            return instance.e_gp_user_id_lgis_for_pe_admin

        return instance.e_gp_user_id_lgis_for_govt

    class Meta:
        model = Profile
        fields = (
            'id', 'designation', 'designation_name', 'procurement_roles', 'procurement_roles_lgis',
            'procurement_roles_egp_id', 'procurement_roles_lgis_egp_id')
        # fields='__all__'
