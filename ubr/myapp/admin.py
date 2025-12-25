from django.contrib import admin
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