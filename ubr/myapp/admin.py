from django.contrib import admin
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
