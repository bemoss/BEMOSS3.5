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


#All classes for alerts and notifications page handling
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from _utils.device_list_utils import get_device_list_and_count
from webapps.alerts.models import Alerts, AlertTypes, PriorityLevels, NotificationChannels, Notification, NotificationChannelAddresses, DeviceType
from webapps.accounts.models import UserFullName

import json
from datetime import datetime, timedelta


@login_required(login_url='/login/')
def alerts(request):
    print 'inside alerts view method'
    context = RequestContext(request)

    device_list_side_nav = get_device_list_and_count(request)
    context.update(device_list_side_nav)

    if request.user.groups.filter(name__iexact='admin').exists():

        usr = UserFullName.objects.filter(username=request.user)[0]
        _registered_alerts = [ob.as_json() for ob in Alerts.objects.all()]
        _alerts = [ob.as_json() for ob in AlertTypes.objects.all()]
        _alert_pr = [ob.as_json() for ob in PriorityLevels.objects.all()]
        _n_type = [ob.as_json() for ob in NotificationChannels.objects.all()]
        active_al = get_notifications()
        data = {'registered_alerts': _registered_alerts, 'alerts': _alerts, 'priority': _alert_pr, 'n_type': _n_type,
             'user_full_name': usr, 'active_al': active_al}
        data.update(get_device_list_and_count(request))
        return render(request,'alerts/alarms.html',data)
    else:
        return HttpResponseRedirect('/home/')


# @login_required(login_url='/login/')
# def no_of_seen_notifications_push(request):
#     response_data = {}
#     bemoss_not = general_notifications()
#     post = SeenNotifications(id=1, counter=len(bemoss_not))
#     post.save()
#     print "succssful"
#     response_data['result'] = 'succssful'
#     return HttpResponse(
#         json.dumps(response_data), content_type="application/json")


@login_required(login_url='/login/')
def create_alert(request):
    # return HttpResponse('1234654654')
    # print 'inside create alert method'
    if request.POST:

        _data = request.body
        _data = json.loads(_data)
        print _data

        _alert = AlertTypes.objects.get(alert_name=_data['alert'])

        print _alert

        _priority = PriorityLevels.objects.get(priority_level=_data['priority'])

        new_alert = Alerts.objects.create(alert_type=_alert, priority_id=_priority.id, user=request.user, created_on=datetime.now())
        new_alert.save()

        # print alerts
        for ntype in ["Email","Text"]:
            n_id = NotificationChannels.objects.get(notification_channel=ntype)
            for address in _data[n_id.notification_channel]:
                address = address.strip()
                if address:
                    try:
                        existing_address = NotificationChannelAddresses.objects.get(notify_address=address)
                    except NotificationChannelAddresses.DoesNotExist:
                        NotificationChannelAddresses.objects.create(notification_channel=n_id, notify_address=address)
                        existing_address = NotificationChannelAddresses.objects.get(notify_address=address)
                    new_alert.alert_channels.add(existing_address)
                    new_alert.save()

        if request.is_ajax():
            return HttpResponse(json.dumps(_data), content_type='application/json')

@login_required(login_url='/login/')
def delete_alert(request):
    print "Inside delete alert method"
    if request.POST:
        _data = request.body

        Alerts.objects.filter(id=int(_data)).delete()

    if request.is_ajax():
        return HttpResponse(json.dumps)


def get_notifications(seen=False):
    print "Fetching active notifications from the database"
    return Notification.objects.filter(seen=seen).order_by('-dt_triggered')


def general_notifications():
    return get_notifications()


def notifications(request):
    print "Notifications page load"
    context = RequestContext(request)

    device_list_side_nav = get_device_list_and_count(request)
    context.update(device_list_side_nav)

    if request.user.groups.filter(name__iexact='admin').exists():
        Notification.objects.filter(seen=False).update(seen=True)
        all_notifications = Notification.objects.all().order_by('-dt_triggered')
        if len(all_notifications) > 100: #TODO limit of how many old notifications to save in Postgresql
            Notification.objects.filter(dt_triggered__lt=all_notifications[99].dt_triggered).delete()
        notifications = get_notifications(seen=True)

        usr = UserFullName.objects.filter(username=request.user)[0]
        data = {"notifications": notifications}
        data.update(get_device_list_and_count(request))
        # print context
        return render(request,
            'alerts/notifications.html',data)
    else:
        return HttpResponseRedirect('/home/')