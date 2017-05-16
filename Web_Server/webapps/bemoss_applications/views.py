import json

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from datetime import datetime

from webapps.bemoss_applications.models import ApplicationRunning
from webapps.deviceinfos.models import DeviceMetadata

from _utils.device_list_utils import get_device_list_and_count
from bemoss_lib.utils.VIP_helper import vip_publish

# Create your views here.

@login_required(login_url='/login/')
def application_main(request):
    # Display the main page of bemoss applications
    iblc_apps = ApplicationRunning.objects.filter(app_type='IBLC')
    return_data = {'iblc_apps': iblc_apps}
    return_data.update(get_device_list_and_count(request))
    return render(request, 'applications/applications.html', return_data)

def application_add(request):
    if request.POST:
        # 1. Save configuration data
        _data = request.body
        _data = json.loads(_data)
        if _data == 'iblc':
            no = ApplicationRunning.objects.filter(app_type='IBLC').count()+1
            new_app_id = 'iblc_app'+str(no)
            total_app = ApplicationRunning.objects.filter().count() + 1
            new_app = ApplicationRunning(id=total_app, start_time=datetime.now(),status='stopped',
                                      app_type='IBLC', app_data={}, app_agent_id=new_app_id)
            new_app.save()
            success = True

        if success:
            if request.is_ajax():
                return HttpResponse(json.dumps("success"))

@login_required(login_url='/login/')
def application_individual(request, app_id):
    app_type = ApplicationRunning.objects.get(app_agent_id=app_id).app_type
    if app_type == 'IBLC':
        return_data = illuminance_based_control(app_id)
        return_data.update(get_device_list_and_count(request))
        return render(request, 'applications/illuminance_light_control.html', return_data)

def illuminance_based_control(app_id):
    data = {}
    available_lights = DeviceMetadata.objects.filter(approval_status='APR', device_type_id=2)
    #TODO: currently there is no flag for light sensor, device model should not be hardcoded, should be updated later.
    available_sensors = DeviceMetadata.objects.filter(approval_status='APR', device_type_id=4, device_model='LMLS-400')
    app_info = ApplicationRunning.objects.get(app_agent_id=app_id)
    data.update({'lights':available_lights, 'sensors':available_sensors, 'app_id': app_id,
                 'app_info':app_info})

    return data

@login_required(login_url='/login/')
def save_and_start(request):
    if request.POST:
        # 1. Save configuration data
        _data = request.body
        _data = json.loads(_data)
        app_id = _data[0]
        app_data = {'lights': _data[1], 'sensors': _data[2]}
        save_app_data(app_id, app_data)
        # 2. Start application
        message_to_agent = {
            "auth_token": "bemoss"
        }
        subtopic = app_id.split('_')
        ieb_topic = 'to/applauncheragent/' + subtopic[0] + '/' + subtopic[1] + '/launch'
        print ieb_topic
        vip_publish(ieb_topic, json.dumps(message_to_agent))

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
def caliberate(request):
    if request.POST:
        # 1. Save configuration data
        _data = request.body
        _data = json.loads(_data)
        app_id = _data
        # 2. Start application
        message_to_agent = {
            "auth_token": "bemoss"
        }
        ieb_topic = 'to/'+app_id+'/from/ui/caliberate'
        vip_publish(ieb_topic, json.dumps(message_to_agent))

        if request.is_ajax():
            return HttpResponse(json.dumps("success"))


def save_app_data(app_id, app_data):
    app = ApplicationRunning.objects.get(app_agent_id=app_id)
    app.app_data = app_data
    app.save()