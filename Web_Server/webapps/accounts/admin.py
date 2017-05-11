from django.contrib import admin

# Register your models here.
from .models import User,UserFullName, UserProfile, Group, UserRegistrationRequests
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'userprofile'

class RegistartionInline(admin.StackedInline):
    model = UserRegistrationRequests
    can_delete = False
    verbose_name_plural = 'UserRegistrationRequests'

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline, RegistartionInline, )


admin.site.unregister(User)
admin.site.register(User, UserAdmin)

