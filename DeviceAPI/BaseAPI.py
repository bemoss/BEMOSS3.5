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
#__created__ = "2016-08-20"
#__lastUpdated__ = "2016-09-20"
'''


import abc
import time

class baseAPI:
    __metaclass__ = abc.ABCMeta

    def __init__(self,**kwargs): # Initialized common attributes
        self.variables = kwargs
        self._debug = False
        self.set_variable('connection_renew_interval',6000)
        self.set_variable('offline_count', 0)

    def set_variable(self,k,v):  # k=key, v=value
        self.variables[k] = v

    def get_variable(self,k,default=None):
        return self.variables.get(k, default)  #  default of get_variable is none

    @abc.abstractmethod
    def API_info(self):
        '''return [{'device_model' : '---', 'vendor_name' : '---', 'communication' : '---', 'device_type_id' : '---',
        'api_name': '---','html_template':'---','agent_type':'---','identifiable' : '---', 'authorizable' : '---',
        'is_cloud_device' : '---', 'schedule_weekday_period' : '---', 'schedule_weekend_period' : '---',
        'allow_schedule_period_delete' : '---'}]'''
        return

    @abc.abstractmethod
    def dashboard_view(self):
        '''return {"top": "thermostat_mode", "center": {"type": "number", "value": "temperature"},
        "bottom": "set_point"}
        For devices using meter gauge in the center, please also add the unit to be displayed:
        return {"top": "thermostat_mode", "center": {"type": "meter", "value": "70", "unit":'W'},
        "bottom": "set_point"}'''
        return

    @abc.abstractmethod
    def ontology(self):
        '''return {"tcool":BEMOSS_ONTOLOGY.COOL_SETPOINT.NAME,...}'''
        return

    @abc.abstractmethod
    def discover(self,username,password):
        '''Discovery Method goes here
        self.getModelVendor()
        self.getMACAddress()
        return [{'address': address1, 'mac': mac_address1, 'model': model1, 'vendor': vendor1, 'nickname': None},
        {'address': address2, 'mac': mac_address2, 'model': model2, 'vendor': vendor2, 'nickname': None}, ...]'''
        return

    def getModelVendor(self,address):
        return

    def getMACAddress(self):
        return

    def renewConnection(self):
        return

    def updateOfflineCount(self,getDeviceStatusResult):
        if getDeviceStatusResult == True:
            self.set_variable('offline_count', 0)
        else:
            self.set_variable('offline_count', self.get_variable('offline_count',0) + 1)

    def getDeviceStatus(self):
        getDeviceStatusResult = True
        try:
            _device_data = self.getDataFromDevice()
            if self._debug: print _device_data

            if not _device_data:
                getDeviceStatusResult = False
            else:
                self.convertDeviceStatus(_device_data)
                if self._debug: print self.variables

        except Exception as er:
            print self.API_info()[0]['api_name']+":ERROR in getdevicestatus: "+str(er)
            getDeviceStatusResult = False

        self.updateOfflineCount(getDeviceStatusResult)

    @abc.abstractmethod
    def getDataFromDevice(self):
        '''Implement in derived API class
        return JSON data with device variables, return None if error occurred'''
        return

    def convertDeviceStatus(self, data):
        for variable_name in data.keys():
            if data[variable_name]=="":
                continue
            if variable_name in self.ontology().keys():
                ont = self.ontology()[variable_name]
                if ont.TYPE in ['float','double']:
                    try:
                        val = float(data[variable_name])
                    except (TypeError, ValueError):
                        val = None
                elif ont.TYPE in ['string','text']:
                    val = str(data[variable_name])
                else:
                    val = data[variable_name]
                self.set_variable(ont.NAME, val)

    # def getDeviceSchedule(self):
    #     if required

    def setDeviceStatus(self, postmsg):
        try:
            setDeviceStatusResult = self.setDeviceData(postmsg)

        except Exception as er:
            print self.API_info()[0]['api_name']+":ERROR in setdevicestatus: "+str(er)
            setDeviceStatusResult = False

        return setDeviceStatusResult

    def setDeviceData(self,postmsg):
        '''Implement in derived API class
        return True for success, False for failure'''
        is_success = True
        return is_success

    # def setDeviceSchedule(self, scheduleData):
    #     if required

    def identifyDevice(self):
        identifyDeviceResult = False
        '''Keep the current state of one of the changeable device variables
        Change device variable that is visually noticeable
        self.timeDelay(5)
        Change device variable back to previous state
        if successful, identifyDeviceResult = True'''
        return identifyDeviceResult

    # time delay
    def timeDelay(self,time_iden): #specify time_iden for how long to delay the process
        t0 = time.time()
        self.seconds = time_iden
        while time.time() - t0 <= time_iden:
            self.seconds = self.seconds - 1
            if self._debug: print("wait: {} sec".format(self.seconds))
            time.sleep(1)

    def dict_rev_translate(self,_JSON,value):
        for k in _JSON.keys():
            if _JSON[k]==value:
                return k
        return None

def main():
    pass

if __name__ == "__main__": main()
