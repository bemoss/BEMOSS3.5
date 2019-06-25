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


from _utils.device_list_utils import get_device_list_and_count
from bemoss_lib.utils.encrypt import decrypt_value
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse
from webapps.deviceinfos.models import DeviceMetadata, Miscellaneous, SupportedDevices
from _utils import config_helper
from _utils import device_list_utils as _helper

import httplib
import os
import time
import json
import urllib2
import logging
from django_web_server import settings
from django_web_server import settings_tornado
import _utils.defaults as __

from volttron.platform.agent import utils
from bemoss_lib.utils.VIP_helper import vip_publish

utils.setup_logging()
logger = logging.getLogger(__name__)


def get_zip_code():
    try:
        location_info = urllib2.urlopen('http://ipinfo.io/json').read()
        location_info_json = json.loads(location_info)
        zipcode = location_info_json['postal'].encode('ascii', 'ignore')
        return zipcode
    except urllib2.HTTPError, e:
        logger.error('HTTPError = ' + str(e.code))
    except urllib2.URLError, e:
        logger.error('URLError = ' + str(e.reason))
    except httplib.HTTPException, e:
        logger.error('HTTPException = ' + str(e.message))
    except Exception:
        import traceback
        logger.error('generic exception: ' + traceback.format_exc())

def get_weather_info():
    #Get current weather data from wunderground
    try:
        zipcode = Miscellaneous.objects.get(key='zipcode').value
    except:
        zipcode = '22203'

    # Get the zip according to your IP, if available:
    ip_zipcode = get_zip_code()
    # our default zip code is 22203, if we can obtain your location based on your IP, we will update it below.
    if zipcode == '22203' and ip_zipcode is not None:
        zipcode = ip_zipcode

    #rs = {}
    try:
        # Get weather underground service key
        wu_key = settings.WUNDERGROUND_KEY
        rs = urllib2.urlopen("http://api.wunderground.com/api/" + wu_key + "/conditions/q/" + zipcode + ".json")
    except urllib2.HTTPError, e:
        logger.error('HTTPError = ' + str(e.code))
    except urllib2.URLError, e:
        logger.error('URLError = ' + str(e.reason))
    except httplib.HTTPException, e:
        logger.error('HTTPException = ' + str(e.message))
    except Exception:
        import traceback
        logger.error('generic exception: ' + traceback.format_exc())
    #print rs
    #print zipcode

    #json_string = rs.read() if rs != {} else {}
    try:
        #parsed_json = json.loads(json_string)
        location = 'Arlington, VA (Default, please update settings)'
        temp_f = '77'
        humidity = '10%'
        precip ='0.0'
        winds = '1.0'
        icon = 'mostlysunny'
        weather = 'Sunny'
    except Exception:
        location = 'Arlington, VA (Default, please update settings)'
        temp_f = '77'
        humidity = '10%'
        precip = '0.0'
        winds = '1.0'
        icon = 'mostlysunny'
        weather = 'Sunny'

    weather_icon = config_helper.get_weather_icon(icon)

    weather_info = {'location':location, 'temp_f':temp_f, 'humidity':humidity, 'precip':precip, 'winds':winds, 'weather':
        weather, 'weather_icon':weather_icon,'zip_code':22311}

    return weather_info

@login_required(login_url='/login/')
def devicedata_view(request, mac):
    if request.method == 'GET':
        device_info = DeviceMetadata.objects.get(mac_address=mac)
        template = SupportedDevices.objects.filter(device_model=device_info.device_model).values('html_template')[0]['html_template']
        context = RequestContext(request)
        username = request.session.get('user')
        agent_id = device_info.agent_id
        _data = _helper.get_page_load_data(agent_id)
        device_list_side_nav = get_device_list_and_count(request)

        weather_info = get_weather_info()
        return_data = {'device_info': device_info, 'device_data': _data, 'weather_info':weather_info}
        return_data.update(device_list_side_nav)
        context.update({'return_data': return_data})

        return render(request, template, return_data)


@login_required(login_url='/login/')
def submit_devicedata(request):
    if request.method == 'POST':
        _data = request.body
        _data = json.loads(_data)
        agent_id = _data['agent_id']
        update_send_topic = 'to/' + agent_id + '/update/from/ui'
        update_send_topic2 = 'to/' + agent_id + '/from/ui/update'

        print update_send_topic
        vip_publish(update_send_topic, _data)
        vip_publish(update_send_topic2, _data)

        if request.is_ajax():
            return HttpResponse(json.dumps(_data))


@login_required(login_url='/login/')
def weather(request):
    print os.path.basename(__file__) + "in weather function"
    if request.method == 'GET':
        weather_info = get_weather_info()

        jsonresult = {
            'locat': weather_info[0],
            'temp_f': weather_info[1],
            'humidity': weather_info[2],
            'precip': weather_info[3],
            'winds': weather_info[4],
            'icon': weather_info[6],
            'weather': weather_info[5]
        }
        print json.dumps(jsonresult)
        if request.is_ajax():
            return HttpResponse(json.dumps(jsonresult), content_type='application/json')
