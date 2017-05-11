from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from _utils.device_list_utils import get_device_list_and_count
from webapps.deviceinfos.models import Miscellaneous
from webapps.deviceinfos.models import SupportedDevices, Miscellaneous
import json
import _utils.defaults as __
import ast
from volttron.platform.vip.agent import Core, Agent
from volttron import platform
from volttron.platform.agent import utils
import gevent
from django.forms.models import modelformset_factory
from webapps.discovery.forms import PasswordManagerForm
from webapps.discovery.models import PasswordsManager

from _utils.encrypt import encrypt_value
import json
import os
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from datetime import datetime
from django.db import IntegrityError
from _utils.device_list_utils import get_device_list_and_count
import django_web_server.settings_tornado
from webapps.device.models import Devicedata
from webapps.schedule.models import Holiday
from webapps.discovery.models import PasswordsManager
from webapps.multinode.models import NodeInfo



from bemoss_lib.utils.VIP_helper import vip_publish
kwargs = {'subscribe_address': __.SUB_SOCKET,
          'publish_address': __.PUSH_SOCKET}


@login_required(login_url='/login')
def discover_devices(request):
    if request.user.groups.filter(name__iexact = 'admin').exists():
        context = RequestContext(request)
        try:
            discovery_status = Miscellaneous.objects.get(key='auto_discovery')
            print discovery_status.value
        except Miscellaneous.DoesNotExist:
            discovery_status = {'value':'not_started'}

        hvac = SupportedDevices.objects.filter(device_type_id=1)
        lt_loads = SupportedDevices.objects.filter(device_type_id=2)
        plugloads = SupportedDevices.objects.filter(device_type_id=3)
        sensors = SupportedDevices.objects.filter(device_type_id=4)
        power_meters = SupportedDevices.objects.filter(device_type_id=5)
        DER=SupportedDevices.objects.filter(device_type_id=6)
        camera=SupportedDevices.objects.filter(device_type_id=7)
        print lt_loads
        print hvac
        print power_meters
        print plugloads
        print sensors
        print DER

        device_list_side_nav = get_device_list_and_count(request)
        return_data = dict()
        return_data.update(device_list_side_nav)
        devices = {'hvac': hvac, 'lt_loads':lt_loads, 'plugloads':plugloads, 'sensors':sensors, 'power_meters':power_meters, "DER": DER, "camera":camera}
        return_data.update(devices)
        return_data.update({'discovery_status':discovery_status})

        return render(request,'discovery/manual_discovery.html', return_data
                                  )
    else:
        return HttpResponseRedirect('/home/')


def discover_new_devices(request):
    if request.POST:
        _data = request.body
        _data = json.loads(_data)
        _data = [x.encode('utf-8') for x in _data]
        print _data
        message = {'devices': _data}
        print message
        print type(message)

        topic = 'to/devicediscoveryagent/discovery_request/from/ui'
        topic2 = 'to/devicediscoveryagent/from/ui/discovery_request'
        vip_publish(topic,_data)
        vip_publish(topic2, _data)

        if request.is_ajax():
            return HttpResponse(json.dumps("success"))

def authenticate_device(request):
    if  request.method == 'POST' and request.body:
        _data = request.body
        _data = ast.literal_eval(_data)
        print _data
        agent_id = _data['agent_id']
        message = {'agent_id': agent_id}
        print message
        print type(message)

        topic = 'to/approvalhelperagent/get_device_username/from/ui'

        vip_publish(topic,message)

        if request.is_ajax():
            return HttpResponse(json.dumps("success"), 'application/json')
