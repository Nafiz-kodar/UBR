# myapp/models.py
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class CustomUserManager(BaseUserManager):  # Fixed: was __BaseUserManager__
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

class CustomUser(AbstractBaseUser, PermissionsMixin):  # Fixed: was __AbstractBaseUser__, __PermissionsMixin__
    USER_TYPES = (
        ('owner', 'Owner'),
        ('inspector', 'Inspector'),
        ('admin', 'Admin'),
    )
    
    u_id = models.AutoField(primary_key=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPES)
    name = models.CharField(max_length=255)
    nid = models.CharField(max_length=20, unique=True)  # Added unique=True
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    license = models.CharField(max_length=50, blank=True, null=True)  # Fixed indentation
    approved_inspector = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'user_type']
    
    class Meta:  # Fixed indentation
        db_table = 'user'
    
    def __str__(self):
        return self.email

class Property(models.Model):  # Fixed: was __models__.__Model__
    PROPERTY_TYPES = (
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
        ('apartment', 'Apartment'),
        ('land', 'Land'),
    )
    
    p_id = models.AutoField(primary_key=True)
    property_type = models.CharField(max_length=50, choices=PROPERTY_TYPES)
    location = models.CharField(max_length=255)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='properties')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'property'
    
    def __str__(self):
        return f"Property #{self.p_id} - {self.property_type}"

class Inspection(models.Model):  # Fixed: was __models__.__Model__
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    )
    
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='inspections')
    inspector = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='inspections')  # Added blank=True
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    scheduled_date = models.DateTimeField()
    completed_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'inspection'
        ordering = ['-scheduled_date']  # Added ordering
    
    def __str__(self):
        return f"Inspection #{self.id} - {self.property}"