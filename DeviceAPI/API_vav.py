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
#__created__ = "2016-10-18 12:04:50"
#__lastUpdated__ = "2016-10-19 11:23:33"
'''

'''This API class is for an agent that want to discover/communicate/monitor/control
prolon Vav '''

from DeviceAPI.ModbusAPI import ModbusAPI
from bemoss_lib.utils.BEMOSS_ONTOLOGY import BEMOSS_ONTOLOGY
from bemoss_lib.protocols.Modbus import  connection


debug = True

class API(ModbusAPI):

    def API_info(self):
        return [{'device_model': 'VC1000', 'vendor_name': 'Prolon', 'communication': 'Modbus',
                'device_type_id': 1,'api_name': 'API_vav','html_template':'thermostat/vav.html',
                'agent_type':'BasicAgent','identifiable': False, 'authorizable' : False, 'is_cloud_device': False,
                'schedule_weekday_period': 4,'schedule_weekend_period': 4, 'allow_schedule_period_delete': True,'chart_template': 'charts/charts_vav.html'},
                ]

    def dashboard_view(self):

        return { "center": {"type": "number", "value": BEMOSS_ONTOLOGY.TEMPERATURE.NAME},
            "bottom": BEMOSS_ONTOLOGY.FLAP.NAME}

    def ontology(self):
        return {"override":BEMOSS_ONTOLOGY.OVERRIDE,"flap_position":BEMOSS_ONTOLOGY.FLAP,
                "cool_setpoint":BEMOSS_ONTOLOGY.COOL_SETPOINT,"heat_setpoint":BEMOSS_ONTOLOGY.HEAT_SETPOINT,
                "temperature":BEMOSS_ONTOLOGY.TEMPERATURE,"supply_temperature":BEMOSS_ONTOLOGY.SUPPLY_TEMPERATURE}


    def cel2far(self,cel_temp):
        return (((cel_temp * 9.0)/5.0)+32.0)

    def far2cel(self,far_temp):
        j= (((far_temp -32.0 )/9.0)*5.0)
        return j

    def getDataFromDevice(self):

        try:
            devicedata=dict()
            client = connection(self.address, port=502)
            client.connect()
            result = client.read_input_registers(0,8,unit=self.subordinate_id)
            if int(result.registers[0])==32767:
                devicedata["temperature"] = None
            else:
                devicedata["temperature"] = round(float(self.cel2far(float(int(result.registers[0]))/100.0)),0)
            devicedata['heat_setpoint'] =round(float(self.cel2far(float(int(result.registers[1]))/100.0)),1)
            devicedata['cool_setpoint'] =round(float(self.cel2far(float(int(result.registers[2]))/100.0)),1)
            if int(result.registers[7])==32767:
                devicedata['supply_temperature'] =None
            else:
                devicedata['supply_temperature']=round(float(self.cel2far(float(int(result.registers[7]))/100.0)),1)
            result = client.read_holding_registers(159,2,unit=self.subordinate_id)
            if (int(result.registers[0])==1):
                devicedata['override']='ON'
            else:
                devicedata['override']='OFF'
            devicedata['flap_position']=int(result.registers[1])
            client.close()
            return devicedata
        except Exception as er:
            print "classAPI_vav: ERROR: Reading Modbus registers at getDeviceStatus:"
            print er
            return {}

    def setDeviceData(self, postmsg):
        try:
            client = connection(self.address,port=502)
            client.connect()
            if BEMOSS_ONTOLOGY.HEAT_SETPOINT.NAME in postmsg.keys():
                result=client.write_register(6,int(self.far2cel(float(postmsg.get('heat_setpoint'))* 100.0)),unit=self.subordinate_id)
            if BEMOSS_ONTOLOGY.COOL_SETPOINT.NAME in postmsg.keys():
                result2=client.write_register(6,int(self.far2cel(float(postmsg.get('cool_setpoint'))* 100.0)),unit=self.subordinate_id)
            if BEMOSS_ONTOLOGY.OVERRIDE.NAME in postmsg.keys():
                if postmsg.get('override') == 'ON' or postmsg.get('override') == True:
                    client.write_register(159,1,unit=self.subordinate_id)
                elif postmsg.get('override') == 'OFF' or postmsg.get('override') == False:
                    client.write_register(159,0,unit=self.subordinate_id)
            if BEMOSS_ONTOLOGY.FLAP.NAME in postmsg.keys():
                 client.write_register(160,int(postmsg.get('flap_position')),unit=self.subordinate_id)
            client.close()
            return True
        except:
            try:
                client.close()
                return False
            except:
                print('Modbus TCP client was not built successfully at the beginning')
                return False

def main():
    #Utilization: test methods
    #Step1: create an object with initialized data from DeviceDiscovery Agent
    #requirements for instantiation1. model, 2.type, 3.api, 4. address,
    Prolon = API(model='VC1000',type='VAV',api='API_vav', address='192.168.10.84:1')

    #Step2: Get data from device
    #Prolon.getDeviceStatus()
    #print Prolon.variables

    #Step3: change device operating set points
    Prolon.setDeviceStatus({'flap_override':'ON','flap_position':20,'heat_setpoint':90})
    #Prolon.setDeviceStatus({'fan_status':'ON'})

    #Prolon.getDeviceStatus()
    #print Prolon.variables
    Prolon.discover()

if __name__ == "__main__": main()
