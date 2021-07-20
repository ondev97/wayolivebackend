from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, BandProfile, UserProfile, Phone


# Register your models here.
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        *UserAdmin.fieldsets,  # original form fieldsets, expanded
        (                      # new fieldset added on to the bottom
            'User Features',  # group heading of your choice; set to None for a blank space instead of a header
            {
                'fields': (
                    'is_band',
                    'phone_no',
                    'is_verified',
                ),
            },
        ),
    )


admin.site.register(User,CustomUserAdmin)
admin.site.register(BandProfile)
admin.site.register(UserProfile)
admin.site.register(Phone)

