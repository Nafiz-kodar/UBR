from django.contrib import admin
<<<<<<< HEAD
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    CustomUser, Property, Message, Report, 
    Transaction, InspectionRequest, Submits, Assigns
)


class CustomUserAdmin(BaseUserAdmin):
    list_display = ('u_id', 'email', 'name', 'user_type', 'nid', 'is_active')
    list_filter = ('user_type', 'is_active')
    search_fields = ('email', 'name', 'nid')
    ordering = ('u_id',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name', 'nid', 'phone', 'user_type', 'license', 'approved_inspect')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'nid', 'user_type', 'password1', 'password2'),
        }),
    )


class PropertyAdmin(admin.ModelAdmin):
    list_display = ('p_id', 'type', 'locations', 'owner')
    list_filter = ('type',)
    search_fields = ('locations', 'owner__name')


class MessageAdmin(admin.ModelAdmin):
    list_display = ('m_id', 'sender_id', 'receiver_id', 'user')
    search_fields = ('sender_id', 'receiver_id')


class ReportAdmin(admin.ModelAdmin):
    list_display = ('r_id', 'owner', 'inspector')
    list_filter = ('owner', 'inspector')


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('t_id', 'details')


class InspectionRequestAdmin(admin.ModelAdmin):
    list_display = ('req_id', 'req_type')
    list_filter = ('req_type',)


class SubmitsAdmin(admin.ModelAdmin):
    list_display = ('transaction', 'request', 'owner')


class AssignsAdmin(admin.ModelAdmin):
    list_display = ('request', 'admin', 'inspector')


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Property, PropertyAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(Report, ReportAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(InspectionRequest, InspectionRequestAdmin)
admin.site.register(Submits, SubmitsAdmin)
admin.site.register(Assigns, AssignsAdmin)

admin.site.site_header = "UBR Property Management"
admin.site.site_title = "UBR Admin"
admin.site.index_title = "Welcome to UBR Admin Portal"
=======
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile
from .models import InspectionRequest, InspectionReport, Complaint, Message, Payment, AdminBalance


class ProfileInline(admin.StackedInline):
    """
    Display Profile fields inline when editing a User.
    """
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'


class CustomUserAdmin(UserAdmin):
    """
    Extended UserAdmin to include Profile inline.
    """
    inlines = (ProfileInline,)


# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# Register Profile separately
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type', 'bio_preview')  # removed 'location'
    search_fields = ('user__username', 'user_type')
    
    def bio_preview(self, obj):
        """Show first 50 characters of bio"""
        # `bio` field removed in current models; safe fallback
        return getattr(obj, 'bio', '')[:50] + '...' if getattr(obj, 'bio', '') and len(getattr(obj, 'bio', '')) > 50 else getattr(obj, 'bio', '')
    
    bio_preview.short_description = 'Bio'


# Register new models
@admin.register(InspectionRequest)
class InspectionRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'building_location', 'status', 'inspector', 'created_at')
    list_filter = ('status', 'req_type')


@admin.register(InspectionReport)
class InspectionReportAdmin(admin.ModelAdmin):
    list_display = ('inspection_request', 'inspector', 'inspection_date', 'decision')


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('reporter', 'against_inspector', 'resolved', 'created_at')
    list_filter = ('resolved',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'sent_at', 'is_read')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payer', 'amount', 'inspection_request', 'created_at')


@admin.register(AdminBalance)
class AdminBalanceAdmin(admin.ModelAdmin):
    list_display = ('balance',)
>>>>>>> sadi
