# -*- coding: utf-8 -*-

'''
Copyright (c) 2016, Virginia Tech
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
 following conditions are met:
1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those of the authors and should not be
interpreted as representing official policies, either expressed or implied, of the FreeBSD Project.

This material was prepared as an account of work sponsored by an agency of the United States Government. Neither the
United States Government nor the United States Department of Energy, nor Virginia Tech, nor any of their employees,
nor any jurisdiction or organization that has cooperated in the development of these materials, makes any warranty,
express or implied, or assumes any legal liability or responsibility for the accuracy, completeness, or usefulness or
any information, apparatus, product, software, or process disclosed, or represents that its use would not infringe
privately owned rights.

Reference herein to any specific commercial product, process, or service by trade name, trademark, manufacturer, or
otherwise does not necessarily constitute or imply its endorsement, recommendation, favoring by the United States
Government or any agency thereof, or Virginia Tech - Advanced Research Institute. The views and opinions of authors
expressed herein do not necessarily state or reflect those of the United States Government or any agency thereof.

VIRGINIA TECH – ADVANCED RESEARCH INSTITUTE
under Contract DE-EE0006352

#__author__ = "BEMOSS Team"
#__credits__ = ""
#__version__ = "2.0"
#__maintainer__ = "BEMOSS Team"
#__email__ = "aribemoss@gmail.com"
#__website__ = "www.bemoss.org"
#__created__ = "2014-09-12 12:04:50"
#__lastUpdated__ = "2016-03-14 11:23:33"
'''
from __future__ import unicode_literals

#Database models for alerts and notifications
from webapps.deviceinfos.models import DeviceType

from django.contrib.auth.models import User
from django.db import models
from django.contrib.postgres.fields import JSONField


class PossibleEvents(models.Model):
    event_name = models.CharField(max_length=50)
    event_description = models.CharField(max_length=1000)
    class Meta:
        db_table = "possible_events"

class AlertTypes(models.Model):
    alert_description = models.CharField(max_length=50)  # temperature exceeds, humidity exceeds, low battery etc.
    alert_name = models.CharField(max_length=50)
    associated_events = models.ManyToManyField(PossibleEvents)

    class Meta:
        db_table = "alert_types"

    def __unicode__(self):
        return str(self.id)

    def as_json(self):
        return dict(
            id=self.id,
            alert_description=self.alert_description.encode('utf-8') if self.alert_description else '',
            alert_name=self.alert_name.encode('utf-8') if self.alert_name else '',
           )



class NotificationChannels(models.Model):
    notification_channel = models.CharField(max_length=50)

    class Meta:
        db_table = "notification_channel"

    def __str__(self):
        return self.notification_channel

    def __unicode__(self):
        return str(self.notification_channel)

    def as_json(self):
        return dict(
            id=self.id,
            notification_channel=self.notification_channel.encode('utf-8') if self.notification_channel else '')


class PriorityLevels(models.Model):
    priority_level = models.CharField(max_length=20)
    priority_notification_hours = models.CharField(max_length=50)
    class Meta:
        db_table = "priority"

    def __unicode__(self):
        return str(self.as_json())

    def as_json(self):
        return dict(
            id=self.id,
            priority=self.priority_level.encode('utf-8').title() if self.priority_level else '')

class NotificationChannelAddresses(models.Model):
    notification_channel = models.ForeignKey(NotificationChannels)
    notify_address = models.CharField(max_length=200)

    class Meta:
        db_table = "alerts_notificationchanneladdress"

    def __unicode__(self):
        return str(self.notify_address)

    def as_json(self):
        return dict(
            channel=self.notification_channel.notification_channel,
            address=self.notify_address
        )


class Alerts(models.Model):
    alert_type = models.ForeignKey(AlertTypes)
    alert_paramter = JSONField(default={})
    #notification_channel = models.ManyToManyField(NotificationChannel, through="NotificationChannelAddress")
    priority = models.ForeignKey(PriorityLevels)
    user = models.ForeignKey(User)
    created_on = models.DateTimeField()
    alert_channels = models.ManyToManyField(NotificationChannelAddresses) #{sms:['99934343','343424234'],'email':['rajeevt.edu']}
    enabled = models.BooleanField(default=True)
    class Meta:
        db_table = "alerts"

    def __unicode__(self):
        return str(self.id)

    def as_json(self):
        # return {}
        alarm = AlertTypes.as_json(self.alert_type)
        notify_address = [ob.as_json() for ob in self.alert_channels.all()]
        priority = PriorityLevels.as_json(self.priority)

        return dict(
            id=self.id,
            alarm=alarm,
            notify_address=notify_address,
            priority=priority,
            created_on=self.created_on,
            created_by=self.user)

class Notification(models.Model):
    event_type = models.ForeignKey(PossibleEvents)
    seen = models.BooleanField(default=False)  # TRUE OR FALSE - if notification was sent successfully then TRUE else FALSE
    dt_triggered = models.DateTimeField()
    message = models.CharField(max_length=1000,blank=True,null=True)
    class Meta:
        db_table = "notification"

    def __unicode__(self):
        return str(self.as_json())

    def as_json(self):

        return dict(
            id=self.id,
            alert_status=self.seen,
            date_triggered=self.dt_triggered,
            event_type=self.event_type,
            message=self.message)
