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

#__author__ = "Mengmeng Cai"
#__credits__ = ""
#__version__ = "3.5"
#__maintainer__ = "BEMOSS Team"
#__email__ = "aribemoss@gmail.com"
#__website__ = "www.bemoss.org"
#__created__ = "2016-10-11"
#__lastUpdated__ = "2016-11-01"
'''

'''This API class is for an agent that want to communicate/monitor/control
devices that compatible with WeMo plugload'''

import re
import requests
from xml.dom import minidom
import time
import json
import datetime
import urllib2
from DeviceAPI.BaseAPI import baseAPI
from bemoss_lib.utils.BEMOSS_ONTOLOGY import BEMOSS_ONTOLOGY
from bemoss_lib.protocols.discovery.SSDP import SSDP
import pprint


class baseAPI_WeMo(baseAPI):

    def __init__(self,**kwargs):
        super(baseAPI_WeMo, self).__init__(**kwargs)
        self.variables = kwargs
        self._debug = True

        self.set_variable('connection_renew_interval', 600)
        self.listeningThread = None
        self.set_variable('offline_count', 0)

    def API_info(self):
        return

    def dashboard_view(self):
        return

    def ontology(self):
        return

    def discover(self):
        group = ("239.255.255.250", 1900)
        message = "\r\n".join([
            'M-SEARCH * HTTP/1.1',
            'HOST: {0}:{1}',
            'MAN: "ssdp:discover"',
            'ST: {st}', 'MX: 3', '', ''])
        service = "upnp:rootdevice"
        message = message.format(*group, st=service)
        SSDPobject = SSDP(message)
        responses = SSDPobject.request()
        if self._debug: print responses
        discovered_devices = list()
        addresslist = list()
        for response in responses:
            if (':49153/setup.xml' in response or ':49154/setup.xml' in response or '/setup.xml' in response) and (
                response not in addresslist):
                deviceUrl = urllib2.urlopen(response)
                dom = minidom.parse(deviceUrl)
                deviceModel = dom.getElementsByTagName('modelName')[0].firstChild.data
                deviceVendor = dom.getElementsByTagName('manufacturer')[0].firstChild.data
                # nickname = dom.getElementsByTagName('friendlyName')[0].firstChild.data
                macid = dom.getElementsByTagName('serialNumber')[0].firstChild.data
                # deviceModel = 'unknown'
                if str(deviceModel).lower() == 'socket':
                    deviceType = dom.getElementsByTagName('deviceType')[0].firstChild.data
                    deviceType = re.search('urn:Belkin:device:([A-Za-z]*):1', deviceType).groups()[0]
                    if deviceType.lower() == 'controllee':
                        deviceModel = deviceModel
                    elif deviceType.lower() == 'sensor':
                        deviceModel = 'Sensor'
                deviceUrl.close()
                address = response.replace('/setup.xml', '')
                addresslist.append(response)
                discovered_devices.append({'address': address, 'mac': macid, 'model': deviceModel,
                                  'vendor': deviceVendor})


        if self._debug == True:
            pprint.pprint(discovered_devices)
        return discovered_devices


    def getDataFromDevice(self):
        print "----------------------------------------------------------------"
        print "{0}Agent is querying its current status at {1} please wait ...".format(
            self.variables.get('agent_id', None),
            datetime.datetime.now())
        if self.get_variable("model") == "Insight":
            SOAPACTION = '"urn:Belkin:service:insight:1#GetInsightParams"'
            body = "<?xml version='1.0' encoding='utf-8'?><s:Envelope xmlns:s='http://schemas.xmlsoap.org/soap/envelope/' s:encodingStyle='http://schemas.xmlsoap.org/soap/encoding/'><s:Body><u:GetInsightParams xmlns:u='urn:Belkin:service:insight:1'></u:GetInsightParams></s:Body></s:Envelope>"
            controlUrl = self.get_variable('address') + '/upnp/control/insight1'
        elif self.get_variable("model") == "Socket" or self.get_variable("model") == "LightSwitch" or self.get_variable("model") == "Dimmer":
            SOAPACTION = '"urn:Belkin:service:basicevent:1#GetBinaryState"'
            body = "<?xml version='1.0' encoding='utf-8'?><s:Envelope xmlns:s='http://schemas.xmlsoap.org/soap/envelope/' s:encodingStyle='http://schemas.xmlsoap.org/soap/encoding/'><s:Body><u:GetBinaryState xmlns:u='urn:Belkin:service:basicevent:1'></u:GetBinaryState></s:Body></s:Envelope>"
            controlUrl = self.get_variable('address') + '/upnp/control/basicevent1'

        else:
            "{0}Agent : currently Wemo device model {1} is not supported by BEMOSS".format(
                self.variables.get('agent_id', None), self.get_variable("model"))
            return

        header = {
            'Content-Type': 'text/xml; charset="utf-8"',
            'SOAPACTION': SOAPACTION
            # old
            # 'SOAPACTION': '"urn:Belkin:service:basicevent:1#GetBinaryState"'
        }

        devicedata = dict()
        try:
            response = requests.post(controlUrl, body, headers=header, timeout=10)
            if self._debug:
                print str(response.content)
            else:
                pass
            dom = minidom.parseString(response.content)
            if self.get_variable("model") == "Insight":
                if self._debug:
                    print str(dom.getElementsByTagName('InsightParams')[0].firstChild.data)
                else:
                    pass
                reading_data = str(dom.getElementsByTagName('InsightParams')[0].firstChild.data).split('|')
                print "State|Seconds of last state change|last on seconds|Seconds on today|unknown|Total Seconds|unknown|Power(mW)|" \
                      "Energy used today (mW*min)|Energy used total (mW*min)|unknown"
                print "reading_data = {}".format(reading_data)
                if int(reading_data[0]) == 0 | False:
                    devicedata['status'] = BEMOSS_ONTOLOGY.STATUS.POSSIBLE_VALUES.OFF
                else:
                    devicedata['status'] = BEMOSS_ONTOLOGY.STATUS.POSSIBLE_VALUES.ON
                if float(reading_data[7]) is not None:
                    devicedata['power'] = float(reading_data[7])/1000
                else:
                    pass
            elif self.get_variable("model") == "Socket" or self.get_variable("model") == "LightSwitch":
                if int(dom.getElementsByTagName('BinaryState')[0].firstChild.data) == 0 | False:
                    devicedata['status'] = BEMOSS_ONTOLOGY.STATUS.POSSIBLE_VALUES.OFF
                elif int(dom.getElementsByTagName('BinaryState')[0].firstChild.data) == 1 | True:
                    devicedata['status'] = BEMOSS_ONTOLOGY.STATUS.POSSIBLE_VALUES.ON
	    elif self.get_variable("model") == "Dimmer":
		if int(dom.getElementsByTagName('BinaryState')[0].firstChild.data) == 0 | False:
                    		devicedata['status'] = BEMOSS_ONTOLOGY.STATUS.POSSIBLE_VALUES.OFF
				devicedata['brightness'] = dom.getElementsByTagName('brightness')[0].firstChild.data
                elif int(dom.getElementsByTagName('BinaryState')[0].firstChild.data) == 1 | True:
                    		devicedata['status'] = BEMOSS_ONTOLOGY.STATUS.POSSIBLE_VALUES.ON
                    		devicedata['brightness'] = dom.getElementsByTagName('brightness')[0].firstChild.data
					

            else:
                "{0}Agent : currently Wemo device model {1} is not supported by BEMOSS".format(
                    self.variables.get('agent_id', None), self.get_variable("model"))
            if self._debug:
                print devicedata
            return devicedata
        except requests.ConnectionError as er:
            print("ERROR: classAPI_WeMo connection failure! @ getDeviceStatus")
            print er

    def renewConnection(self):
        self.discover()

    def setDeviceData(self, postmsg):
        setDeviceStatusResult = True
        header = {
            'Content-Type': 'text/xml; charset="utf-8"',
            'SOAPACTION': '"urn:Belkin:service:basicevent:1#SetBinaryState"'
        }
        # Data conversion before passing to the device
        _data = json.dumps(postmsg)
        _data = json.loads(_data)

        if _data[BEMOSS_ONTOLOGY.STATUS.NAME] == BEMOSS_ONTOLOGY.STATUS.POSSIBLE_VALUES.OFF:
            newstatus = 0
        else:
            newstatus = 1
	
	

	if "brightness" in _data :

		newbrightness = _data[BEMOSS_ONTOLOGY.BRIGHTNESS.NAME]

            	body = "<?xml version='1.0' encoding='utf-8'?><s:Envelope xmlns:s='http://schemas.xmlsoap.org/soap/envelope/' " \
               "s:encodingStyle='http://schemas.xmlsoap.org/soap/encoding/'><s:Body><u:SetBinaryState " \
               "xmlns:u='urn:Belkin:service:basicevent:1'><BinaryState>" + str(int(newstatus)) \
	            +"</BinaryState><brightness>" + str(int(newbrightness)) \
                + "</brightness></u:SetBinaryState></s:Body></s:Envelope>"


	else :

            	body = "<?xml version='1.0' encoding='utf-8'?><s:Envelope xmlns:s='http://schemas.xmlsoap.org/soap/envelope/' " \
               "s:encodingStyle='http://schemas.xmlsoap.org/soap/encoding/'><s:Body><u:SetBinaryState " \
               "xmlns:u='urn:Belkin:service:basicevent:1'><BinaryState>" + str(int(newstatus)) \
                + "</BinaryState></u:SetBinaryState></s:Body></s:Envelope>"

        controlUrl = self.get_variable('address') + '/upnp/control/basicevent1'
        try:
            response = requests.post(controlUrl, body, headers=header)
            dom = minidom.parseString(response.content)
            responsestatus = dom.getElementsByTagName('BinaryState')[0].firstChild.data
            if responsestatus != 'Error':
                pass
            else:
                print("ERROR: classAPI_WeMo action failure! @ setDeviceStatus")
                # self.set_variable('status',int(responsestatus))
        except:
            print("ERROR: classAPI_WeMo connection failure! @ setDeviceStatus")
            setDeviceStatusResult = False
        self.getDataFromDevice()
        
        return setDeviceStatusResult

    def identifyDevice(self):
        identifyDeviceResult = False
        try:
            self.toggleDeviceStatus()
            print(self.get_variable("model")+" is being identified with starting status "+str(self.get_variable('status')))
            self.timeDelay(5)
            self.toggleDeviceStatus()
            print("Identification for "+self.get_variable("model")+" is done with status "+str(self.get_variable('status')))
            identifyDeviceResult = True
        except:
            print("ERROR: classAPI_WeMo connection failure! @ identifyDevice")
        return identifyDeviceResult

    #GET current status and POST toggled status
    def toggleDeviceStatus(self):
        if self.getDataFromDevice()['status'] == "ON":
            self.setDeviceStatus({"status":"OFF"})
        else:
            self.setDeviceStatus({"status":"ON"})
    def preidentify_message(self):
        identifyDeviceResult = False
        print(" {0}Agent for {1} is identifying itself by doing colorloop. Please observe your lights"
              .format(self.variables.get('agent_id', None), self.variables.get('model', None)))
        self.devicewasoff = 0
        if self.get_variable('status') == "OFF":
            self.devicewasoff = 1
            message={"status": "ON"}
            return message
        else:
            return {"status": "OFF"}


    def postidentify_message(self):
        if self.devicewasoff:
            return {"status": "OFF"}
        else:
            message = {"status": "ON"}
            return message






    def timeDelay(self, time_iden):  # specify time_iden for how long to delay the process
        t0 = time.time()
        self.seconds = time_iden
        while time.time() - t0 <= time_iden:
            self.seconds = self.seconds - 1
            print("wait: {} sec".format(self.seconds))
            time.sleep(1)

# This main method will not be executed when this class is used as a module
def main():
    # Step1: create an object with initialized data from DeviceDiscovery Agent
    # requirements for instantiation1. model, 2.type, 3.api, 4. address
    WeMoSwitch = baseAPI_WeMo(model='Socket', api='API_WeMo', address='http://192.168.10.97:49154',
                     agent_id='PlugloadAgent')
    WeMoSwitch.discover()
    WeMoSwitch.getDeviceStatus()
    # WeMoSwitch.setDeviceStatus({"status":"OFF"})
    WeMoSwitch.identifyDevice()

if __name__ == "__main__": main()
