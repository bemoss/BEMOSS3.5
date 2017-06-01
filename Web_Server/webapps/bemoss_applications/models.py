from __future__ import unicode_literals

from django.db import models
from django.contrib.postgres.fields import JSONField


class ApplicationRegistered(models.Model):

    class Meta:
        db_table = 'application_registered'

    application_id = models.AutoField(primary_key=True)
    app_name = models.CharField(max_length=50,blank=True,null=True)
    description = models.CharField(max_length=1000, blank=True, null=True)
    app_folder = models.CharField(max_length=200, blank=False, null=False)
    registered_time = models.DateTimeField()

class ApplicationRunning(models.Model):

    class Meta:
        db_table = 'application_running'

    #id = models.IntegerField(primary_key=True,auto_created=True)
    start_time = models.DateTimeField()
    app_agent_id = models.CharField(max_length=50,null=False)
    status = models.CharField(max_length=20,blank=True,null=True)
    app_type = models.ForeignKey(ApplicationRegistered)
    app_data = JSONField(default={})
