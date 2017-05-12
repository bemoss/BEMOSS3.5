import json

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from webapps.bemoss_applications.models import ApplicationRunning
from webapps.deviceinfos.models import DeviceMetadata

from _utils.device_list_utils import get_device_list_and_count
from bemoss_lib.utils.VIP_helper import vip_publish

# Create your views here.

@login_required(login_url='/login/')
def application_main(request):
    # Display the main page of bemoss applications
    pass
    # return render(request, template, return_data)

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
    available_sensors = DeviceMetadata.objects.filter(approval_status='APR', device_type_id=4)
    data.update({'lights':available_lights, 'sensors':available_sensors, 'app_id': app_id})

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
    pass

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