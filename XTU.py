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

#__author__ = "Hassaan Muhammad SHEIKH"
#__credits__ = ""
#__version__ = "3.5"
#__maintainer__ = "BEMOSS Team"
#__email__ = "aribemoss@gmail.com"
#__website__ = "www.bemoss.org"
#__created__ = "2016-12-05 12:04:50"
#__lastUpdated__ = "2016-12-05 11:23:33"
'''

'''This API class is for an agent that want to discover/communicate/monitor/control
prolon Vav '''
import socket
from DeviceAPI.ModbusAPI import ModbusAPI
from bemoss_lib.utils.BEMOSS_ONTOLOGY import BEMOSS_ONTOLOGY
from bemoss_lib.protocols.Modbus import connection
import csv
import os
debug = True
_Timeout=15

class API(ModbusAPI):
    def __init__(self, **kwargs):
        super(API, self).__init__(**kwargs)
        self.set_variable('connection_renew_interval', 6000)
        self.device_supports_auto = True
        if 'address' in self.variables.keys():
            address_parts = self.get_variable("address").split(':')
            self.address = address_parts[0]
            self.slave_id =int(address_parts[1])
        self._debug = True


    def API_info(self):
        return [{'device_model' : 'XTENDER-8000-48', 'vendor_name' : 'XTU', 'communication' : 'Modbus',
                'device_type_id' : 4,'api_name': 'API_XTU','html_template':'inverter/solar.html',
                'agent_type':'BasicAgent','identifiable' : False, 'authorizable': False, 'is_cloud_device' : False,
                'schedule_weekday_period' : 4,'schedule_weekend_period' : 4, 'allow_schedule_period_delete' : False,
                'chart_template': 'charts/charts_solar.html'}]

    def dashboard_view(self):
        return {"top": None, "center": {"type": "meter", "value": BEMOSS_ONTOLOGY.ENERGY_TOTAL.NAME, "unit": 'MWH'},
                "bottom": BEMOSS_ONTOLOGY.VOLTAGE_L1.NAME,"image":"PV.png"}

    def ontology(self):
        return { "Total yield": BEMOSS_ONTOLOGY.ENERGY_TOTAL,"DC voltage": BEMOSS_ONTOLOGY.VOLTAGE_DC, "DC current": BEMOSS_ONTOLOGY.CURRENT_DC,
                "AC active power": BEMOSS_ONTOLOGY.POWER_AC, "Power frequency":BEMOSS_ONTOLOGY.FREQUENCY,
                "Grid voltage L1": BEMOSS_ONTOLOGY.VOLTAGE_L1,"Grid voltage L2": BEMOSS_ONTOLOGY.VOLTAGE_L2,  "Grid current L1": BEMOSS_ONTOLOGY.CURRENT_AC,
                }

    def getDataFromDevice(self):

            try:
                device_data={}
                client = connection(self.address, port=502)
                name="inverter"
                if not hasattr(self, "data"):
                    config_path = os.path.dirname(os.path.abspath(__file__))
                    config_path = config_path + "/Modbusdata/" + name + ".csv"
                    with open(os.path.join(config_path), 'rU') as infile:
                        reader = csv.DictReader(infile)
                        data = {}
                        for row in reader:
                            for header, value in row.items():
                                try:
                                    data[header].append(value)
                                except KeyError:
                                    data[header] = [value]
                    self.data = data
                device_count = self.data["Type"]
                device_map = self.duplicates_indices(device_count)
                scale={}
                for device, values in device_map.iteritems():
                    if device == "energy":
                        energy = self.collectdata(client, values, 30533, 1,scale)
                        for k, v in energy.iteritems():
                            device_data[k] = v
                    elif device =="others":
                        others = self.collectdata(client, values, 30769, 40,scale)
                        for k, v in others.iteritems():
                            device_data[k] = v

                return device_data

            except Exception as er:
                print "classAPI_ModPowerMeter: ERROR: Reading Modbus registers at getDeviceStatus:"
                print er
                return None



    def getSignedNumber(self,number,limit):
        mask = (2 ** limit) - 1
        if number & (1 << (limit - 1)):
            return number | ~mask
        else:
            return number & mask


def main():
    #Utilization: test methods
    #Step1: create an object with initialized data from DeviceDiscovery Agent
    #requirements for instantiation1. model, 2.type, 3.api, 4. address,
    Inv = API(model='XTU',type='inverter',api='API_XTU',address='78.188.64.34:1')

    #Inv.getDeviceStatus()

    Inv.discover()

if __name__ == "__main__": main()
