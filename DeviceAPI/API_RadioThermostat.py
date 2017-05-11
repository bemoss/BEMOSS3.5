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
#__version__ = "2.0"
#__maintainer__ = "BEMOSS Team"
#__email__ = "aribemoss@gmail.com"
#__website__ = "www.bemoss.org"
#__created__ = "2014-09-12 12:04:50"
#__lastUpdated__ = "2016-03-14 11:23:33"
'''

'''This API class is for an agent that want to communicate/monitor/control
devices that compatible with Radio Thermostat Wi-Fi USNAP Module API Version 1.3 March 22, 2012
http://www.radiothermostat.com/documents/rtcoawifiapiv1_3.pdf'''

import urllib2
import json
import datetime
from urlparse import urlparse
from DeviceAPI.BaseAPI import baseAPI
from bemoss_lib.protocols.discovery.SSDP import SSDP,parseJSONresponse
from bemoss_lib.utils.BEMOSS_ONTOLOGY import BEMOSS_ONTOLOGY

class API(baseAPI):
    def __init__(self,**kwargs):
        super(API, self).__init__(**kwargs)
        self.set_variable('connection_renew_interval',6000)
        self.device_supports_auto = False
        self.set_variable(BEMOSS_ONTOLOGY.THERMOSTAT_MODE.NAME,BEMOSS_ONTOLOGY.THERMOSTAT_MODE.POSSIBLE_VALUES.OFF)
        self._debug = False

    def API_info(self):
        return [{'device_model' : 'CT30 V1.94', 'vendor_name' : 'RadioThermostat', 'communication' : 'WiFi',
                'device_type_id' : 1,'api_name': 'API_RadioThermostat','html_template':'thermostat/thermostat.html',
                'agent_type':'ThermostatAgent','identifiable' : True, 'authorizable': False, 'is_cloud_device' : False,
                'schedule_weekday_period' : 4,'schedule_weekend_period' : 4, 'allow_schedule_period_delete' : False,
                'chart_template': 'charts/charts_thermostat.html'},
                {'device_model' : 'CT50 V1.94', 'vendor_name' : 'RadioThermostat', 'communication' : 'WiFi',
                'device_type_id' : 1,'api_name': 'API_RadioThermostat','html_template':'thermostat/thermostat.html',
                'agent_type':'ThermostatAgent','identifiable' : True, 'authorizable': False, 'is_cloud_device' : False,
                'schedule_weekday_period' : 4,'schedule_weekend_period' : 4, 'allow_schedule_period_delete' : False,
                'chart_template': 'charts/charts_thermostat.html'},]

    def dashboard_view(self):
        if self.get_variable(BEMOSS_ONTOLOGY.THERMOSTAT_MODE.NAME) == BEMOSS_ONTOLOGY.THERMOSTAT_MODE.POSSIBLE_VALUES.OFF:
            return {"top": BEMOSS_ONTOLOGY.THERMOSTAT_MODE.NAME, "center": {"type": "number", "value": BEMOSS_ONTOLOGY.TEMPERATURE.NAME},
            "bottom": None}
        else:
            return {"top": BEMOSS_ONTOLOGY.THERMOSTAT_MODE.NAME, "center": {"type": "number", "value": BEMOSS_ONTOLOGY.TEMPERATURE.NAME},
            "bottom": BEMOSS_ONTOLOGY.SETPOINT.NAME}

    def ontology(self):
        return {"tmode":BEMOSS_ONTOLOGY.THERMOSTAT_MODE,"tstate":BEMOSS_ONTOLOGY.THERMOSTAT_STATE,
                "fmode":BEMOSS_ONTOLOGY.FAN_MODE,"fstate":BEMOSS_ONTOLOGY.FAN_STATE,
                "t_cool":BEMOSS_ONTOLOGY.COOL_SETPOINT,"t_heat":BEMOSS_ONTOLOGY.HEAT_SETPOINT,
                "temp":BEMOSS_ONTOLOGY.TEMPERATURE,"hold":BEMOSS_ONTOLOGY.HOLD,
                "setpoint":BEMOSS_ONTOLOGY.SETPOINT,"anti-tampering":BEMOSS_ONTOLOGY.ANTI_TAMPERING}

    def discover(self):
        message="TYPE: WM-DISCOVER\r\nVERSION: 1.0\r\n\r\nservices: com.marvell.wm.system*\r\n\r\n"
        SSDPobject = SSDP(message)
        responses = SSDPobject.request()
        if self._debug: print responses
        discovered_devices = list()
        for response in responses:
            if "/sys/" in response:
                try:
                    address = response
                    model_vendor = self.getModelVendor(address)
                    mac_address = self.getMACAddress(address)
                    address = response.replace('/sys/','')
                    discovered_devices.append({'address': address, 'mac': mac_address, 'model': model_vendor['model'],
                                      'vendor': model_vendor['vendor']})
                except Exception as er:
                    print er
                    pass

        return discovered_devices

    def getModelVendor(self,address):
        modeladdress = address.replace('/sys', '/tstat/model')
        deviceModelUrl = urllib2.urlopen(modeladdress,timeout=5)
        if deviceModelUrl.getcode() == 200:
            deviceModel = parseJSONresponse(deviceModelUrl.read(), "model")
        else:
            deviceModel = 'unknown'
        deviceVendor = "RadioThermostat"
        deviceModelUrl.close()
        return {'model': deviceModel, 'vendor': deviceVendor}

    def getMACAddress(self,address):
        deviceuuidUrl = urllib2.urlopen(address, timeout=5)
        mac_address = parseJSONresponse(deviceuuidUrl.read().decode("utf-8"), "uuid")
        return mac_address


    def renewConnection(self):
        discovered_devices= self.discover()
        new_address = None
        for device in discovered_devices:
            macaddress = device['mac']
            if macaddress == self.get_variable('macaddress'):
                new_address = device['address']
                break
        if new_address != None:
            parsed = urlparse(new_address)
            new_address = parsed.scheme+"://"+parsed.netloc
            self.set_variable('address',new_address)
            with open(self.variables['config_path'],'r') as f:
                k = json.loads(f.read())
            k['address'] = new_address
            with open(self.variables['config_path'], 'w') as outfile:
                json.dump(k, outfile, indent=4, sort_keys=True)

    tmode_dict = {0:BEMOSS_ONTOLOGY.THERMOSTAT_MODE.POSSIBLE_VALUES.OFF,
                  1:BEMOSS_ONTOLOGY.THERMOSTAT_MODE.POSSIBLE_VALUES.HEAT,
                  2:BEMOSS_ONTOLOGY.THERMOSTAT_MODE.POSSIBLE_VALUES.COOL,
                  3:BEMOSS_ONTOLOGY.THERMOSTAT_MODE.POSSIBLE_VALUES.AUTO}
    fmode_dict = {0:BEMOSS_ONTOLOGY.FAN_MODE.POSSIBLE_VALUES.AUTO,
                  1:BEMOSS_ONTOLOGY.FAN_MODE.POSSIBLE_VALUES.CIRCULATE,
                  2:BEMOSS_ONTOLOGY.FAN_MODE.POSSIBLE_VALUES.ON}
    tstate_dict = {0:BEMOSS_ONTOLOGY.THERMOSTAT_STATE.POSSIBLE_VALUES.OFF,
                   1:BEMOSS_ONTOLOGY.THERMOSTAT_STATE.POSSIBLE_VALUES.HEAT,
                   2:BEMOSS_ONTOLOGY.THERMOSTAT_STATE.POSSIBLE_VALUES.COOL}
    fstate_dict = {0:BEMOSS_ONTOLOGY.FAN_STATE.POSSIBLE_VALUES.OFF,
                   1:BEMOSS_ONTOLOGY.FAN_STATE.POSSIBLE_VALUES.ON}

    # GET Open the URL and read the data
    def getDataFromDevice(self):
        _urlData = self.get_variable("address")+'/tstat'
        try:
            _deviceUrl = urllib2.urlopen(_urlData, timeout=20)
            if (_deviceUrl.getcode() == 200):
                jsonResult = _deviceUrl.read().decode("utf-8")
                _theJSON = json.loads(jsonResult)
                if self._debug: print _theJSON
                devicedata = {"temp":_theJSON["temp"],"tmode":self.tmode_dict[_theJSON["tmode"]],
                              "fmode":self.fmode_dict[_theJSON["fmode"]],"tstate":self.tstate_dict[_theJSON["tstate"]],
                              "fstate":self.fstate_dict[_theJSON["fstate"]],"day":_theJSON["time"]["day"],
                              "hour":_theJSON["time"]["hour"],"minute":_theJSON["time"]["minute"],
                              "override":_theJSON["override"],"t_type_post":_theJSON["t_type_post"]}
                if "t_cool" in _theJSON.keys():
                    devicedata["t_cool"]=_theJSON["t_cool"]
                if "t_heat" in _theJSON.keys():
                    devicedata["t_heat"]=_theJSON["t_heat"]

                if "t_cool" not in _theJSON.keys() and "t_heat" not in _theJSON.keys():
                    devicedata["t_heat"] = None
                    devicedata["t_cool"] = None

                if devicedata["tstate"] == BEMOSS_ONTOLOGY.THERMOSTAT_STATE.POSSIBLE_VALUES.COOL:
                    if "t_cool" in devicedata:
                        devicedata["setpoint"]=devicedata["t_cool"]
                elif devicedata["tstate"] == BEMOSS_ONTOLOGY.THERMOSTAT_STATE.POSSIBLE_VALUES.HEAT:
                    if "t_heat" in devicedata:
                        devicedata["setpoint"]=devicedata["t_heat"]
                else:
                    devicedata["setpoint"]=None

                if _theJSON["hold"] == 1:
                    hold = BEMOSS_ONTOLOGY.HOLD.POSSIBLE_VALUES.PERMANENT
                else:
                    schedule_setpoint = self.getScheduleSetpoint(datetime.datetime.now())
                    if _theJSON['tmode'] == 1 and 't_heat' in _theJSON:
                        if _theJSON['t_heat'] == schedule_setpoint['heat_setpoint']:
                            hold = BEMOSS_ONTOLOGY.HOLD.POSSIBLE_VALUES.NONE
                        else:
                            hold = BEMOSS_ONTOLOGY.HOLD.POSSIBLE_VALUES.TEMPORARY
                    elif _theJSON['tmode'] == 2 and 't_cool' in _theJSON:
                        if _theJSON['t_cool'] == schedule_setpoint['cool_setpoint']:
                            hold = BEMOSS_ONTOLOGY.HOLD.POSSIBLE_VALUES.NONE
                        else:
                            hold = BEMOSS_ONTOLOGY.HOLD.POSSIBLE_VALUES.TEMPORARY
                    else:
                        hold = BEMOSS_ONTOLOGY.HOLD.POSSIBLE_VALUES.TEMPORARY
                devicedata["hold"]=hold

                if self._debug: print devicedata
                return devicedata
            else:
                print (" Received an error from server, cannot retrieve results " + str(_deviceUrl.getcode()))
                return None
        except Exception as er:
            print er
            return None

    def getDeviceSchedule(self):
        scheduleData = dict()
        try:
            _urlData = self.get_variable("address")
            _deviceUrl = urllib2.urlopen(_urlData+'/tstat', timeout=20)
            data_str = _deviceUrl.read().encode('utf8')
            data = json.loads(data_str)
            if data['hold']==0:
                scheduleData['Enabled']=True
            else:
                scheduleData['Enabled']=False
            tmode = data['tmode']   # thermostat operation state: 0:OFF, 1:HEAT, 2:COOL
            _getCool = urllib2.urlopen(_urlData+'/tstat/program/cool', timeout=20)
            cool_str = _getCool.read().encode('utf8')
            cool_sch = json.loads(cool_str)
            _getHeat = urllib2.urlopen(_urlData+'/tstat/program/heat', timeout=20)
            heat_str = _getHeat.read().encode('utf8')
            heat_sch = json.loads(heat_str)
            if tmode == 1:
                time_sch = heat_sch
            else:       # If HVAC is off, system shows cool schedule
                time_sch = cool_sch
            Days = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
            day = 0
            for item in Days:
                list1 = ['Morning']
                list2 = ['Day']
                list3 = ['Evening']
                list4 = ['Night']
                sch_time = time_sch[str(day)]
                cool_set = cool_sch[str(day)]
                heat_set = heat_sch[str(day)]
                list1.append(sch_time[0])
                list1.append(cool_set[1])
                list1.append(heat_set[1])
                list2.append(sch_time[2])
                list2.append(cool_set[3])
                list2.append(heat_set[3])
                list3.append(sch_time[4])
                list3.append(cool_set[5])
                list3.append(heat_set[5])
                list4.append(sch_time[6])
                list4.append(cool_set[7])
                list4.append(heat_set[7])
                listall = [list1, list2, list3, list4]
                scheduleData[item] = listall
                day += 1    # keep day and item the same day
        except Exception as er:
            print er
            print("Get device schedule failed @RadioThermostat API")
            raise er

        self.set_variable('scheduleData', scheduleData)

    def setDeviceData(self, postmsg):
        is_success = True
        _urlData = self.get_variable("address")+'/tstat'
        if self.isPostmsgValid(postmsg) == True:  # check if the data is valid
            _data = json.dumps(self.convertPostMsg(postmsg))
            _data = _data.encode(encoding='utf_8')
            _request = urllib2.Request(_urlData)
            _request.add_header('Content-Type','application/json')
            try:
                _f = urllib2.urlopen(_request, _data, timeout=20)  # when include data this become a POST command
            except:
                is_success = False
            # print(" after send a POST request: {}".format(_f.read().decode('utf-8')))
        else:
            print("The POST message is invalid, check thermostat_mode, heat_setpoint, cool_coolsetpoint setting and try again\n")
            is_success = False
        return is_success

    def isPostmsgValid(self,postmsg):  # check validity of postmsg
        dataValidity = True
        for k,v in postmsg.items():
            if k == BEMOSS_ONTOLOGY.THERMOSTAT_MODE.NAME:
                if postmsg.get(BEMOSS_ONTOLOGY.THERMOSTAT_MODE.NAME) == BEMOSS_ONTOLOGY.THERMOSTAT_MODE.POSSIBLE_VALUES.HEAT:
                    for k,v in postmsg.items():
                        if k == BEMOSS_ONTOLOGY.COOL_SETPOINT.NAME:
                            dataValidity = False
                            break
                elif postmsg.get(BEMOSS_ONTOLOGY.THERMOSTAT_MODE.NAME) == BEMOSS_ONTOLOGY.THERMOSTAT_MODE.POSSIBLE_VALUES.COOL:
                    for k,v in postmsg.items():
                        if k == BEMOSS_ONTOLOGY.HEAT_SETPOINT.NAME:
                            dataValidity = False
                            break
        return dataValidity

    def convertPostMsg(self, postmsg):
        msgToDevice = dict()
        if BEMOSS_ONTOLOGY.THERMOSTAT_MODE.NAME not in postmsg:
            if BEMOSS_ONTOLOGY.HEAT_SETPOINT.NAME in postmsg:
                msgToDevice = {self.dict_rev_translate(self.ontology(),BEMOSS_ONTOLOGY.HEAT_SETPOINT):
                                   postmsg.get(BEMOSS_ONTOLOGY.HEAT_SETPOINT.NAME)}
            elif BEMOSS_ONTOLOGY.COOL_SETPOINT.NAME in postmsg:
                msgToDevice = {self.dict_rev_translate(self.ontology(),BEMOSS_ONTOLOGY.COOL_SETPOINT):
                                   postmsg.get(BEMOSS_ONTOLOGY.COOL_SETPOINT.NAME)}
            else: pass
        else: pass
        for k,v in postmsg.items():
            if k == BEMOSS_ONTOLOGY.THERMOSTAT_MODE.NAME:
                msgToDevice["tmode"] = self.dict_rev_translate(self.tmode_dict,postmsg.get(BEMOSS_ONTOLOGY.THERMOSTAT_MODE.NAME))
                if postmsg.get(BEMOSS_ONTOLOGY.THERMOSTAT_MODE.NAME)==BEMOSS_ONTOLOGY.THERMOSTAT_MODE.POSSIBLE_VALUES.HEAT:
                    msgToDevice["t_heat"]=postmsg.get(BEMOSS_ONTOLOGY.HEAT_SETPOINT.NAME)
                elif postmsg.get(BEMOSS_ONTOLOGY.THERMOSTAT_MODE.NAME)==BEMOSS_ONTOLOGY.THERMOSTAT_MODE.POSSIBLE_VALUES.COOL:
                    msgToDevice["t_cool"]=postmsg.get(BEMOSS_ONTOLOGY.COOL_SETPOINT.NAME)
            if k == BEMOSS_ONTOLOGY.FAN_MODE.NAME:
                msgToDevice["fmode"]=self.dict_rev_translate(self.fmode_dict,postmsg.get(BEMOSS_ONTOLOGY.FAN_MODE.NAME))
            if k == BEMOSS_ONTOLOGY.THERMOSTAT_STATE.NAME:
                msgToDevice["tstate"]=self.dict_rev_translate(self.tstate_dict,postmsg.get(BEMOSS_ONTOLOGY.THERMOSTAT_STATE.NAME))
            if k == BEMOSS_ONTOLOGY.FAN_STATE.NAME:
                msgToDevice["fstate"]=self.dict_rev_translate(self.fstate_dict,postmsg.get(BEMOSS_ONTOLOGY.FAN_STATE.NAME))
            if k == BEMOSS_ONTOLOGY.HOLD.NAME:
                if postmsg.get(BEMOSS_ONTOLOGY.HOLD.NAME) == BEMOSS_ONTOLOGY.HOLD.POSSIBLE_VALUES.PERMANENT:
                    msgToDevice["hold"] = 1
                else:
                    msgToDevice["hold"] = 0
        if BEMOSS_ONTOLOGY.HOLD.NAME in postmsg.keys():
            if postmsg.get(BEMOSS_ONTOLOGY.HOLD.NAME) == BEMOSS_ONTOLOGY.HOLD.POSSIBLE_VALUES.NONE:
                schedule_setpoint = self.getScheduleSetpoint(datetime.datetime.now())
                if postmsg.get(BEMOSS_ONTOLOGY.THERMOSTAT_MODE.NAME) == BEMOSS_ONTOLOGY.THERMOSTAT_MODE.POSSIBLE_VALUES.HEAT:
                    msgToDevice["t_heat"] = schedule_setpoint['heat_setpoint']
                elif postmsg.get(BEMOSS_ONTOLOGY.THERMOSTAT_MODE.NAME) == BEMOSS_ONTOLOGY.THERMOSTAT_MODE.POSSIBLE_VALUES.COOL:
                    msgToDevice["t_cool"] = schedule_setpoint['cool_setpoint']
        return msgToDevice

    def setDeviceSchedule(self, scheduleData):
        _urlData = self.get_variable("address")+'/tstat'
        if scheduleData['Enabled'] == False:
            msg = {"hold":1}
            _request = urllib2.Request(_urlData)
            _request.get_method = lambda: 'POST'
            try:
                f = urllib2.urlopen(_request, msg, timeout=20)
                if f.getcode() == 200:
                    print "Thermostat " + self.variables.get("agent_id") + " is on hold now!"
                else:
                    print "Thermostat " + self.variables.get("agent_id") + " setting HOLD failed! "
            except Exception as er:
                print er
                print("Failure setting schedule HOLD @ RadioThermostat API")
        else:
            url_coolset = self.get_variable("address")+'/tstat/program/cool'
            url_heatset = self.get_variable("address")+'/tstat/program/heat'
            cool_sch = dict()
            heat_sch = dict()
            Days = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
            keys = ["0","1","2","3","4","5","6"]
            day = 0
            for item in Days:
                day_list = scheduleData[item]
                cool_list = list()
                heat_list = list()
                for period in day_list:
                    cool_list.append(period[1])
                    heat_list.append(period[1])
                    cool_list.append(period[2])
                    heat_list.append(period[3])
                if len(cool_list) < 8:
                    while len(cool_list)<8:
                        add1 = cool_list[-2]
                        add2 = cool_list[-1]
                        cool_list.append(add1)
                        cool_list.append(add2)
                if len(heat_list) < 8:
                    while len(heat_list)<8:
                        add1 = heat_list[-2]
                        add2 = heat_list[-1]
                        heat_list.append(add1)
                        heat_list.append(add2)
                cool_sch[keys[day]] = cool_list
                heat_sch[keys[day]] = heat_list

                day += 1

            _request = urllib2.Request(url_coolset)
            _request.get_method = lambda: 'POST'
            cool_sch_str = str(cool_sch)
            cool_sch_str = cool_sch_str.replace('\'','"')
            try:
                f = urllib2.urlopen(_request, cool_sch_str, timeout=20)
                if f.getcode() == 200:
                    print('Cool schedule updated!')
                else:
                    print('Cool schedule updated failed!')
            except Exception as er:
                print er
                print("Failure setting cool schedule @ RadioThermostat API")

            _request = urllib2.Request(url_heatset)
            _request.get_method = lambda: 'POST'
            heat_sch_str = str(heat_sch)
            heat_sch_str = heat_sch_str.replace('\'','"')
            try:
                f = urllib2.urlopen(_request, heat_sch_str, timeout=20)
                if f.getcode() == 200:
                    print('Heat schedule updated!')
                else:
                    print('Heat schedule updated failed!')
            except Exception as er:
                print er
                print("Failure setting heat schedule @ RadioThermostat API")

    def identifyDevice(self):
        identifyDeviceResult = False
        _data = json.dumps({'energy_led': 2})
        _data = _data.encode(encoding='utf_8')
        _request = urllib2.Request(self.get_variable('address')+"/tstat/led")
        _request.add_header('Content-Type','application/json')
        try:
            _f = urllib2.urlopen(_request, _data, timeout=20) #when include data this become a POST command
            print(" after send a POST request: {}".format(_f.read().decode('utf-8')))
        except:
            print("ERROR: classAPI_RadioThermostat connection failure! @ identifyDevice")
        print(" {0}Agent for {1} is identifying itself by changing LED light to yellow for 10 seconds "
              "then back to green please wait ...".format(self.variables.get('device_type', None),
                                                          self.variables.get('model', None)))
        _data = json.dumps({'energy_led': 1})
        _data = _data.encode(encoding='utf_8')
        _request = urllib2.Request(self.get_variable('address')+"/tstat/led")
        _request.add_header('Content-Type','application/json')
        try:
            self.timeDelay(10)
            _f = urllib2.urlopen(_request, _data, timeout=20) #when include data this become a POST command
            print(" after send a POST request: {}".format(_f.read().decode('utf-8')))
            identifyDeviceResult = True
        except:
            print("ERROR: classAPI_RadioThermostat connection failure! @ identifyDevice")
        return identifyDeviceResult

    def getScheduleSetpoint(self,testDate):
        if self.get_variable('scheduleData') is None:
            try:
                self.getDeviceSchedule()
            except Exception as er:
                return None
        schData = self.get_variable('scheduleData')
        daysofweek=['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
        todayDay = daysofweek[testDate.weekday()]
        if todayDay != 'monday':
            yesterdayDay = daysofweek[testDate.weekday()-1]
        else:
            yesterdayDay = 'sunday'

        TodaysSchedule = schData[todayDay]
        YesterdaysSchedule = schData[yesterdayDay]
        setPoints = YesterdaysSchedule[-1][2:] #yesterday's last setpoint
        nowminute = testDate.hour*60+testDate.minute
        for entries in TodaysSchedule:
            if int(entries[1]) <= nowminute:
                setPoints = [int(entries[2]),int(entries[3])]
            else:
                break
        return {'cool_setpoint':setPoints[0],'heat_setpoint':setPoints[1]}

# This main method will not be executed when this class is used as a module
def main():
    # Step1: create an object with initialized data from DeviceDiscovery Agent
    # requirements for instantiation1. model, 2.type, 3.api, 4. address
    CT50Thermostat = API(model='CT50',agent_id='wifithermostat1',api='API1',address='http://192.168.10.166')
    print("{0}agent is initialzed for {1} using API={2} at {3}".format(CT50Thermostat.get_variable('agent_id'),CT50Thermostat.get_variable('model'),CT50Thermostat.get_variable('api'),CT50Thermostat.get_variable('address')))
    #CT50Thermostat.getDeviceModel()
    # CT50Thermostat.getDeviceSchedule()
    # CT50Thermostat.setDeviceStatus({"thermostat_mode":"COOL","cool_setpoint":78})
    CT50Thermostat.getDeviceStatus()
    #CT50Thermostat.identifyDevice()
    # scheduleData = {'Enabled': True, 'monday':[['Morning', 50, 83, 80],['Day',480, 72, 82],['Evening',960, 71, 84],['Night',1000, 69, 72]], 'tuesday':[['Morning', 360 , 70, 80],['Day',480, 72, 82],['Evening',960, 71, 84],['Night',1000, 69, 72]],'wednesday':[['Morning', 300 , 70, 80],['Day',480, 72, 82],['Evening',960, 71, 84],['Night',1000, 69, 72]],'thursday':[['Morning', 360 , 70, 80],['Day',480, 72, 82],['Evening',960, 71, 84],['Night',1000, 69, 72]],'friday':[['Morning', 360 , 70, 80],['Day',480, 72, 82],['Evening',960, 71, 84],['Night',1000, 69, 72]],'saturday':[['Morning', 360 , 70, 80],['Day',480, 72, 82],['Evening',960, 71, 84],['Night',1000, 69, 72]],'sunday':[['Morning', 360 , 70, 80],['Day',480, 72, 82],['Evening',960, 71, 84],['Night',1000, 69, 72]],}
    # CT50Thermostat.setDeviceSchedule(scheduleData)
    # CT50Thermostat.discover()

if __name__ == "__main__": main()
