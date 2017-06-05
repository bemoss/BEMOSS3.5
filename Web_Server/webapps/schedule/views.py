from django.shortcuts import render

import os
import shutil
from datetime import datetime
from django.template import RequestContext

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
# from _utils.page_load_utils import get_device_list_side_navigation
from _utils.device_list_utils import get_device_list_and_count
from webapps.deviceinfos.models import DeviceMetadata
from webapps.deviceinfos.models import SupportedDevices
from webapps.device.models import Devicedata
from webapps.schedule.models import schedule_data
from bemoss_lib.utils.BEMOSS_globals import *
from webapps.bemoss_applications.models import ApplicationRunning, ApplicationRegistered


import json
from _utils import config_helper

from bemoss_lib.utils.VIP_helper import vip_publish
from django_web_server import settings_tornado
from _utils import defaults as __

def showSchedule(request,device_id):
    # return HttpResponse('No schedule yet for: ' + str(device_id) )
    device_info = DeviceMetadata.objects.get(mac_address=device_id)
    if device_info.device_type.device_type == 'HVAC':
        return thermostat_schedule(request, device_id)
    elif device_info.device_type.device_type == 'Lighting':
        return lighting_schedule(request, device_id)
    elif device_info.device_type.device_type == 'Plugload':
        return plugload_schedule(request, device_id)


device_id = ''

disabled_values_thermostat = {"everyday": {
            'monday': [],
            'tuesday': [],
            'wednesday': [],
            'thursday': [],
            'friday': [],
            'saturday': [],
            'sunday': []},
        "weekdayweekend": {
            'weekday': [],
            'weekend': []},
        "holiday": {
            'holiday': []}}

disabled_values_lighting = {"everyday": {
            'monday': [],
            'tuesday': [],
            'wednesday': [],
            'thursday': [],
            'friday': [],
            'saturday': [],
            'sunday': []},
        "weekdayweekend": {
            'weekday': [],
            'weekend': []},
        "holiday": {
            'holiday': []}}

disabled_values_plugload = {"everyday": {
            'monday': [],
            'tuesday': [],
            'wednesday': [],
            'thursday': [],
            'friday': [],
            'saturday': [],
            'sunday': []},
        "weekdayweekend": {
            'weekday': [],
            'weekend': []},
        "holiday": {
            'holiday': []}}


@login_required(login_url='/login/')
def thermostat_schedule(request, mac):
    print 'Inside Set Schedule method in Schedule app'
    context = RequestContext(request)
    user_group = request.user.groups.all().values_list('name', flat=True)
    if 'Admin' in user_group or 'Zone Manager' in user_group:
        print type(mac)
        mac = mac.encode('ascii', 'ignore')
        print type(mac)

        device_metadata = [ob.device_control_page_info() for ob in DeviceMetadata.objects.filter(mac_address=mac)]
        print device_metadata
        device_id = device_metadata[0]['agent_id']
        device_model = device_metadata[0]['device_model']

        device_status = [ob.data_as_json() for ob in Devicedata.objects.filter(agent_id=device_id)]
        device_node = device_status[0]['node_id']
        device_nickname = device_status[0]['nickname']
        node_nickname = device_status[0]['node_nickname']

        device_list_side_nav = get_device_list_and_count(request)
        context.update(device_list_side_nav)
        _data = {}
        active_schedule = []
        disabled_range = __.DISABLED_VALUES_THERMOSTAT_NEW

        #Check if schedule for this device exists
        try:
            sch_data = schedule_data.objects.get(agent_id=device_id)
            _json_data = sch_data.schedule
            if device_id in _json_data['thermostat']:
                print 'device id present'
                _data = _json_data['thermostat'][device_id]['schedulers']

                active_schedule = _json_data['thermostat'][device_id]['active']
                active_schedule = [str(x) for x in active_schedule]
                disabled_range = get_disabled_date_ranges_thermostat(_data)
                _data = json.dumps(_data)
                _data = json.loads(_data, object_hook=_decode_dict)
        except ObjectDoesNotExist:
            _json_data = {"thermostat": {
                device_id: {
                    "active": ['everyday', 'holiday'],
                    "inactive": [],
                    "schedulers": __.THERMOSTAT_DEFAULT_SCHEDULE_NEW
                }}}

            schedule_data(agent_id=device_id, schedule=_json_data).save()
            _data = _json_data['thermostat'][device_id]['schedulers']
            active_schedule = ['everyday', 'holiday']
            disabled_range = get_disabled_date_ranges_thermostat(_data)

        schedule_meta = [ob.get_schedule_info() for ob in SupportedDevices.objects.filter(device_model=device_model)]
        schedule_meta = json.dumps(schedule_meta[0])
        print schedule_meta

        return_data = {'device_id': device_id, 'device_zone': device_node, 'zone_nickname': node_nickname, 'mac_address': mac,
             'device_nickname': device_nickname, 'schedule': _data,
             'disabled_ranges': disabled_range, 'active_schedule': active_schedule, 'schedule_meta': schedule_meta}

        return_data.update(device_list_side_nav)

        return render(request, 'schedule/thermostat_schedule.html', return_data)
    else:
        return HttpResponseRedirect('/home')


def get_disabled_date_ranges_thermostat(_data):

    disabled_values = __.DISABLED_VALUES_THERMOSTAT_NEW
    for sch_type in _data:
        if sch_type == 'holiday':
            for item in _data[sch_type]:
                value = []
                for _item in _data[sch_type]:
                    value.append(int(_item['at']))
                disabled_values[sch_type]['holiday'] = value
        else:
            for day in _data[sch_type]:
                for item in _data[sch_type][day]:
                    value = []
                    for _item in _data[sch_type][day]:
                        value.append(int(_item['at']))
                    disabled_values[sch_type][day] = value
    print disabled_values
    return disabled_values


@login_required(login_url='/login/')
def update_device_schedule(request):

    _data = json.loads(request.body)
    print _data
    device_info = _data['device_info']
    device_info = device_info.split('/')
    device_id = device_info[2]
    device_type = device_info[1]
    device_zone = device_info[0]
    activate_schedule(device_type,device_id)
    schedule_type = ''
    if 'everyday' in str(_data):
        schedule_type = 'everyday'
    elif 'weekdayweekend' in str(_data):
        schedule_type = 'weekdayweekend'
    elif 'holiday' in str(_data):
        schedule_type = 'holiday'
    content = save_schedule(device_id, device_type, _data['schedule'], schedule_type, _data['user'])

    message_to_agent = {
        "auth_token": "bemoss",
        "user": _data['user'],
        "content": content
    }
    ieb_topic = 'to/scheduler_' + device_id + '/update/from/ui'
    ieb_topic2 = 'to/scheduler_'+device_id+'/from/ui/update'
    print ieb_topic
    vip_publish(ieb_topic, json.dumps(message_to_agent))
    vip_publish(ieb_topic2, json.dumps(message_to_agent))
    result = 'success'



    if request.is_ajax():
        return HttpResponse(json.dumps(result))


def save_schedule(device_id, device_type, _data, schedule_type, user):
    try:
        _json_data = schedule_data.objects.get(agent_id=device_id).schedule
    except ObjectDoesNotExist:
        _json_data = {device_type: {
            device_id: {
                "active": ['everyday', 'holiday'],
                "inactive": [],
                "schedulers": __.THERMOSTAT_DEFAULT_SCHEDULE_NEW
            }}}
    if device_id not in _json_data[device_type]:
        _json_data[device_type][device_id] = {'active': [], 'inactive': [], 'schedulers': {}}
    _json_data[device_type][device_id]['schedulers'][schedule_type] = _data[schedule_type]
    _json_data[device_type][device_id]['user'] = user
    _json_data[device_type][device_id]['start_from'] = str(datetime.now())
    print _json_data
    schedule_file_content = _json_data
    sch_data = schedule_data(agent_id=device_id, schedule=schedule_file_content)
    sch_data.save()
    return schedule_file_content



def activate_schedule(device_type,device_id):
    app_agent_id = 'scheduler_'+device_id
    registered_app = ApplicationRegistered.objects.filter(app_name__iexact=device_type + '_scheduler')
    if registered_app:
        registered_app = registered_app[0]
        device = DeviceMetadata.objects.filter(agent_id=device_id)
        try:
            app = ApplicationRunning.objects.get(app_agent_id='scheduler_'+device_id)
        except ApplicationRunning.DoesNotExist:
            app = ApplicationRunning(start_time=datetime.now(), status='running',
                                     app_type=registered_app, app_data={"device_agent_id":device_id},
                                     app_agent_id='scheduler_'+device_id)

        app.status = 'running'
        if device:
            app.app_data['description'] = 'For: ' + device[0].nickname

        app.save()
        message = dict()
        message[STATUS_CHANGE.AGENT_ID] = app_agent_id
        message[STATUS_CHANGE.NODE] = "0"
        message[STATUS_CHANGE.AGENT_STATUS] = 'start'
        message[STATUS_CHANGE.NODE_ASSIGNMENT_TYPE] = ZONE_ASSIGNMENT_TYPES.PERMANENT
        message['is_app'] = True
        topic = 'to/networkagent/status_change/from/ui'
        vip_publish(topic, [message])


@login_required(login_url='/login/')
def update_schedule_status_to_browser(request):
    print "device_schedule_update_message_to_browser"
    if request.method == 'POST':
        _data = request.raw_post_data
        device_info = _data
        device_info = device_info.split('/')
        device_type = device_info[1]
        device_id = device_info[2]
        topic = 'schedule_update_status'
        thermostat_update_schedule_status = config_helper.get_update_message(topic)
        print type(thermostat_update_schedule_status)
        data_split = str(thermostat_update_schedule_status).split("/")
        if data_split[0] == device_id:
            result = data_split[1]
        else:
            result = 'failure'
        json_result = {'status': result}
        #zmq_topics.reset_update_topic()
        print json.dumps(json_result)
        if request.is_ajax():
            return HttpResponse(json.dumps(json_result), content_type='application/json')


@login_required(login_url='/login/')
def plugload_schedule(request, mac):
    print 'Inside Set Schedule method in Schedule app'
    context = RequestContext(request)
    user_group = request.user.groups.all().values_list('name', flat=True)
    if 'Admin' in user_group or 'Zone Manager' in user_group:
        mac = mac.encode('ascii', 'ignore')
        print type(mac)

        device_metadata = [ob.device_control_page_info() for ob in DeviceMetadata.objects.filter(mac_address=mac)]
        print device_metadata
        device_id = device_metadata[0]['agent_id']
        device_model = device_metadata[0]['device_model']

        device_status = [ob.data_as_json() for ob in Devicedata.objects.filter(agent_id=device_id)]
        device_node = device_status[0]['node_id']
        device_nickname = device_status[0]['nickname']
        node_nickname = device_status[0]['node_nickname']

        _data = {}
        active_schedule = []
        disabled_range = __.DISABLED_VALUES_PLUGLOAD

        try:
            sch_data = schedule_data.objects.get(agent_id=device_id)
            _json_data = sch_data.schedule
            if device_id in _json_data['plugload']:
                print 'device id present'
                _data = _json_data['plugload'][device_id]['schedulers']

                active_schedule = _json_data['plugload'][device_id]['active']
                active_schedule = [str(x) for x in active_schedule]
                disabled_range = get_disabled_date_ranges(_data, __.DISABLED_VALUES_PLUGLOAD)
                _data = json.dumps(_data)
                _data = json.loads(_data, object_hook=_decode_dict)
        except ObjectDoesNotExist:
            _json_data = {"plugload": {
                device_id: {
                    "active": ['everyday', 'holiday'],
                    "inactive": [],
                    "schedulers": __.PLUGLOAD_DEFAULT_SCHEDULE
                }}}

            schedule_data(agent_id=device_id, schedule=_json_data).save()
            _data = _json_data['plugload'][device_id]['schedulers']

            active_schedule = ['everyday', 'holiday']
            disabled_range = get_disabled_date_ranges(_data, __.DISABLED_VALUES_PLUGLOAD)



        device_list_side_nav = get_device_list_and_count(request)
        context.update(device_list_side_nav)
        return_data = {'device_id': device_id, 'device_zone': device_node, 'zone_nickname': node_nickname,
                       'mac_address': mac,
                       'device_nickname': device_nickname, 'schedule': _data,
                       'disabled_ranges': disabled_range, 'active_schedule': active_schedule}

        return_data.update(device_list_side_nav)

        return render(request, 'schedule/plugload_schedule.html', return_data)
    else:
        return HttpResponseRedirect('/home/')



@login_required(login_url='/login/')
def lighting_schedule(request, mac):
    print 'Inside Set Schedule method in Schedule app'
    context = RequestContext(request)
    user_group = request.user.groups.all().values_list('name', flat=True)
    if 'Admin' in user_group or 'Zone Manager' in user_group:
        print type(mac)
        mac = mac.encode('ascii', 'ignore')
        print type(mac)

        device_metadata = [ob.device_control_page_info() for ob in DeviceMetadata.objects.filter(mac_address=mac)]
        print device_metadata
        device_id = device_metadata[0]['agent_id']
        device_model = device_metadata[0]['device_model']
        device_status = [ob.data_as_json() for ob in Devicedata.objects.filter(agent_id=device_id)]
        device_node = device_status[0]['node_id']
        device_nickname = device_status[0]['nickname']
        node_nickname = device_status[0]['node_nickname']

        device_list_side_nav = get_device_list_and_count(request)
        context.update(device_list_side_nav)
        _data = {}
        active_schedule = []
        disabled_range = __.DISABLED_VALUES_LIGHTING

        #Check if schedule file for this device exists
        try:
            sch_data = schedule_data.objects.get(agent_id=device_id)
            _json_data = sch_data.schedule
            if device_id in _json_data['lighting']:
                print 'device id present'
                _data = _json_data['lighting'][device_id]['schedulers']

                active_schedule = _json_data['lighting'][device_id]['active']
                active_schedule = [str(x) for x in active_schedule]
                disabled_range = get_disabled_date_ranges(_data, __.DISABLED_VALUES_LIGHTING)
                _data = json.dumps(_data)
                _data = json.loads(_data, object_hook=_decode_dict)
        except ObjectDoesNotExist:
            _json_data = {"lighting": {
            device_id: {
                "active": ['everyday', 'holiday'],
                "inactive": [],
                "schedulers": __.LIGHTING_DEFAULT_SCHEDULE
                }}}

            schedule_data(agent_id=device_id, schedule=_json_data).save()
            _data = _json_data['lighting'][device_id]['schedulers']

            active_schedule = ['everyday', 'holiday']
            disabled_range = get_disabled_date_ranges(_data, __.DISABLED_VALUES_LIGHTING)

        return_data = {'device_id': device_id, 'device_zone': device_node, 'zone_nickname': node_nickname, 'mac_address': mac,
         'device_nickname': device_nickname, 'schedule': _data,
         'disabled_ranges': disabled_range, 'active_schedule': active_schedule}

        return_data.update(device_list_side_nav)

        return render(request, 'schedule/lighting_schedule.html', return_data)
    else:
        return HttpResponseRedirect('/home/')


def get_disabled_date_ranges(_data, disabled_values_type):
    disabled_values = disabled_values_type
    for sch_type in _data:
        if sch_type == 'holiday':
            for item in _data[sch_type]:
                value = []
                for _item in _data[sch_type][item]:
                    value.append(int(_item['at']))
                disabled_values[sch_type][item] = value
        else:
            for day in _data[sch_type]:
                value = []
                for item in _data[sch_type][day]:
                    value.append(int(item['at']))
                disabled_values[sch_type][day] = value
    print disabled_values
    return disabled_values


def _decode_list(data):
    rv = []
    for item in data:
        if isinstance(item, unicode):
            item = item.encode('utf-8')
        elif isinstance(item, list):
            item = _decode_list(item)
        elif isinstance(item, dict):
            item = _decode_dict(item)
        rv.append(item)
    return rv


def _decode_dict(data):
    rv = {}
    for key, value in data.iteritems():
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        elif isinstance(value, list):
            value = _decode_list(value)
        elif isinstance(value, dict):
            value = _decode_dict(value)
        rv[key] = value
    return rv
