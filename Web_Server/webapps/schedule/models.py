from __future__ import unicode_literals

from django.db import models
from django.contrib.postgres.fields import JSONField


class Holiday(models.Model):
    date = models.DateField(primary_key=True)
    description = models.CharField(max_length=50)

    class Meta:
        db_table = "holiday"

    def __unicode__(self):
        return str(self.date)

    def as_json(self):
        return dict(
            holiday_date=self.date,
            description=self.description.encode('utf-8') if self.description else ''
        )

class schedule_data(models.Model):
    agent_id = models.CharField(max_length=100,primary_key=True)
    schedule = JSONField(default={})

    class Meta:
        db_table = "schedule_data"

    def __unicode__(self):
        return str(self.agent_id)+'_schedule'

    def as_json(self):
        return dict(
            agent_id=self.agent_id,
            schedule=self.schedule
        )