from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser, Property, Inspection


class CustomUserAdmin(BaseUserAdmin):
    """
    Custom admin interface for CustomUser model
    """
    list_display = ('email', 'name', 'user_type', 'nid', 'is_active', 'approved_inspector', 'is_staff')
    list_filter = ('user_type', 'is_active', 'approved_inspector', 'is_staff')
    search_fields = ('email', 'name', 'nid', 'phone')
    ordering = ('-u_id',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {
            'fields': ('name', 'nid', 'phone', 'user_type', 'license')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'approved_inspector', 'groups', 'user_permissions')
        }),
        ('Important Dates', {
            'fields': ('last_login',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'nid', 'phone', 'user_type', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ('last_login',)
    filter_horizontal = ('groups', 'user_permissions')


class PropertyAdmin(admin.ModelAdmin):
    """
    Admin interface for Property model
    """
    list_display = ('p_id', 'property_type', 'location', 'owner', 'created_at', 'updated_at')
    list_filter = ('property_type', 'created_at')
    search_fields = ('location', 'owner__name', 'owner__email', 'p_id')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Property Information', {
            'fields': ('property_type', 'location', 'owner')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class InspectionAdmin(admin.ModelAdmin):
    """
    Admin interface for Inspection model
    """
    list_display = ('id', 'property', 'inspector', 'status', 'scheduled_date', 'completed_date', 'created_at')
    list_filter = ('status', 'scheduled_date', 'created_at')
    search_fields = ('property__location', 'inspector__name', 'inspector__email', 'notes')
    ordering = ('-scheduled_date',)
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Inspection Details', {
            'fields': ('property', 'inspector', 'status')
        }),
        ('Schedule', {
            'fields': ('scheduled_date', 'completed_date')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """
        Optimize queries by selecting related objects
        """
        qs = super().get_queryset(request)
        return qs.select_related('property', 'inspector')


# Register all models
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Property, PropertyAdmin)
admin.site.register(Inspection, InspectionAdmin)

# Customize admin site header and title
admin.site.site_header = "UBR Property Management"
admin.site.site_title = "UBR Admin Portal"
admin.site.index_title = "Welcome to UBR Property Management System"