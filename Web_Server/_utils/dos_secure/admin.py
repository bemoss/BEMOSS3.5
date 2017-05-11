from django.contrib import admin

# Register your models here.
from django.contrib import admin

from models import Banishment, Whitelist

admin.site.register(Banishment)
admin.site.register(Whitelist)
