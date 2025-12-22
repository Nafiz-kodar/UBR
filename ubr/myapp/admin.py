from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile


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


# Also register Profile separately for direct access
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'bio_preview')
    search_fields = ('user__username', 'location')
    
    def bio_preview(self, obj):
        """Show first 50 characters of bio"""
        return obj.bio[:50] + '...' if len(obj.bio) > 50 else obj.bio
    
    bio_preview.short_description = 'Bio'