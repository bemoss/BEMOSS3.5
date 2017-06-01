import json

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import redirect

from datetime import datetime

from django.core.urlresolvers import reverse

from webapps.bemoss_applications.models import ApplicationRunning, ApplicationRegistered
from webapps.deviceinfos.models import DeviceMetadata
from webapps.device.models import Devicedata

from _utils.device_list_utils import get_device_list_and_count
from bemoss_lib.utils.VIP_helper import vip_publish
from bemoss_lib.utils.BEMOSS_globals import *
# Create your views here.

@login_required(login_url='/login/')
def application_main(request):
    # Display the main page of bemoss applications

    hvac_fault_apps = ApplicationRunning.objects.filter(app_type__app_name='fault_detection')
    used_thermostat_ids = []
    for app in hvac_fault_apps:
        used_thermostat_ids.append(app.app_data['thermostat'])

    available_thermostas = DeviceMetadata.objects.filter(approval_status='APR', device_type_id=1,
                                                          device_model__startswith='CT').exclude(agent_id__in=used_thermostat_ids)

    apps = ApplicationRunning.objects.all()
    return_data = {'apps': apps, 'available_thermostats':available_thermostas}
    return_data.update(get_device_list_and_count(request))
    return render(request, 'applications/applications.html', return_data)

def application_add(request):
    if request.POST:
        # 1. Save configuration data
        _data = request.body
        _data = json.loads(_data)

        registered_app = ApplicationRegistered.objects.filter(app_name__iexact=_data['app_name'])
        thermostat = DeviceMetadata.objects.get(agent_id=_data['app_data']['thermostat'])

        data = {'thermostat':thermostat.agent_id,'description':"For: " + thermostat.nickname }
        if registered_app:
            registered_app = registered_app[0]
            no = ApplicationRunning.objects.filter(app_type=registered_app).count()+1
            new_app = ApplicationRunning(start_time=datetime.now(),status='stopped',
                                      app_type=registered_app, app_data=data, app_agent_id='some_name')
            new_app.save()
            new_app.app_agent_id = registered_app.app_name + str(new_app.id)
            new_app.save()
            if request.is_ajax():
                return HttpResponse(json.dumps("success"))


def application_remove(request,app_agent_id):
    running_app = ApplicationRunning.objects.filter(app_agent_id=app_agent_id)
    if running_app:
        running_app.delete()
        message = dict()
        message[STATUS_CHANGE.AGENT_ID] = app_agent_id
        message[STATUS_CHANGE.NODE] = "0"
        message[STATUS_CHANGE.AGENT_STATUS] = 'stop'
        message[STATUS_CHANGE.NODE_ASSIGNMENT_TYPE] = ZONE_ASSIGNMENT_TYPES.PERMANENT
        message['is_app'] = True
        topic = 'to/networkagent/status_change/from/ui'
        vip_publish(topic, [message])

    return redirect('application-main')

@login_required(login_url='/login/')
def application_individual(request, app_agent_id):
    try:
        running_app = ApplicationRunning.objects.get(app_agent_id=app_agent_id)
        app_type = running_app.app_type
    except ApplicationRunning.DoesNotExist:
        print "Invalid application id"
        raise Http404
    if app_type.app_name == 'iblc':
        return_data = illuminance_based_control(app_agent_id)
        return_data.update(get_device_list_and_count(request))
        return render(request, 'applications/illuminance_light_control.html', return_data)
    elif app_type.app_name == 'fault_detection':
        return_data = fault_detection_info(app_agent_id)
        return_data.update(get_device_list_and_count(request))
        return render(request, 'applications/fault_detection.html', return_data)
    elif app_type.app_name in ['plugload_scheduler','lighting_scheduler']:
        app_data = running_app.app_data
        device_mac = app_data['device_agent_id'].split('_')[-1]
        return redirect('view-device-schedule',device_mac)



def fault_detection_info(app_agent_id):
    data = {}

    app_info = ApplicationRunning.objects.get(app_agent_id=app_agent_id)
    thermostat_agent_id = app_info.app_data['thermostat']
    thermostat = DeviceMetadata.objects.filter(agent_id=thermostat_agent_id)[0]
    data.update({'thermostat': thermostat,'app_info': app_info, 'app_id': app_agent_id})
    return data

def illuminance_based_control(app_agent_id):
    data = {}
    available_lights = DeviceMetadata.objects.filter(approval_status='APR', device_type_id=2)
    controllable_lights = list()
    for light in available_lights:
        dev_data = Devicedata.objects.filter(agent_id=light.agent_id)
        if dev_data and 'brightness' in dev_data[0].data:
            controllable_lights.append(light)

    #TODO: currently there is no flag for light sensor, device model should not be hardcoded, should be updated later.
    available_sensors = DeviceMetadata.objects.filter(approval_status='APR', device_type_id=4, device_model='LMLS-400')
    app_info = ApplicationRunning.objects.get(app_agent_id=app_agent_id)
    data.update({'lights':controllable_lights, 'sensors':available_sensors, 'app_id': app_agent_id,
                 'app_info':app_info})

    return data

@login_required(login_url='/login/')
def save_and_start(request):
    if request.POST:
        # 1. Save configuration data
        _data = request.body
        _data = json.loads(_data)
        app_agent_id = _data['app_id']
        app_data = _data['app_data']
        save_app_data(app_agent_id, app_data)
        # 2. Start application
        message_to_agent = {
            "auth_token": "bemoss"
        }
        subtopic = app_agent_id.split('_')
        message = dict()
        message[STATUS_CHANGE.AGENT_ID] = app_agent_id
        message[STATUS_CHANGE.NODE] = "0"
        message[STATUS_CHANGE.AGENT_STATUS] = 'start'
        message[STATUS_CHANGE.NODE_ASSIGNMENT_TYPE] = ZONE_ASSIGNMENT_TYPES.PERMANENT
        message['is_app'] = True

        topic = 'to/networkagent/status_change/from/ui'
        vip_publish(topic, [message])
        topic = 'to/'+app_agent_id+'/update/from/ui'
        vip_publish(topic, "update")

        if request.is_ajax():
            return HttpResponse(json.dumps("success"))

@login_required(login_url='/login/')
def update_target_illuminance(request):
    if request.POST:
        # 1. Save configuration data
        _data = request.body
        _data = json.loads(_data)
        app_id = _data[0]
        target = _data[1]
        try:
            message_to_agent = {
                "auth_token": "bemoss",
                "target": int(target)
            }
            ieb_topic = 'to/' + app_id + '/from/ui/update_target'
            vip_publish(ieb_topic, json.dumps(message_to_agent))

            if request.is_ajax():
                return HttpResponse(json.dumps("success"))
        except ValueError:
            if request.is_ajax():
                return HttpResponse(json.dumps("invalid target"))

@login_required(login_url='/login/')
def calibrate(request):
    if request.POST:
        # 1. Save configuration data
        _data = request.body
        _data = json.loads(_data)
        app_id = _data
        # 2. Start application
        message_to_agent = {
            "auth_token": "bemoss"
        }
        ieb_topic = 'to/'+app_id+'/from/ui/calibrate'
        vip_publish(ieb_topic, json.dumps(message_to_agent))

        if request.is_ajax():
            return HttpResponse(json.dumps("success"))


def save_app_data(app_agent_id, app_data):
    app = ApplicationRunning.objects.get(app_agent_id=app_agent_id)
    for key, value in app_data.items():
        app.app_data[key] = value
    app.save()