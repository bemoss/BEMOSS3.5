# -*- coding: utf-8 -*-
from __future__ import division
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

__author__ =  "BEMOSS Team"
__credits__ = ""
__version__ = "3.5"
__maintainer__ = "BEMOSS Team""
__email__ = "aribemoss@gmail.com"
__website__ = ""
__status__ = "Prototype"
__created__ = "2016-10-22 16:12:00"
__lastUpdated__ = "2016-10-25 13:25:00"
'''

from DeviceAPI.BACnetAPI import BACnetAPI

import gevent


CONFIG_FILE = "/Bacnetdata/wattstopper_config.csv"
class baseAPI_Wattstopper(BACnetAPI):

    def __init__(self, parent=None,**kwargs):

        BACnetAPI.__init__(self, parent=parent, **kwargs)
        self.set_variable('connection_renew_interval', 6000)
        self.device_supports_auto = True
        self.config_file = CONFIG_FILE
        if 'agent_id' in self.variables.keys():
            decode=self.variables["agent_id"]
            agent= decode.split('n')[0]
            number=decode.split('n')[1]
            self.agent=agent
            self.number=number


    def discover(self):

        try:
            devicelist=list()
            maclist = list()
            modellist = list()
            vendorlist=list()
            addresslist = list()
            deviceinfo = self.broadcast()

            for device in deviceinfo:
                #retries=200

                address = device["address"]
                device_id = device["mac"]
                vendor = device["vendor"]
                model=device["model"]
                if vendor == 'WattStopper':
                    deviceinfo.remove(device)
                    try:
                        data = self.readcsv()
                        if data:
                            device_count = data["Device number"]
                            device_map = self.duplicates_indices(device_count)
                            for device, value in device_map.iteritems():
                                if device != "":
                                    for each_value in value:

                                                maclist.append(str(device_id) + "n" + device)
                                                modellist.append(data['Model Name'][each_value])
                                                addresslist.append(address)
                                                vendorlist.append(vendor)
                                                break
                    except Exception as e:
                        print e
                        continue
                    except gevent.Timeout:
                        print " discovery call timeout"
                        continue
                    devicelist = zip(maclist, modellist, addresslist, vendorlist)
            if devicelist:
                for mac, model, add, Vendor in devicelist:
                    deviceinfo.append({'address': add, 'mac': mac,
                                       'model': model, 'vendor': Vendor, })
            return deviceinfo

        except Exception as e:
            print e
            return deviceinfo

