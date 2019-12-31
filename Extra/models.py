# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import User
from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField

# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------- User Profile ---------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
from django.forms import forms


class Permission(models.Model):
    name = models.CharField(max_length=50, blank=False,
                            null=False, unique=True)
    code = models.CharField(max_length=50, blank=False, unique=True)
    active = models.BooleanField(null=False, blank=False, default=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return '{}'.format(self.name)


class Role(models.Model):
    name = models.CharField(max_length=50, blank=False,
                            null=False, unique=True)
    code = models.CharField(max_length=50, blank=False, unique=True)
    priority = models.IntegerField(default=1)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    permission = models.ManyToManyField(Permission, related_name='permissions')

    def __str__(self):
        return self.name


class UserProfileManager(BaseUserManager):
    """Helps Django work with our custom user model."""
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

    def create_user(self, email, username, password=None):
        """Creates a new user profile."""
        if not email:
            raise ValueError('Users must have an email addresss.')

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, )

        user.set_password(password)
        user.save(using=self._db)
        print('cr')
        return user

    def create_superuser(self, email, username, password):
        """Creates and saves a new superuser with given details."""
        print('csr')
        user = self.create_user(email, username, password)

        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user


# ----------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------- Procurement Role -------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class ProcurementRole(models.Model):
    role = models.CharField(max_length=30, null=True, blank=True)
    weight = models.IntegerField(default=0)
    description = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.role


# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------ Designation ---------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class Designation(models.Model):
    designation = models.CharField(max_length=50, null=True, blank=True, unique=True)
    short_form = models.CharField(max_length=20, null=True, blank=True)
    weight = models.IntegerField(default=0)
    description = models.CharField(max_length=255, null=True, blank=True)
    office_categories = ArrayField(models.CharField(max_length=100), null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.designation


# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------- Division -----------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class Division(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.name


# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------- City Corporation ---------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class CityCorporation(models.Model):
    name = models.CharField(max_length=50, unique=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.name


# ----------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------- Region ------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class Region(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    division = models.ForeignKey(Division, on_delete=models.PROTECT)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.name


# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------- District -----------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class District(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    region = models.ForeignKey(Region, on_delete=models.PROTECT)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.name


# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------- Upazila ------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class Upazila(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=255, null=True, blank=True)
    district = models.ForeignKey(District, on_delete=models.PROTECT)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.name


# name should be Venue !!!! Danger Don't change this
# ----------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------- Resource Center --------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class ResourceCenter(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.name


# ----------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------- Office ------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class Office(models.Model):
    name = models.CharField(max_length=200)
    organization = models.CharField(max_length=20)
    office_category = models.CharField(max_length=50)
    pourashava_class = models.CharField(max_length=50, blank=True, null=True)
    division = models.ForeignKey(Division, on_delete=models.PROTECT, null=True, blank=True)
    city_corporation = models.ForeignKey(CityCorporation, on_delete=models.CASCADE, blank=True, null=True)
    region = models.ForeignKey(Region, on_delete=models.PROTECT, blank=True, null=True)
    district = models.ForeignKey(District, on_delete=models.PROTECT, blank=True, null=True)
    upazila = models.ForeignKey(Upazila, on_delete=models.PROTECT, blank=True, null=True)
    post_code = models.CharField(max_length=20, blank=True, null=True)
    latt = models.FloatField(null=True, blank=True)
    long = models.FloatField(null=True, blank=True)
    address = models.CharField(max_length=500, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone_no = models.CharField(max_length=20, blank=True, null=True)
    fax_no = models.CharField(max_length=20, blank=True, null=True)
    website_link = models.CharField(max_length=200, blank=True, null=True)
    profile_pic = models.FileField(upload_to='office-profile/', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.name



# ----------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------- Tender ------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# class Tender(models.Model):
#     tender_id = models.IntegerField(unique=True, blank=True, null=True)
#     package_no = models.CharField(max_length=100, blank=True, null=True)
#     status = models.CharField(max_length=100, default="Live")
#     financial_year = models.CharField(max_length=100, blank=True, null=True)
#     online_offline = models.CharField(max_length=100, blank=True, null=True)
#     office = models.ForeignKey(Office, on_delete=models.PROTECT, blank=True, null=True)
#     development_revenue = models.CharField(max_length=100, blank=True, null=True)
#     estimated_amount = models.IntegerField(default=0)
#     contract_amount = models.IntegerField(default=0)
#     document = models.FileField(upload_to='tenders/', null=True, blank=True)
#
#     created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
#     updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)
#
#     def __str__(self):
#         return '%s' % self.tender_id


# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------ Inventory Type Category ---------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class InventoryTypeCategory(models.Model):
    category = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.category


# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------ Inventory Type ----------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class InventoryType(models.Model):
    type = models.CharField(max_length=100, blank=True, null=True)
    weight = models.IntegerField(default=0)
    type_category = models.ForeignKey(InventoryTypeCategory, on_delete=models.PROTECT, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.type


# ----------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------- Source -----------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class Source(models.Model):
    source = models.CharField(max_length=150, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.source


# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------- Package No--------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class PackageNo(models.Model):
    package_no = models.CharField(max_length=200)
    office = models.ManyToManyField(Office)
    source = models.ForeignKey(Source, on_delete=models.PROTECT, null=True, blank=True)
    document = models.FileField(upload_to='package-specification/', null=True, blank=True)
    document_name = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.package_no


# ----------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------- Supplier ----------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class Supplier(models.Model):
    supplier_name = models.CharField(max_length=150, blank=True, null=True)
    supplier_mobile_no = models.CharField(max_length=30, blank=True, null=True)
    supplier_email_no = models.EmailField(null=True, blank=True)
    supplier_district = models.ForeignKey(District, on_delete=models.PROTECT, null=True, blank=True)
    supplier_address = models.CharField(max_length=400, null=True, blank=True)

    package_no = models.ForeignKey(PackageNo, on_delete=models.PROTECT, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.supplier_name


# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------- SupportCenter Address ----------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class SupportCenter(models.Model):
    support_center_contact_person = models.CharField(max_length=100, blank=True, null=True)
    support_center_name = models.CharField(max_length=100, blank=True, null=True)
    support_mobile_no = models.CharField(max_length=30, blank=True, null=True)
    support_phone_no = models.CharField(max_length=20, blank=True, null=True)
    support_email_no = models.EmailField(null=True, blank=True)
    support_center_address = models.CharField(max_length=400, null=True, blank=True)
    support_center_district = models.ForeignKey(District, on_delete=models.PROTECT, null=True, blank=True)

    package_no = models.ForeignKey(PackageNo, on_delete=models.PROTECT, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.support_center_address


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------- Devices ---------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class Devices(models.Model):
    type = models.ForeignKey(InventoryType, on_delete=models.PROTECT)
    brand_name = models.CharField(max_length=100, blank=True, null=True)
    model_no = models.CharField(max_length=100, blank=True, null=True)
    validity = models.DateField(blank=True, null=True)

    package_no = models.ForeignKey(PackageNo, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.type


#     supplier information
# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------- Inventory Status ------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class InventoryStatus(models.Model):
    status = models.CharField(max_length=100, blank=True, null=True)
    weight = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.status


# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------- Inventory ----------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class Inventory(models.Model):
    item = models.CharField(max_length=150, blank=True, null=True)  # previous fields
    brand_name = models.CharField(max_length=150, blank=True, null=True)  # previous fields
    model_no = models.CharField(max_length=150, blank=True, null=True)  # previous fields
    serial_no = models.CharField(max_length=150, blank=True, null=True)
    asset_no = models.CharField(max_length=50, blank=True, null=True)
    date_of_delivery = models.DateField(blank=True, null=True)
    validity = models.DateField(blank=True, null=True)  # previous fields
    supplied_quantity = models.IntegerField(blank=True, null=True)
    status_description = models.CharField(max_length=500, blank=True, null=True)
    comment = models.CharField(max_length=500, blank=True, null=True)
    package_number = models.CharField(max_length=30, null=True, blank=True)  # package no is actually package type, only
    # available for local purchase package type

    # Supplier
    # supplier_name = models.CharField(max_length=150, blank=True, null=True)  # previous fields
    # supplier_mobile_no = models.CharField(max_length=30, blank=True, null=True)  # previous fields
    # supplier_email_no = models.EmailField(null=True, blank=True)  # previous fields
    # support_mobile_no = models.CharField(max_length=30, blank=True, null=True)  # previous fields
    # support_email_no = models.EmailField(null=True, blank=True)  # previous fields
    # supplier_address = models.CharField(max_length=400, null=True, blank=True)  # previous fields
    # support_center_address = models.CharField(max_length=400, null=True, blank=True)  # previous fields

    # organization = models.CharField(max_length=20)
    # office_category = models.CharField(max_length=50)
    # Foreign
    # district = models.ForeignKey(District, null=True, blank=True)
    office = models.ForeignKey(Office, on_delete=models.PROTECT)
    status = models.ForeignKey(InventoryStatus, on_delete=models.PROTECT, null=True, blank=True)
    type = models.ForeignKey(InventoryType, on_delete=models.PROTECT, null=True, blank=True)
    package_no = models.ForeignKey(PackageNo, on_delete=models.PROTECT, null=True, blank=True)
    source = models.ForeignKey(Source, on_delete=models.PROTECT, null=True, blank=True)
    device = models.ForeignKey(Devices, on_delete=models.PROTECT, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.item


# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------- Inventory Files -------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class InventoryFileType(models.Model):
    file_type = models.CharField(max_length=300, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)


# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------- Inventory Files -------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class InventoryFile(models.Model):
    document = models.FileField(upload_to='inventories/', null=True, blank=True)
    file_name = models.CharField(max_length=300, blank=True, null=True)
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)


# ----------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------- Profile -----------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class Profile(models.Model):
    BOOL_CHOICES = ((True, 'Yes'), (False, 'No'))
    personal_email = models.EmailField(blank=True, null=True)
    official_email = models.EmailField(blank=True, null=True)
    mobile_no = models.CharField(max_length=30, null=True, blank=True)  # personal_mobile_no
    official_mobile_no = models.CharField(max_length=30, null=True, blank=True)

    # e_gp_user_id
    e_gp_user_id = models.CharField(max_length=100, null=True, blank=True)  # this one not needed
    e_gp_user_id_lgis = models.CharField(max_length=100, null=True, blank=True)  # this one not needed
    e_gp_user_id_for_govt = models.EmailField(null=True, blank=True)
    e_gp_user_id_lgis_for_govt = models.EmailField(null=True, blank=True)
    e_gp_user_id_for_org_admin = models.EmailField(null=True, blank=True)
    e_gp_user_id_lgis_for_org_admin = models.EmailField(null=True, blank=True)
    e_gp_user_id_for_pe_admin = models.EmailField(null=True, blank=True)
    e_gp_user_id_lgis_for_pe_admin = models.EmailField(null=True, blank=True)
    # e_gp_user_id1 = models.ManyToManyField('EGPUserID', on_delete=models.PROTECT, null=True, blank=True)
    # e_gp_user_id_lgis1 = models.ManyToManyField('EGPUserID', related_name='e_gp_user_id_lgis',
    # on_delete=models.PROTECT, null=True, blank=True)
    floating = models.BooleanField(default=False)

    nid = models.CharField(max_length=50, null=True, blank=True, unique=True)
    bengali_name = models.CharField(max_length=50, null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    image_name = models.CharField(max_length=100, null=True, blank=True)
    PPR_training = models.NullBooleanField(choices=BOOL_CHOICES, blank=True, null=True, default=None)
    trainer = models.BooleanField(default=False)
    training_under = models.ForeignKey(Office, on_delete=models.CASCADE, null=True, blank=True, related_name='training_under')

    gender = models.CharField(max_length=50, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    is_temp_office_assign = models.BooleanField(default=False)

    procurement_roles = models.ManyToManyField(ProcurementRole)
    procurement_roles_lgis = models.ManyToManyField(ProcurementRole, related_name='procurement_roles_lgis')
    designation = models.ForeignKey(Designation, on_delete=models.PROTECT, null=True, blank=True)
    office = models.ForeignKey(Office, on_delete=models.PROTECT, null=True, blank=True)

    role = models.ForeignKey(
        Role, on_delete=models.PROTECT, null=False, blank=False, related_name='user', default=5)  # set default to general user

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.id


# ----------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------- User -------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField('email address', unique=True, null=True, blank=True)  # !!! warning: don't change
                                                                                    #  unique=true
    username = models.CharField(max_length=20, unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    stage = models.SmallIntegerField(default=0)
    password_reset = models.BooleanField(default=False)
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, null=True, blank=True)

    objects = UserProfileManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def __str__(self):
        return '%s' % self.id

# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------- TemporaryOffice ----------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

class TemporaryOffice(models.Model):
    office = models.ForeignKey(Office, on_delete=models.CASCADE, null=False, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    blank_user_id= models.CharField(max_length=100 ,null=True, blank=True)
    designation = models.ForeignKey(Designation, on_delete=models.PROTECT, null=True, blank=True)
    official_mobile_no = models.CharField(max_length=30, null=True, blank=True)
    official_email = models.EmailField(blank=True, null=True)

    # e_gp_user_id
    e_gp_user_id = models.CharField(max_length=100, null=True, blank=True)  # this one not needed
    e_gp_user_id_lgis = models.CharField(max_length=100, null=True, blank=True)  # this one not needed
    e_gp_user_id_for_govt = models.EmailField(null=True, blank=True)
    e_gp_user_id_lgis_for_govt = models.EmailField(null=True, blank=True)
    e_gp_user_id_for_org_admin = models.EmailField(null=True, blank=True)
    e_gp_user_id_lgis_for_org_admin = models.EmailField(null=True, blank=True)
    e_gp_user_id_for_pe_admin = models.EmailField(null=True, blank=True)
    e_gp_user_id_lgis_for_pe_admin = models.EmailField(null=True, blank=True)

    floating = models.BooleanField(default=False)

    procurement_roles = models.ManyToManyField(ProcurementRole)
    procurement_roles_lgis = models.ManyToManyField(ProcurementRole, related_name='temp_procurement_roles_lgis')

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)


# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------- EGPUserID ----------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# class EGPUserID(models.Model):
#     e_gp_user_id = models.CharField(max_length=100, null=True, blank=True)
#
#     created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
#     updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)
#
#     def __str__(self):
#         return '%s' % self.e_gp_user_id


# ----------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------- Publication -------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class Publication(models.Model):
    TYPE_CHOICES = (('Folder', 'Folder'), ('File', 'File'))
    HOMEPAGE_CHOICES = ((1, 'HOMEPAGE'), (0, 'Other'))
    title = models.CharField(max_length=150)
    # type = models.CharField(max_length=50)
    type = models.ForeignKey('PublicationType', on_delete=models.PROTECT, null=True, blank=True)
    publish_date = models.DateField(blank=True, null=True)
    document = models.FileField(upload_to='publications/', null=True, blank=True)
    for_homepage = models.SmallIntegerField(choices=HOMEPAGE_CHOICES, default=0)
    genre = models.CharField(max_length=20, choices=TYPE_CHOICES, default='File')
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)
    office = models.ManyToManyField(Office, related_name='publication_office', blank=True, default=401002)
    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.title


# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------- Gallery ---------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class Gallery(models.Model):
    TYPE_CHOICES = (('Folder', 'Folder'), ('File', 'File'))
    HOMEPAGE_CHOICES = ((1, 'HOMEPAGE'), (0, 'Other'))
    title = models.CharField(max_length=300, null=True, blank=True)
    file = models.FileField(upload_to='gallery/', null=True, blank=True)
    for_homepage = models.SmallIntegerField(choices=HOMEPAGE_CHOICES, default=0)
    date = models.DateField(null=True, blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='File')
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.title


# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------ User Multiple Assign History ----------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class MultipleAssignHistory(models.Model):
    APPROVED_STATUS = (
        (0, 'pending'),
        (1, 'approved'),
        (2, 'rejected'),
        (3, 'rollback')
    )
    STATUS = (
        (0, 'promotion'),
        (1, 'multiassigned')
    )
    TYPE = (
        (0, 'to'),
        (1, 'from')
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    multiassign_blank_user = models.ForeignKey(User, related_name='multiassign_blank_user', on_delete=models.CASCADE, null=True, blank=True)
    multiassign_floating_user = models.ForeignKey(User, related_name='multiassign_floating_user', on_delete=models.CASCADE, null=True,
                                      blank=True)  # for only transfer from
    assigned_office = models.ForeignKey(Office, related_name='assigned_office', on_delete=models.CASCADE,
                                           blank=True, null=True)
    new_designation = models.ForeignKey(Designation, on_delete=models.CASCADE, null=True, blank=True)
    previous_official_info = JSONField(blank=True, null=True)  # transferred users' official info
    previous_personal_info = JSONField(blank=True, null=True)  # transferred users' personal info

    # transfer related details
    multiassign_memo_no = models.CharField(max_length=150, null=True, blank=True)
    multiassign_order = models.FileField(upload_to='multiassign', null=True, blank=True)
    charge_takeover_date = models.DateField(null=True, blank=True)
    charge_handover_date = models.DateField(null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)

    approved_status = models.SmallIntegerField(choices=APPROVED_STATUS, default=0)
    status = models.SmallIntegerField(choices=STATUS, default=1)
    multiassign_type = models.SmallIntegerField(choices=TYPE, default=0)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.user.id


# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------ Transfer History ----------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------


class TransferHistory(models.Model):
    APPROVED_STATUS = (
        (0, 'pending'),
        (1, 'approved'),
        (2, 'rejected'),
        (3, 'rollback')
    )
    STATUS = (
        (0, 'promotion'),
        (1, 'transfer')
    )
    TYPE = (
        (0, 'to'),
        (1, 'from')
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    blank_user = models.ForeignKey(User, related_name='blank_user', on_delete=models.CASCADE, null=True, blank=True)
    floating_user = models.ForeignKey(User, related_name='floating_user', on_delete=models.CASCADE, null=True,
                                      blank=True)  # for only transfer from
    transferred_office = models.ForeignKey(Office, related_name='transferred_office', on_delete=models.CASCADE,
                                           blank=True, null=True)
    new_designation = models.ForeignKey(Designation, on_delete=models.CASCADE, null=True, blank=True)
    previous_official_info = JSONField(blank=True, null=True)  # transferred users' official info
    previous_personal_info = JSONField(blank=True, null=True)  # transferred users' personal info

    # transfer related details
    transfer_memo_no = models.CharField(max_length=150, null=True, blank=True)
    transfer_order = models.FileField(upload_to='transfer', null=True, blank=True)
    charge_takeover_date = models.DateField(null=True, blank=True)
    charge_handover_date = models.DateField(null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)

    approved_status = models.SmallIntegerField(choices=APPROVED_STATUS, default=0)
    status = models.SmallIntegerField(choices=STATUS, default=1)
    transfer_type = models.SmallIntegerField(choices=TYPE, default=0)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.user.id



# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------ BudgetType ----------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class BudgetType(models.Model):
    type = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.type


# ----------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------- Procurement Nature ------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class ProcurementNature(models.Model):
    nature = models.CharField(max_length=100, unique=True)
    weight = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.nature


# ----------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------- Committee Type ---------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

class CommitteeType(models.Model):
    type = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.type



# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------ Office Type ---------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class OfficeType(models.Model):
    type = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.type


# ----------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------- TypeOfEmergency ------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class TypeOfEmergency(models.Model):
    type = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.type


# ----------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------- ProcMethod ------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class ProcMethod(models.Model):
    method = models.CharField(max_length=100, unique=True)
    weight = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.method


# ----------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------- ProcType ------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class ProcType(models.Model):
    type = models.CharField(max_length=100, unique=True)
    weight = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.type


# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------- Training Funded by ----------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class FundedBy(models.Model):
    funded_by = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.funded_by


# ----------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------- SourceOfFund ------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class SourceOfFund(models.Model):
    source = models.CharField(max_length=100, unique=True)
    weight = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.source


# ----------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------- FundDisburseFrom -------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class FundDisburseFrom(models.Model):
    source = models.CharField(max_length=100, unique=True)
    weight = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.source


# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------- Project ------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class Project(models.Model):
    name = models.CharField(max_length=250, null=True, blank=True)
    full_name = models.CharField(max_length=100, null=True, blank=True)
    cost = models.FloatField(default=0.0, null=True, blank=True)
    code = models.IntegerField(null=True, blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    source_of_fund = models.ManyToManyField(SourceOfFund, related_name='project_fund', blank=True)
    director_name = models.CharField(max_length=150, blank=True, null=True)
    development_partner = models.ForeignKey(FundedBy, on_delete=models.PROTECT, blank=True, null=True)
    floor_no = models.CharField(max_length=30, blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    phone_no = models.CharField(max_length=20, blank=True, null=True)
    mobile_no = models.CharField(max_length=20, blank=True, null=True)
    fax_no = models.CharField(max_length=20, blank=True, null=True)
    intercom = models.CharField(max_length=20, blank=True, null=True)
    ip_phone = models.CharField(max_length=20, blank=True, null=True)
    official_email = models.EmailField(null=True, blank=True)

    district = models.ManyToManyField(District, related_name='project_district', blank=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.name
# ----------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------- ApprovingAuthority -----------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------


class ApprovingAuthority(models.Model):
    authority = models.CharField(max_length=100, unique=True)
    weight = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.authority


# ----------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------- ContractStatus -----------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class ContractStatus(models.Model):
    status = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.status


# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------- APP ----------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class APP(models.Model):
    type = models.CharField(max_length=100, null=True, blank=True)
    app_id = models.CharField(null=True, blank=True, max_length=50, unique=True)
    status = models.CharField(null=True, blank=True, max_length=50, default="Pending")
    financial_year = models.CharField(max_length=100, blank=True, null=True)

    budget_type = models.ForeignKey(BudgetType, on_delete=models.PROTECT, blank=True, null=True)
    source_of_fund = models.ForeignKey(SourceOfFund, on_delete=models.PROTECT, blank=True, null=True)  # del
    package_no = models.CharField(max_length=100, null=True, blank=True, default=0)
    approval_date = models.DateField(null=True, blank=True)
    no_of_package = models.IntegerField(null=True, blank=True, default=0)

    # proc_nature = models.ForeignKey(ProcurementNature, on_delete=models.PROTECT, blank=True, null=True) #del
    # type_of_emergency = models.ForeignKey(TypeOfEmergency, on_delete=models.PROTECT, blank=True, null=True) #del
    office = models.ForeignKey(Office, on_delete=models.PROTECT, blank=True, null=True)
    project = models.ForeignKey(Project, on_delete=models.PROTECT, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.app_id


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------- Package --------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class Package(models.Model):
    app_cost = models.FloatField(blank=True, null=True)
    package_no = models.CharField(max_length=100, null=True, blank=True, unique=True)
    package_description = models.CharField(max_length=500, null=True, blank=True)

    lot_no = models.IntegerField(null=True, blank=True, default=0)
    proc_nature = models.ForeignKey(ProcurementNature, on_delete=models.PROTECT, blank=True, null=True)  # del
    type_of_emergency = models.ForeignKey(TypeOfEmergency, on_delete=models.PROTECT, blank=True, null=True)  # del
    approving_authority = models.ForeignKey(ApprovingAuthority, on_delete=models.PROTECT, blank=True, null=True)
    proc_method = models.ForeignKey(ProcMethod, on_delete=models.PROTECT, blank=True, null=True)  # del
    proc_type = models.ForeignKey(ProcType, on_delete=models.PROTECT, blank=True, null=True)  # del

    # lot_description = models.CharField(max_length=500, null=True, blank=True)
    # approval_date = models.DateField(null=True, blank=True)
    # proc_method = models.ForeignKey(ProcMethod, on_delete=models.PROTECT, blank=True, null=True)
    # proc_type = models.ForeignKey(ProcType, on_delete=models.PROTECT, blank=True, null=True)
    # source_of_fund = models.ForeignKey(SourceOfFund, on_delete=models.PROTECT, blank=True, null=True)
    status = models.CharField(null=True, blank=True, max_length=50, default="Pending")
    approval_date = models.DateField(null=True, blank=True)

    app_id = models.ForeignKey(APP, on_delete=models.PROTECT, blank=True, null=True)
    office = models.ForeignKey(Office, on_delete=models.PROTECT, blank=True, null=True)  # this field is redundant

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.package_no


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------- Lot No ---------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class Lot(models.Model):
    lot_description = models.CharField(max_length=500, null=True, blank=True)
    cost = models.FloatField(null=True, blank=True)

    # approval_date = models.DateField(null=True, blank=True) #del
    # proc_method = models.ForeignKey(ProcMethod, on_delete=models.PROTECT, blank=True, null=True) #del
    # proc_type = models.ForeignKey(ProcType, on_delete=models.PROTECT, blank=True, null=True) #del
    # source_of_fund = models.ForeignKey(SourceOfFund, on_delete=models.PROTECT, blank=True, null=True) #del

    office = models.ForeignKey(Office, on_delete=models.PROTECT, blank=True, null=True)
    package_no = models.ForeignKey(Package, related_name='lots', on_delete=models.PROTECT, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.lot_description


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------- Tender ---------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class Tender(models.Model):
    tender_id = models.IntegerField(null=True, blank=True, unique=True)
    publication_date = models.DateField(null=True, blank=True)
    closing_date = models.DateField(null=True, blank=True)
    approval_date = models.DateField(null=True, blank=True)
    tender_validity = models.IntegerField(null=True, blank=True)
    no_of_tender_doc_sold = models.IntegerField(null=True, blank=True)
    no_of_tender_doc_received = models.IntegerField(null=True, blank=True)
    no_of_responsive_tenderer = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=True)  # auto generated

    tender_status = models.CharField(max_length=100, null=True,
                                     blank=True)  # from drop down -> this is now just redundant field
    cancel_status = models.BooleanField(default=False)  # from cancel checkbox -> this is also a redundant field

    save_status = models.BooleanField(default=False)  # redundant field
    estimated_amount = models.IntegerField(default=0)  # redundant field

    # lot = models.ForeignKey(Lot, on_delete=models.PROTECT, blank=True, null=True)
    package = models.ForeignKey(Package, on_delete=models.PROTECT, blank=True, null=True)
    approving_authority = models.ForeignKey(ApprovingAuthority, on_delete=models.PROTECT, blank=True, null=True)
    office = models.ForeignKey(Office, on_delete=models.PROTECT, blank=True, null=True)  # this field is redundant
    previous_tender = models.IntegerField(null=True, blank=True)
    # previous_tender = models.ForeignKey('Tender', on_delete=models.PROTECT, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.tender_id

# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------- New Contract ---------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------Responsive Bidder------------------------------------------------------


class ResponsiveBidder(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)


class PublicationType(models.Model):
    type = models.CharField(max_length=100, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)


class NewContract(models.Model):
    contract_id = models.IntegerField(null=True, blank=True, unique=True)
    # NOA issue status
    noa_issuing_date = models.DateField(null=True, blank=True)
    responsive_bidder = models.CharField(max_length=100, null=True, blank=True)
    # responsive_bidder = models.ForeignKey(ResponsiveBidder, on_delete=models.PROTECT, null=True, blank=True)
    contract_signing_date = models.DateField(null=True, blank=True)
    contract_amount = models.FloatField(null=True, blank=True)

    # Contract status
    contractor_name = models.CharField(max_length=100, null=True, blank=True)
    tender_type = models.CharField(max_length=100, null=True, blank=True)
    no_of_firm = models.IntegerField(default=1)
    lead_firm_id = models.ForeignKey('Firm', on_delete=models.CASCADE, null=True, blank=True)
    document = models.FileField(upload_to='tenders/', null=True, blank=True)

    tender = models.ForeignKey(Tender, on_delete=models.PROTECT, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.id

# ----------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------- Tender Cost -------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------


class TenderCost(models.Model):
    cost = models.FloatField(null=True, blank=True)
    tender = models.ForeignKey(Tender, on_delete=models.PROTECT, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.cost


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------- Firm ---------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class Firm(models.Model):
    contractor_e_gp_id = models.CharField(max_length=100, null=True, blank=True)
    contractor_tin = models.CharField(max_length=100, null=True, blank=True)
    name_of_firm = models.CharField(max_length=500, null=True, blank=True)
    share = models.CharField(max_length=50, null=True, blank=True)

    contract = models.ForeignKey(NewContract, related_name='firms', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return '%s' % self.contractor_e_gp_id


# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------- Contract --------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class Contract(models.Model):
    physical_progress = models.FloatField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    completion_date = models.DateField(null=True, blank=True)
    actual_completion_date = models.DateField(null=True, blank=True)
    revise_contract_amount = models.FloatField(null=True, blank=True)
    amount_paid = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=True)

    tender_id = models.ForeignKey(Tender, on_delete=models.PROTECT, blank=True, null=True)
    # status = models.ForeignKey(ContractStatus, on_delete=models.PROTECT, blank=True, null=True)
    office = models.ForeignKey(Office, on_delete=models.PROTECT, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.tender_id


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------- Contract Payment -----------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class ContractPayment(models.Model):
    payment_date = models.DateField(null=True, blank=True)
    amount_paid = models.FloatField(null=True, blank=True)

    contract = models.ForeignKey(Contract, related_name='contract_payment', on_delete=models.PROTECT, blank=True,
                                 null=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.amount_paid


# ----------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------- Budget Common -----------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class BudgetCommon(models.Model):
    fund_disburse_from = models.CharField(max_length=100, null=True, blank=True)
    memo_no = models.CharField(max_length=500, unique=True)
    financial_year = models.CharField(max_length=100, null=True, blank=True)
    installment_no = models.CharField(max_length=300, null=True, blank=True)
    subject = models.CharField(max_length=1000, null=True, blank=True)
    issue_date = models.DateField(null=True, blank=True)
    total_provision = models.FloatField(default=0)
    released_budget = models.FloatField(default=0)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.memo_no


# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------ Budget --------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class Budget(models.Model):
    fund_disburse_from = models.CharField(max_length=100, null=True, blank=True)
    memo_no = models.CharField(max_length=500, null=True, blank=True)
    financial_year = models.CharField(max_length=100, null=True, blank=True)
    installment_no = models.CharField(max_length=300, null=True, blank=True)
    subject = models.CharField(max_length=1000, null=True, blank=True)
    comments = models.CharField(max_length=1000, null=True, blank=True)
    issue_date = models.DateField(null=True, blank=True)
    total_provision = models.FloatField(default=0)
    budget_amount = models.FloatField(default=0)
    type = models.CharField(max_length=20, null=True, blank=True)
    released_budget = models.FloatField(default=0)

    budget_common = models.ForeignKey(BudgetCommon, on_delete=models.PROTECT, blank=True, null=True)
    office = models.ForeignKey(Office, on_delete=models.PROTECT, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.budget_amount


# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------- Nominated Official ----------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class ExternalMember(models.Model):
    organization = models.ForeignKey("ExtOrg", on_delete=models.PROTECT, null=True, blank=True)
    invitee_office_bangla = models.CharField(max_length=200, blank=True, null=True)
    contact_no = models.CharField(max_length=20, blank=True, null=True)
    org_email = models.CharField(max_length=100, blank=True, null=True)
    committee_type = models.ManyToManyField(CommitteeType, blank=True, related_name='committee_type')
    invitee_name = models.CharField(max_length=200, blank=True, null=True)
    invitee_designation = models.CharField(max_length=50, blank=True, null=True)
    invitee_office = models.ForeignKey('InviteeOffice', blank=True, null=True)
    address = models.CharField(max_length=500, blank=True, null=True)

    # nominee_name = models.CharField(max_length=100, blank=True, null=True)
    # nominee_contact_no = models.CharField(max_length=20, blank=True, null=True)
    # nominee_designation = models.CharField(max_length=50, blank=True, null=True)
    # nominee_nid = models.CharField(max_length=30, blank=True, null=True)
    # nominee_gender = models.CharField(max_length=20, blank=True, null=True)
    # nominee_date_of_birth = models.DateField(null=True, blank=True)
    # nominee_id = models.IntegerField(null=True, blank=True)
    # nominee_office = models.ForeignKey(Office, on_delete=models.PROTECT, null=True, blank=True)

    memo = models.CharField(max_length=200, blank=True, null=True)
    comments = models.CharField(max_length=500, blank=True, null=True)
    office_order_date = models.DateField(null=True, blank=True)
    document = models.FileField(upload_to='external_member', null=True, blank=True)

    # ---------------------------- Foreign ----------------------------
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True) # nominee
    # office_type = models.ForeignKey(OfficeType, on_delete=models.PROTECT, null=True, blank=True)

    is_draft = models.IntegerField(default=0, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.user


# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------- From in Announcement --------------------------------------------------


class FromAnnouncement(models.Model):
    from_announcement = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.from_announcement

# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------- Announcement ---------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------


class Announcement(models.Model):
    DRAFT_STATUS = (
        (0, 'Draft'),
        (1, 'Not Draft'),
        (2, 'Deleted'),
    )
    TRAINING_STATUS = (
        (0, 'user generated'),
        (1, 'system generated'),
    )

    HOMEPAGE_STATUS = (
        (0, 'Not In Homepage'),
        (1, 'In Homepage'),
    )

    title = models.CharField(max_length=200, blank=False)
    description = models.TextField(blank=True)
    expired_date = models.DateTimeField(null=True, blank=True)
    issue_date = models.DateField(null=True, blank=True)
    draft = models.SmallIntegerField(choices=DRAFT_STATUS, default=1)
    weight = models.IntegerField(null=True, blank=True)
    for_homepage = models.SmallIntegerField(choices=HOMEPAGE_STATUS, default=0)
    from_announcement = models.ForeignKey(FromAnnouncement, on_delete=models.PROTECT, null=True, blank=True)

    # ---------------------------- Foreign ----------------------------
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    training_status = models.SmallIntegerField(choices=TRAINING_STATUS, default=0)
    office = models.ManyToManyField(Office, related_name='announcement_office', blank=True)
    # office_cc = models.ManyToManyField(Office, related_name='announcement_office_cc', blank=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.title

    def get_office_name(self):
        return ", ".join([single.name for single in self.office.all()])


class AnnouncementStatus(models.Model):
    # STATUS = (
    #     (0, 'Not Seen'),
    #     (1, 'Seen'),
    # )

    office = models.ForeignKey(Office, on_delete=models.CASCADE)
    announcement = models.ForeignKey(Announcement, related_name='offices_seen_by', on_delete=models.CASCADE)
    time = models.DateTimeField(null=True, blank=True)

    # status = models.SmallIntegerField(choices=STATUS, default=0)

    class Meta:
        unique_together = (("office", "announcement"),)


class AnnouncementAttachment(models.Model):
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name='announcement_attachment')
    attachment = models.FileField(upload_to='attachment', blank=True, null=True)
    attachment_name = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)


# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------- Issue Category --------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

class IssueTitle(models.Model):
    MODEL_CHOICES = (
        ('User', 'User'),
        ('Office', 'Office'),
        ('Inventory', 'Inventory'),
        ('APP', 'APP'),
        ('Package', 'Package'),
        ('Lot', 'Lot'),
        ('Tender', 'Tender'),
        ('Contract', 'Contract'),
        ('Other', 'Other'),
        ('Budget', 'Budget'),
        ('Training', 'Training')
    )
    title = models.CharField(max_length=500, blank=False, null=False)
    category = models.CharField(max_length=50, blank=False, null=False, default='Other', choices=MODEL_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.title


# --------------------------------------------------------------------------package--------------------------------------------
# ------------------------------------------------------ Issue ---------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

class Issue(models.Model):
    ADMIN_ISSUE_ACTION = (
        (0, ''),
        (1, 'Query Required'),
        (2, 'Hold'),
        (3, 'Solved')
    )
    USER_ISSUE_ACTION = (
        (1, 'Forward'),
        (2, 'Closed'),
    )
    # category = models.ForeignKey(IssueCategory, on_delete=models.PROTECT, related_name='issue_category')
    # model = models.CharField(max_length=50, blank=True, null=True, choices=MODEL_CHOICES)
    item_id = models.BigIntegerField(blank=True, null=True)
    title = models.ForeignKey(IssueTitle, on_delete=models.PROTECT, related_name='issue_title', blank=True, null=True)
    description = models.CharField(max_length=1000, null=False, blank=False)
    raised_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='issue_raised_by')
    # action = models.SmallIntegerField(choices=ISSUE_ACTION, default=1)
    user_end_action = models.SmallIntegerField(choices=USER_ISSUE_ACTION, default=1)
    admin_end_action = models.SmallIntegerField(choices=ADMIN_ISSUE_ACTION, default=0)
    seen_status = models.BooleanField(blank=False, null=False, default=False)
    seen_time1 = models.DateTimeField(blank=True, null=True)  # admin view time
    seen_time2 = models.DateTimeField(blank=True, null=True)  # other office view time
    other_title = models.CharField(max_length=200, null=True, blank=True)
    other_category = models.CharField(max_length=50, null=True, blank=True, default='Other')

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    last_modified_by = models.ForeignKey(User, null=False, blank=False, related_name='issue_modified_by')
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.title


class IssueComment(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.PROTECT, related_name='comments')
    commented_by = models.ForeignKey(User, on_delete=models.PROTECT)
    comment = models.CharField(max_length=1000)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.comment


class IssueAttachment(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.PROTECT, related_name='issue_attachment')
    attachment = models.FileField(upload_to='issue', blank=False, null=False)
    attachment_type = models.CharField(max_length=100, blank=True, null=True)

    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)


# ----------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------Training Name, Batch No------------------------------

class TrainingName(models.Model):
    training_name = models.CharField(max_length=200, blank=False, null=False)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.training_name


class TrainingCategory(models.Model):
    category = models.CharField(max_length=200, blank=False, null=False)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.category


class BatchNumber(models.Model):
    batch_no = models.IntegerField(blank=False, null=False)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.batch_no


# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------- Training Batch --------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class TrainingBatch(models.Model):
    CREATED_BY_STATUS = (
        (0, 'Admin'),
        (1, 'Local'),
        (2, 'System')
    )
    COMPLETED_STATUS = (
        (0, 'Draft'),
        (1, 'Finalized'),
        (2, 'Notified'),
        (3, 'completed'),
        (4, 'Notified and Finalized'),
        (5, 'Time out')
    )
    # DRAFT_STATUS = (
    #     (0, 'Final'),
    #     (1, 'Draft')
    # )

    organization = models.CharField(max_length=20, null=True, blank=True)
    training_category = models.CharField(max_length=100, null=True, blank=True)
    financial_year = models.CharField(max_length=30, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    no_of_participants = models.IntegerField(default=0)
    created_by_status = models.SmallIntegerField(choices=CREATED_BY_STATUS, default=0)
    office = models.ForeignKey(Office, on_delete=models.PROTECT, null=True, blank=True)
    batch_number = models.IntegerField(null=True, blank=True)
    order_file = models.FileField(upload_to='attachments', blank=True, null=True)
    status = models.SmallIntegerField(choices=COMPLETED_STATUS, default=0)
    #draft = models.SmallIntegerField(choices=DRAFT_STATUS, default=0)

    # ---------------------------- Foreign ----------------------------
    # users = models.ManyToManyField(User, blank=True)
    batch_no = models.ForeignKey(BatchNumber, on_delete=models.PROTECT, blank=True, null=True)
    venue = models.ForeignKey(ResourceCenter, on_delete=models.CASCADE, null=True, blank=True)
    training_name = models.ForeignKey(TrainingName, on_delete=models.PROTECT, blank=True, null=True)
    project = models.ForeignKey(FundedBy, on_delete=models.PROTECT, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.id


class TrainingUser(models.Model):
    EMAIL_STATUS=(
        (False, 'NOT SENT'),
        (True, 'SENT')
    )
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    training = models.ForeignKey(TrainingBatch, related_name='traininguser', on_delete=models.CASCADE, null=True,
                                 blank=True)
    evaluation_marks = models.FloatField(blank=True, default=0.0)
    certificate = models.FileField(upload_to='attachments', blank=True, null=True)
    document_name = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    mail_body = models.TextField(null=True, blank=True)
    to = models.EmailField(null=True, blank=True)
    from_e = models.EmailField(null=True, blank=False)
    subject = models.TextField(null=True, blank=True)
    status = models.BooleanField(choices=EMAIL_STATUS, default=False, null=False, blank=False)

    def __str__(self):
        return '%s' % self.id

    class Meta:
        unique_together = (("user", "training"),)


# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------- Audit Trail --------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

class AuditTrail(models.Model):
    module_name = models.CharField(max_length=100, null=True, blank=True)
    module_id = models.IntegerField(null=True, blank=True)
    time = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    action = models.CharField(max_length=100, null=True, blank=True)
    ip_address = models.GenericIPAddressField(default='127.0.0.1', null=True, blank=True)
    detail = JSONField(null=True, blank=True)
    prev_detail = JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)


# ----------------------------------------------Home Page Image------------------------------------------------------
class HomePageImage(models.Model):
    title = models.TextField(blank=True)
    image = models.ImageField(upload_to='homepage/', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)


# ----------------------------Payment---------------------------------------

class Payment(models.Model):
    start_date = models.DateField(blank=True, null=True)
    commencement_date = models.DateField(blank=True, null=True)
    completion_date = models.DateField(blank=True, null=True)
    contract = models.OneToOneField(NewContract, related_name='payment_set', on_delete=models.CASCADE, blank=True,
                                    null=True)

    termination_date = models.DateField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    reason = models.CharField(max_length=200, blank=True, null=True)
    is_terminated = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)


class PaymentAmountVariation(models.Model):
    amount_variation = models.IntegerField(default=0, blank=True, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)


class PaymentTimeVariation(models.Model):
    time_variation = models.IntegerField(default=0, blank=True, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)


class MonthlyProgress(models.Model):
    month = models.SmallIntegerField(blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    progress = models.IntegerField(blank=True, null=True)
    amount = models.IntegerField(blank=True, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)


class ExtOrg(models.Model):
    name = models.CharField(max_length=50, unique=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.name


class InviteeOffice(models.Model):
    name = models.TextField(unique=True)
    external_organization = models.ForeignKey(ExtOrg, null=False, blank=False, related_name='external_organization')
    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.name


class ColumnCustomization(models.Model):
    report_for = models.CharField(max_length=50, unique=True, null=True)
    columns = ArrayField(models.IntegerField())

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.report_for


class InventoryProducts(models.Model):
    serial_no = models.CharField(max_length=150, blank=True, null=True)
    asset_no = models.CharField(max_length=50, blank=True, null=True)
    cost = models.FloatField(blank=True, null=True)
    user_designation = models.ForeignKey(Designation, on_delete=models.PROTECT, null=True, blank=True)

    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)


class PasswordRequest(models.Model):
    TYPE_CHOICES = (('Main Domain', 'Main Domain'), ('Other Domain', 'Other Domain'))
    STATUS_CHOICES = (('Pending', 'Pending'), ('Solved', 'Solved'))
    comment = models.CharField(max_length=200, blank=True, null=True)
    user = models.ForeignKey(User)
    new_password = models.CharField(max_length=50, blank=True, null=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='Main Domain')
    e_gp_id = models.EmailField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    user_comment = models.CharField(max_length=200, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)


class HomepageWriting(models.Model):
    about_dimappp = models.TextField(null=True, blank=True)
    about_lged = models.TextField(null=True, blank=True)
    about_lgis = models.TextField(null=True, blank=True)
    contact = models.TextField(null=True, blank=True)
    notice_no_limit = models.SmallIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)


class ImportantLinks(models.Model):
    label = models.CharField(max_length=50, blank=True, null=True)
    link = models.URLField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)


class ExtMemberTransferHistory(models.Model):
    STATUS = (
        (0, 'promotion'),
        (1, 'transfer')
    )
    APPROVED_STATUS = (
        (0, 'pending'),
        (1, 'approved')
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    transferred_office = models.ForeignKey(Office, related_name='ext_member_transferred_office', on_delete=models.CASCADE,
                                           blank=True, null=True)
    organization = models.CharField(max_length=30, null=True, blank=True)
    office_category = models.CharField(max_length=60, null=True, blank=True)
    new_designation = models.ForeignKey(Designation, on_delete=models.CASCADE, null=True, blank=True)
    nid = models.CharField(max_length=50, null=True, blank=True)

    # transfer related details
    transfer_memo_no = models.CharField(max_length=150, null=True, blank=True)
    transfer_order = models.FileField(upload_to='transfer', null=True, blank=True)
    charge_handover_date = models.DateField(null=True, blank=True)

    status = models.SmallIntegerField(choices=STATUS, default=1)
    approved_status = models.SmallIntegerField(choices=APPROVED_STATUS, default=0)


    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s' % self.id


class ExtMemberInclusionHistory(models.Model):
    APPROVED_STATUS = (
        (0, 'pending'),
        (1, 'approved')
    )

    # office information
    office_name = models.CharField(max_length=200, blank=True, null=True)
    organization = models.CharField(max_length=20, blank=True, null=True)
    office_category = models.CharField(max_length=50, blank=True, null=True)
    bangla_name = models.CharField(max_length=50, blank=True, null=True)

    # focal point user information
    user_id_for_pro_info = models.EmailField(blank=True, null=True)
    focal_designation = models.ForeignKey(Designation, on_delete=models.PROTECT, related_name='focal_designation',
                                          null=True, blank=True)

    # personal information
    first_name = models.CharField(max_length=30, null=True, blank=True)
    designation = models.ForeignKey(Designation, on_delete=models.PROTECT, related_name='personal_designation',
                                    null=True, blank=True)
    nid = models.CharField(max_length=50, null=True, blank=True, unique=True)
    personal_mobile_no = models.CharField(max_length=30, null=True, blank=True)
    official_email = models.EmailField(blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    procurement_roles = models.ManyToManyField(ProcurementRole, blank=True)
    e_gp_user_id_for_govt = models.EmailField(null=True, blank=True)
    BOOL_CHOICES = ((True, 'Yes'), (False, 'No'))
    PPR_training = models.NullBooleanField(choices=BOOL_CHOICES, blank=True, null=True, default=None)
    start_date = models.DateField(null=True, blank=True)
    venue = models.ForeignKey(ResourceCenter, on_delete=models.CASCADE, null=True, blank=True)

    approved_status = models.SmallIntegerField(choices=APPROVED_STATUS, default=0)
    case = models.SmallIntegerField(default=1)

    certificate = models.FileField(upload_to='attachments', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)


class AdminUsers(models.Model):
    designation = models.ForeignKey(Designation, on_delete=models.PROTECT, null=True, blank=True)
    procurement_roles = models.ManyToManyField(ProcurementRole)
    ext_member_history = models.ForeignKey(ExtMemberInclusionHistory, related_name='admin_users', on_delete=models.PROTECT, null=True, blank=True)


class GovtUsers(models.Model):
    designation = models.ForeignKey(Designation, on_delete=models.PROTECT, null=True, blank=True)
    procurement_roles = models.ManyToManyField(ProcurementRole)
    ext_member_history = models.ForeignKey(ExtMemberInclusionHistory, related_name='govt_users', on_delete=models.PROTECT, null=True, blank=True)


class ExpiredLink(models.Model):
    link = models.URLField(max_length=200)
    expired = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, blank=True)
