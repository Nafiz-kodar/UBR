<<<<<<< HEAD
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
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
    
    class Meta:
        db_table = 'user'
        managed = False
    
    def __str__(self):
        return self.email or f"User {self.u_id}"
    
    @property
    def is_approved_inspector(self):
        """Check if inspector is approved"""
        if self.user_type != 'inspector':
            return True
        return self.approved_inspect is not None


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


class InspectionRequest(models.Model):
    req_id = models.AutoField(primary_key=True)
    req_type = models.CharField(max_length=100, null=True, blank=True)
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        db_column='property_id',
        related_name='inspection_requests',
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'inspection_request'
        managed = False
    
    def __str__(self):
        return f"Request #{self.req_id} - {self.req_type}"


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
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        db_column='property_id',
        related_name='reports',
        null=True,
        blank=True
    )
    inspection_request = models.ForeignKey(
        InspectionRequest,
        on_delete=models.SET_NULL,
        db_column='inspection_request_id',
        related_name='reports',
        null=True,
        blank=True
    )
    report_content = models.TextField(null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    has_issues = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'report'
        managed = False
    
    def __str__(self):
        return f"Report #{self.r_id}"


class Transaction(models.Model):
    t_id = models.AutoField(primary_key=True)
    details = models.TextField(null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payment_status = models.CharField(max_length=50, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'transaction'
        managed = False
    
    def __str__(self):
        return f"Transaction #{self.t_id}"


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
    assigned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'assigns'
        managed = False
        unique_together = (('request', 'admin', 'inspector'),)
    
    def __str__(self):
        return f"Assignment: Request {self.request.req_id}"
=======
# myapp/models.py
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Profile(models.Model):
    USER_TYPES = (
        ('Owner', 'Owner'),
        ('Inspector', 'Inspector'),
        ('Admin', 'Admin'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='Owner')
    nid = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    is_approved = models.BooleanField(default=True)  # Inspectors require admin approval
    is_banned = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} ({self.user_type})"


class InspectionRequest(models.Model):
    REQ_TYPES = (
        ('New Construction', 'New Construction'),
        ('Reinspection', 'Reinspection'),
    )
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Assigned', 'Assigned'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Completed', 'Completed'),
        ('Paid', 'Paid'),
    )
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner_requests')
    inspector = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_inspections')
    req_type = models.CharField(max_length=30, choices=REQ_TYPES, default='New Construction')
    building_location = models.CharField(max_length=255)
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.owner.username} - {self.building_location} ({self.status})"


class InspectionReport(models.Model):
    inspection_request = models.OneToOneField(InspectionRequest, on_delete=models.CASCADE, related_name='report')
    inspector = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reports')
    inspection_date = models.DateTimeField(default=timezone.now)
    structural_evaluation = models.TextField(blank=True)
    compliance_checklist = models.TextField(blank=True)
    decision = models.CharField(max_length=20, choices=(('Approved','Approved'),('Rejected','Rejected')), blank=True)
    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"Report for {self.inspection_request}"


class Complaint(models.Model):
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='complaints_made')
    against_inspector = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='complaints_received')
    message = models.TextField()
    admin_response = models.TextField(blank=True)
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Complaint by {self.reporter.username} against {self.against_inspector.username if self.against_inspector else 'N/A'}"


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=200, blank=True)
    body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender.username} to {self.recipient.username}"


class Payment(models.Model):
    payer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    inspection_request = models.ForeignKey(InspectionRequest, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.amount} by {self.payer.username}"


class AdminBalance(models.Model):
    # Single-row table to track demo admin balance
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"Admin Balance: {self.balance}"


# Ensure a Profile exists for every User. This creates a Profile when a User
# is created and also ensures one exists if the signal fires for an existing
# user without a Profile (get_or_create is idempotent).
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def ensure_user_profile(sender, instance, created, **kwargs):
    profile, _ = Profile.objects.get_or_create(user=instance)
    # If the User has admin/staff flags (e.g. created via createsuperuser),
    # ensure their Profile reflects that role so dashboard routing works.
    if instance.is_staff or instance.is_superuser:
        if profile.user_type != 'Admin':
            profile.user_type = 'Admin'
            profile.save()
>>>>>>> sadi
