from __future__ import unicode_literals

from django.db import models

# Create your models here.

class ApplicationRegistered(models.Model):

    class Meta:
        db_table = 'application_registered'

    application = models.AutoField(primary_key=True)
    app_name = models.CharField(max_length=50,blank=True,null=True)
    executable = models.CharField(max_length=50, blank=True, null=True)
    auth_token = models.CharField(max_length=50, blank=True, null=True)
    app_user = models.CharField(max_length=50, blank=True, null=True)
    description = models.CharField(max_length=1000, blank=True, null=True)
    registered_time = models.DateTimeField()
    last_updated_time = models.DateTimeField()

class ApplicationRunning(models.Model):

    class Meta:
        db_table = 'application_running'

    application = models.OneToOneField(ApplicationRegistered)
    start_time = models.DateTimeField()
    status = models.CharField(max_length=20,blank=True,null=True)
    app_settings = models.CharField(max_length=200,blank=True,null=True)