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

#__author__ =  "BEMOSS Team"
#__credits__ = ""
#__version__ = "3.5"
#__maintainer__ = "BEMOSS Team"
#__email__ = "aribemoss@gmail.com"
#__website__ = "www.bemoss.org"
#__created__ = "2016-10-11"
#__lastUpdated__ = "2016-10-11"
'''

'''This API class is for an agent that want to communicate/monitor/control
devices that compatible with Philips Hue'''

import socket
import time
import urllib2
import json
from DeviceAPI.BaseAPI import baseAPI
from bemoss_lib.utils import rgb_cie
from ast import literal_eval
from bemoss_lib.utils.BEMOSS_ONTOLOGY import BEMOSS_ONTOLOGY
from xml.dom import minidom
import re
from bemoss_lib.protocols.discovery.SSDP import SSDP
import pprint
import requests

class API(baseAPI):

    def __init__(self,**kwargs):
        super(API, self).__init__(**kwargs)
        # Initialized common attributes
        self.variables = kwargs
        self.debug = True
        self.set_variable('offline_count', 0)
        self.set_variable('connection_renew_interval', 6000)  # nothing to renew, right now
        self.only_white_bulb = None
        # to initialize the only white bulb value
        # self.getDeviceStatus()
        self._debug = True

    def API_info(self):
        return [{'device_model' : 'Philips hue bridge', 'vendor_name' : 'Royal Philips Electronics', 'communication' : 'WiFi',
                'device_type_id' : 2, 'api_name': 'API_PhilipsHue','html_template':'lighting/lighting.html',
                'agent_type':'BasicAgent','identifiable' : True, 'authorizable': True, 'is_cloud_device' : False,
                'schedule_weekday_period' : 4,'schedule_weekend_period' : 4, 'allow_schedule_period_delete' : True,'chart_template': 'charts/charts_lighting.html'}]

    def dashboard_view(self):
        if self.get_variable(BEMOSS_ONTOLOGY.STATUS.NAME) == BEMOSS_ONTOLOGY.STATUS.POSSIBLE_VALUES.ON:
            return {"top": None, "center": {"type": "image", "value": 'bulbon.png'},
            "bottom": BEMOSS_ONTOLOGY.STATUS.NAME}
        else:
            return {"top": None, "center": {"type": "image", "value": 'bulboff.png'},
            "bottom": BEMOSS_ONTOLOGY.STATUS.NAME}

    def ontology(self):
        return {"on": BEMOSS_ONTOLOGY.STATUS, "bri": BEMOSS_ONTOLOGY.BRIGHTNESS,
                "hexcolor": BEMOSS_ONTOLOGY.HEXCOLOR}

    def discover(self):
        group = ("239.255.255.250", 1900)
        message = "\r\n".join([
            'M-SEARCH * HTTP/1.1',
            'HOST: {0}:{1}',
            'MAN: "ssdp:discover"',
            'ST: {st}', 'MX: 3', '', ''])
        service = "urn:schemas-upnp-org:device:Basic:1"
        message = message.format(*group, st=service)
        SSDPobject = SSDP(message)
        responses = SSDPobject.request()
        if self._debug: print responses
        discovered_devices = list()
        addresslist = list()
        for response in responses:
            if (":80/description.xml" in response ) and (response not in addresslist):
                print "response {}".format(response)
                deviceUrl = urllib2.urlopen(response)
                dom = minidom.parse(deviceUrl)

                deviceModel = dom.getElementsByTagName('modelName')[0].firstChild.data
                macid = dom.getElementsByTagName('serialNumber')[0].firstChild.data
                deviceVendor = 'Philips'
                if "Philips hue bridge" in deviceModel:
                    deviceModel = "Philips hue bridge"
                    deviceVendor = dom.getElementsByTagName('manufacturer')[0].firstChild.data
                    deviceUrl.close()
                addresslist.append(response)
                address = response.replace('/description.xml', '')
                discovered_devices.append({'address': address, 'mac': macid, 'model': deviceModel,
                                           'vendor': deviceVendor})
        if self._debug == True:
            pprint.pprint(discovered_devices)
        return discovered_devices

    def renewConnection(self):
       self.discover()

    on_dict = {True: BEMOSS_ONTOLOGY.STATUS.POSSIBLE_VALUES.ON,
           False: BEMOSS_ONTOLOGY.STATUS.POSSIBLE_VALUES.OFF}

    # GET Open the URL and read the data
    def getDataFromDevice(self):
        devicedata = dict()
        _hue_username = self.get_variable("username")
        _url_append = '/api/' + _hue_username + '/groups/0/'
        _urlData = self.get_variable("address").replace(':80', _url_append)
        try:
            _deviceUrl = urllib2.urlopen(_urlData, timeout=20)
            print(" {0}Agent is querying its current status (status:{1}) please wait ...".
                  format(self.variables.get('agent_id', None), _deviceUrl.getcode()))
            if (_deviceUrl.getcode() == 200):
                data = _deviceUrl.read().decode("utf-8")
                # Use the json module to load the string data into a dictionary
                _theJSON = json.loads(data)
                # 1. status
                devicedata['on'] = self.on_dict[_theJSON["action"]['on']]
                # 2. brightness convert to %
                devicedata["bri"] = int(round(float(_theJSON["action"]["bri"]) * 100 / 255, 0))
                # update only white variable every round is necessary in case user add a/take away all color bulb(s).
                self.only_white_bulb = False if 'hue' in _theJSON["action"].keys() else True
                if self.only_white_bulb is False:
                    # 3. color convert to RGB 0-255
                    # hue = _theJSON["action"]["hue"]
                    # xy = _theJSON["action"]["xy"]
                    # ct = _theJSON["action"]["ct"]
                    x = _theJSON["action"]["xy"][0]
                    y = _theJSON["action"]["xy"][1]
                    devicedata['color'] = rgb_cie.ColorHelper.getRGBFromXYAndBrightness(x, y, _theJSON["action"]["bri"])
                    devicedata['hexcolor'] = '#%02x%02x%02x' % devicedata['color']
                    # 4. saturation convert to %
                    # sat = int(round(float(_theJSON["action"]["sat"]) * 100 / 255, 0))
                    # effect = _theJSON["action"]["effect"]
                    # colormode = _theJSON["action"]["colormode"]
                # for k in _theJSON["lights"]:
                #     self.set_variable("lights{}".format(k), k)
                # number_lights = len(_theJSON["lights"])
                # name = _theJSON["name"]
            else:
                print(" Received an error from server, cannot retrieve results " + str(_deviceUrl.getcode()))
        except Exception as er:
            print er
            print('ERROR: API_PhilipsHue failed to getDeviceStatus')

        print devicedata
        return devicedata

    def setDeviceData(self, postmsg):
        # Ex. postmsg = {"on":True,"bri":100,"hue":50260,"sat":200}
        _hue_username = self.get_variable("username")
        _url_append = '/api/' + _hue_username + '/groups/0/'
        _urlData = self.get_variable("address").replace(':80', _url_append)
        if self.isPostmsgValid(postmsg) == True:  # check if the data is valid
            temp=self.convertPostMsg(postmsg)
            _data = json.dumps(temp)
            _data = _data.encode(encoding='utf_8')
            _request = urllib2.Request(_urlData + 'action')
            _request.add_header('Content-Type', 'application/json')
            _request.get_method = lambda: 'PUT'
            try:
                _f = urllib2.urlopen(_request, _data, timeout=20)  # when include data this become a POST command
                print(" {0}Agent for {1} is changing its status with {2} please wait ..."
                      .format(self.variables.get('agent_id', None), self.variables.get('model', None), postmsg))
                print(" after send a POST request: {}".format(_f.read().decode('utf-8')))
            except:
                print("ERROR: API_PhilipsHue connection failure! @ setDeviceStatus")
        else:
            print("The POST message is invalid, try again\n")


    def isPostmsgValid(self,postmsg):  # check validity of postmsg
        dataValidity = True
        # TODO algo to check whether postmsg is valid
        return dataValidity

    def convertPostMsg(self, postmsg):
        msgToDevice = {}
        datacontainsRGB = False
        if BEMOSS_ONTOLOGY.COLOR.NAME in postmsg.keys():
            datacontainsRGB = True

        for k, v in postmsg.items():
            if k == BEMOSS_ONTOLOGY.STATUS.NAME:
                msgToDevice[self.dict_rev_translate(self.ontology(), BEMOSS_ONTOLOGY.STATUS)] = self.dict_rev_translate(self.on_dict, postmsg[k])
            elif k == BEMOSS_ONTOLOGY.BRIGHTNESS.NAME:
                msgToDevice[self.dict_rev_translate(self.ontology(), BEMOSS_ONTOLOGY.BRIGHTNESS)] = int(round(float(postmsg[k]) * 255.0 / 100.0, 0))
            elif k == BEMOSS_ONTOLOGY.COLOR.NAME:
                if self.only_white_bulb is False:
                    if type(postmsg[k])==str:
                        postmsg[k] = literal_eval(postmsg[k])
                    print(type(postmsg[k]))
                    _red = postmsg[k][0]
                    _green = postmsg[k][1]
                    _blue = postmsg[k][2]
                    _xyY = rgb_cie.ColorHelper.getXYPointFromRGB(_red, _green, _blue)
                    msgToDevice['xy'] = [_xyY.x, _xyY.y]
                    # msgToDevice['bri']= int(round(_xyY.y*255,0))
            elif k == 'hue':
                if datacontainsRGB == False and self.only_white_bulb is False:
                    msgToDevice['hue'] = postmsg.get('hue')
            elif k == 'saturation':
                if datacontainsRGB == False and self.only_white_bulb is False:
                    msgToDevice['sat'] = int(round(float(postmsg.get('saturation')) * 255.0 / 100.0, 0))
            else:
                msgToDevice[k] = v
        return msgToDevice

    def identifyDevice(self):
        identifyDeviceResult = False
        print(" {0}Agent for {1} is identifying itself by doing colorloop. Please observe your lights"
              .format(self.variables.get('agent_id', None), self.variables.get('model', None)))
        try:
            devicewasoff = 0
            if self.get_variable('status') == "OFF":
                devicewasoff = 1
                self.setDeviceStatus({"status": "ON"})
            elif self.only_white_bulb:
                self.setDeviceStatus({"status": "OFF"})
            if self.only_white_bulb is False:
                self.setDeviceStatus({"effect": "colorloop"})
            if self.only_white_bulb:
                time_iden = 3
            else:
                time_iden = 10  # time to do identification
            t0 = time.time()
            self.seconds = time_iden
            while time.time() - t0 <= time_iden:
                self.seconds = self.seconds - 1
                print("wait: {} sec".format(self.seconds))
                time.sleep(1)
            self.setDeviceStatus({"effect": "none"})
            if devicewasoff == 1:
                self.setDeviceStatus({"status": "OFF"})
            else:
                self.setDeviceStatus({"status": "ON"})
            identifyDeviceResult = True
        except:
            print("ERROR: classAPI_PhilipsHue connection failure! @ identifyDevice")
        return identifyDeviceResult

    def query_username(self):
        # newdeveloper is for the old version of Hue hub, might no longer be useful in future version.
        url = self.get_variable("address") + '/api/newdeveloper'
        req = requests.get(url)
        result = json.loads(req.content)
        message = json.dumps(result)
        message = message.encode(encoding='utf_8')

        substring = "unauthorized user"
        no_name = substring in message

        if no_name:
            cnt = 60
            while cnt > 0:
                body = {"devicetype": "my_hue_app#bemoss"}
                url = self.get_variable("address") + '/api'

                r = requests.post(url, json.dumps(body))
                print r.content
                substring = "link button not pressed"
                if substring in r.content:
                    time.sleep(0.5)
                    cnt -= 1
                    print cnt
                else:
                    exp = '\"username\":\"(.*?)\"'
                    pattern = re.compile(exp, re.S)
                    result = re.findall(pattern, r.content)
                    hub_name = result[0]
                    break
        else:
            hub_name = 'newdeveloper'

        return hub_name


# This main method will not be executed when this class is used as a module
def main():
    # Step1: create an object with initialized data from DeviceDiscovery Agent
    # requirements for instantiation1. model, 2.type, 3.api, 4. address
    PhilipsHue = API(model='Philips Hue',type='wifiLight',api='API_PhilipsHue',address='http://192.168.10.116:80',username='djaRJvXdtrP-Xdk9nuBUeSinEgC7TqLESst04oTZ',agent_id='BasicAgent')
    PhilipsHue.discover()
    PhilipsHue.getDataFromDevice()
    PhilipsHue.setDeviceData({'status': 'ON', 'color':'(87,145,255)'})
    # PhilipsHue.identifyDevice()

if __name__ == "__main__":
    main()
