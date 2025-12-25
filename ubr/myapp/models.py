# myapp/models.py
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('user_type', 'admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    u_id = models.AutoField(primary_key=True)
    user_type = models.CharField(max_length=50, null=True, blank=True)
    nid = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, null=True, blank=True)
    license = models.CharField(max_length=50, null=True, blank=True)
    approved_inspect = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='approved_inspect_id',
        related_name='approved_inspectors'
    )
    
    # Required for Django admin
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
    
    class Meta:
        db_table = 'user'
        managed = False  # Django won't try to create/modify this table
    
    def __str__(self):
        return self.email or f"User {self.u_id}"


class Property(models.Model):
    p_id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=50, null=True, blank=True, db_column='type')
    locations = models.CharField(max_length=255, null=True, blank=True)
    owner = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        db_column='owner_id',
        related_name='properties',
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'property'
        managed = False
    
    def __str__(self):
        return f"Property #{self.p_id} - {self.type}"


class Message(models.Model):
    m_id = models.AutoField(primary_key=True)
    sender_id = models.IntegerField(null=True, blank=True)
    receiver_id = models.IntegerField(null=True, blank=True)
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        db_column='user_id',
        related_name='messages',
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'message'
        managed = False
    
    def __str__(self):
        return f"Message #{self.m_id}"


class Report(models.Model):
    r_id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        db_column='owner_id',
        related_name='reports_as_owner',
        null=True,
        blank=True
    )
    inspector = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        db_column='inspector_id',
        related_name='reports_as_inspector',
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'report'
        managed = False
    
    def __str__(self):
        return f"Report #{self.r_id}"


class Transaction(models.Model):
    t_id = models.AutoField(primary_key=True)
    details = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'transaction'
        managed = False
    
    def __str__(self):
        return f"Transaction #{self.t_id}"


class InspectionRequest(models.Model):
    req_id = models.AutoField(primary_key=True)
    req_type = models.CharField(max_length=100, null=True, blank=True)
    
    class Meta:
        db_table = 'inspection_request'
        managed = False
    
    def __str__(self):
        return f"Request #{self.req_id} - {self.req_type}"


class Submits(models.Model):
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
        db_column='t_id',
        primary_key=True
    )
    request = models.ForeignKey(
        InspectionRequest,
        on_delete=models.CASCADE,
        db_column='req_id'
    )
    owner = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        db_column='owner_id'
    )
    
    class Meta:
        db_table = 'submits'
        managed = False
        unique_together = (('transaction', 'request', 'owner'),)
    
    def __str__(self):
        return f"Submit: T{self.transaction.t_id} - R{self.request.req_id}"


class Assigns(models.Model):
    request = models.ForeignKey(
        InspectionRequest,
        on_delete=models.CASCADE,
        db_column='req_id',
        primary_key=True
    )
    admin = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        db_column='admin_id',
        related_name='assigned_as_admin'
    )
    inspector = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        db_column='inspector_id',
        related_name='assigned_as_inspector'
    )
    
    class Meta:
        db_table = 'assigns'
        managed = False
        unique_together = (('request', 'admin', 'inspector'),)
    
    def __str__(self):
        return f"Assignment: Request {self.request.req_id}"