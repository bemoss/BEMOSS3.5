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
import json
import datetime
from django.http import HttpResponse
from _utils.device_list_utils import get_device_list_and_count
from collections import OrderedDict
from webapps.deviceinfos.models import DeviceMetadata, SupportedDevices
from webapps.device.models import Devicedata

from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, render
import numpy
import itertools
import os
import sys
import pytz
#sys.path.insert(0,os.path.expanduser('~/BEMOSS/'))
from bemoss_lib.databases.cassandraAPI.cassandraDB import retrieve
from bemoss_lib.utils import date_converter
import settings

def parse_resultset(variables, data_point, result_set, last_date=None):
    if len(result_set)>0 and type(result_set[0][variables.index(data_point)]) in [str,unicode]:
        return []
    try:
        x = [[lst[variables.index('time')], lst[variables.index(data_point)]+0.0]
                for lst in result_set if lst[variables.index(data_point)] is not None]
    except TypeError:
        return []
    if len(x) == 0:
        return []
    #sort based on time
    x=sorted(x, key=lambda n: n[0])
    #interleave redundant data to make it step-plot
    if last_date==None:
        last_date=datetime.datetime.utcnow()
    else:
        last_date = date_converter.localToUTC(last_date)

    last_time = int((last_date-datetime.datetime(1970,1,1)).total_seconds()*1000)
    old = numpy.array(x)
    newTime = numpy.append(old[1:,0],last_time)-1.0 #decrease one millisecond time to arrange for chronological order
    newList = numpy.vstack((newTime,old[:,1])).transpose().tolist()
    old = old.tolist()
    finalResult = list(itertools.chain(*zip(old,newList)))
    return finalResult



def returnChartsPage(request, context,mac,data_variables,page,get_weather=False):
    '''
    :param context: var obtained from RequestContext(request)
    :param mac: Device mac ID (table id)
    :param data_variables: Dict. Variables in the database that is to be retrieved as value, and varaibles in html as keys
    :param page: The html page to be returned to
    :param device_type: The device type class
    :return: the rendered html page
    '''
    agent_id = get_agent_id_from_mac(mac)
    try:
        if not get_weather:
            varlist, rs = retrieve(agent_id)
        else:
            data = retrieve(agent_id, weather_agent=settings.weather_agent)
            if data is not None:
                varlist, rs=data
            else:
                varlist, rs = retrieve(agent_id)
    except Exception as er:
        print er
        print 'Cassandra data reading error'
        return {}

    device_list_side_nav = get_device_list_and_count(request)

    data_dict = {}
    objects = [ob for ob in DeviceMetadata.objects.filter(mac_address=mac)]
    try:
        device_nickname = objects[0].nickname
        node_name = objects[0].node.node_name
        data_dict = {'mac': mac, 'nickname': device_nickname, 'node_name': node_name}
    except Exception as er:
        print er
        print 'get device status failed'

    for key,val in data_variables.items():
        try:
            data_dict[key] = parse_resultset(varlist,val,rs)
        except (KeyError, ValueError) as er:
            print er
            continue

    context.update(get_device_list_and_count(request))
    data_dict.update(device_list_side_nav)
    return render(request, page,data_dict)

def returnsCharts(request,data_variables,get_weather=False):

    _data = request.body
    _data = json.loads(_data)
    mac = _data['mac']
    if 'from_dt' in _data.keys():
        from_date = _data['from_dt']
        if from_date not in [None,'',u'']:
            if type(from_date) in [str,unicode]:
                from_date = datetime.datetime.strptime(from_date, '%Y/%m/%d %H:%M')
        else:
            from_date = None
        print from_date
    else:
        from_date = None


    if 'to_dt' in _data.keys():
        to_date = _data['to_dt']
        if to_date not in [None,'',u'']:
            if type(to_date) in [str,unicode]:
                to_date = datetime.datetime.strptime(to_date, '%Y/%m/%d %H:%M')
        else:
            to_date = None
    else:
        to_date = None

    if from_date is None and to_date is None:
        to_date = datetime.datetime(2017, 2, 4)
        from_date = datetime.datetime(2017, 1, 1)

    agent_id = get_agent_id_from_mac(mac)
    if get_weather:
        varlist, rs = retrieve(agent_id,startTime=from_date,endTime=to_date,weather_agent=settings.weather_agent)
    else:
        varlist, rs = retrieve(agent_id,startTime=from_date,endTime=to_date)
    #varlist, rs = retrieve(agent_id, weather_agent="weatheragent22101", )
    json_result =dict()
    for key,val in data_variables.items():
        if key in varlist:
            json_result[key] = parse_resultset(varlist,val,rs,to_date)

    if request.is_ajax():
            return HttpResponse(json.dumps(json_result))

@login_required(login_url='/login/')
def charts_device(request, mac):
    context = RequestContext(request)
    objects = [ob for ob in DeviceMetadata.objects.filter(mac_address=mac)]
    #Todo make device model a foreign key
    device_model = objects[0].device_model
    supported_device = SupportedDevices.objects.get(device_model=device_model)
    chart_page = supported_device.chart_template
    agent_id = get_agent_id_from_mac(mac)
    data = Devicedata.objects.get(agent_id=agent_id)


    data_variables = dict()
    for item in data.data.keys():
        data_variables[item] = item

    if supported_device.device_type.device_type == "HVAC":
        get_weather = True
        weather_vars = ['weather_temperature', 'weather_humidity', 'weather_pressure', 'weather_v_wind',
                        'weather_sky_condition']
        for v in weather_vars:
            data_variables[v] = v
    else:
        get_weather = False


    if request.method == 'GET':
        return returnChartsPage(request, context, mac, data_variables, chart_page, get_weather=get_weather)
    elif request.method == 'POST':
        return returnsCharts(request,data_variables,get_weather=get_weather)

    '''
    thermostat
        data_variables = {'temperature':'temperature','heat_setpoint':'heat_setpoint','cool_setpoint':'cool_setpoint'}
    vav
        data_variables = {'temperature':'temperature', 'supply_temperature':'supply_temperature','heat_setpoint':'heat_setpoint', 'cool_setpoint':'cool_setpoint', 'flap_position':'flap_position'}
    rtu
        data_variables = {'outside_temperature':'outside_temperature', 'return_temperature':'return_temperature', 'supply_temperature':'supply_temperature',
                                  'heat_setpoint':'heat_setpoint', 'cool_setpoint':'cool_setpoint', 'cooling_mode':'cooling_mode', 'heating':'heating',
                                  'outside_damper_position':'outside_damper_position', 'bypass_damper_position':'bypass_damper_position'}
    lighting
        data_variables ={'status':'status', 'brightness':'brightness'}
    plugload
        data_variables = {'status':'status','power':'power'}

    '''


def get_agent_id_from_mac(mac):
    device_metadata = [ob.device_control_page_info() for ob in DeviceMetadata.objects.filter(mac_address=mac)]
    print device_metadata
    agent_id = device_metadata[0]['agent_id']
    return agent_id


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

def export_time_series_data_spreadsheet(request, mac):

    if request.method == 'POST':
        print 'inside export to spreadsheet for power meter based on given from and to datetime'
        _data = request.body
        print _data
        _data = json.loads(_data)
        from_date = _data['from_dt']
        to_date = _data['to_dt']
        agent_id = get_agent_id_from_mac(mac)
        data = Devicedata.objects.get(agent_id=agent_id)
        data_variables = dict()
        for item in data.data.keys():
            data_variables[item] = item
        device_status = [ob.data_as_json() for ob in Devicedata.objects.filter(agent_id=agent_id)]
        if device_status[0]["device_type"] == "hvac" or device_status[0]["device_type"] == "HVAC":
            weather_agent = True
        else:
            weather_agent=False
        if not from_date and not to_date:
            data_points, rs = retrieve_for_export(agent_id,weather_agent=weather_agent)
        elif not to_date and from_date:
            from_date = datetime.datetime.strptime(from_date, '%Y/%m/%d %H:%M')
            data_points, rs = retrieve_for_export(agent_id,
                                                  startTime=from_date,weather_agent=weather_agent)
        else:
            from_date = datetime.datetime.strptime(from_date, '%Y/%m/%d %H:%M')
            to_date = datetime.datetime.strptime(to_date, '%Y/%m/%d %H:%M')
            data_points, rs = retrieve_for_export(agent_id,
                                                  startTime=from_date, endTime=to_date,weather_agent=weather_agent)
        _data = list()
        single_entry=dict()
        if weather_agent:
            data_variables["weather_temperature"] = "weather_temperature"
        for lst in rs:

            for variable in data_variables.values():
                if variable in data_points:
                    single_entry[variable]=lst[data_points.index(variable)]

            single_entry["time"] = lst[data_points.index('time')]
            preffered_key_order = ['time'] + sorted(single_entry.keys())
            new_ordered_dict = OrderedDict()
            for key in preffered_key_order:
                new_ordered_dict[key] = single_entry[key]
            _data.append(new_ordered_dict)
        if request.is_ajax():
            return HttpResponse(json.dumps(_data))
    else:
        return []



def retrieve_for_export(agentID, vars=None, startTime=None, endTime=None, tablename=None,weather_agent=False):
    if weather_agent:
        data = retrieve(agentID=agentID,vars=vars,startTime=startTime,endTime=endTime,export=True,tablename=tablename,weather_agent=settings.weather_agent)
        if data is not None:
            a,b=data
        else:
            a, b = retrieve(agentID=agentID, vars=vars, startTime=startTime, endTime=endTime, export=True,
                            tablename=tablename, weather_agent=None)
    else:
        a, b = retrieve(agentID=agentID, vars=vars, startTime=startTime, endTime=endTime, export=True,
                        tablename=tablename, weather_agent=None)
    return a,b


