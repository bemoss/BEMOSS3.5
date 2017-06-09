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
import importlib
import psycopg2
import sys
import json
import datetime
import logging
import os
import re
from volttron.platform.vip.agent import Agent, Core, PubSub, compat
from volttron.platform.agent import utils
from volttron.platform.messaging import headers as headers_mod
import time
import settings
import random
import netifaces as ni
import subprocess
from bemoss_lib.utils.encrypt import decrypt_value
from bemoss_lib.utils import db_helper
from bemoss_lib.utils.BEMOSSAgent import BEMOSSAgent

utils.setup_logging()  # setup logger for debugging
_log = logging.getLogger(__name__)

# Step1: Agent Initialization
def DeviceDiscoveryAgent(config_path, **kwargs):
    config = utils.load_config(config_path)  # load the config_path from devicediscoveryagent.launch.json
    def get_config(name):
        try:
            kwargs.pop(name)  # from the **kwargs when call this function
        except KeyError as er:
            return config.get(name, '')

    # 1. @params agent
    agent_id = get_config('agent_id')
    device_scan_time = get_config('device_scan_time')
    # device_scan_time_multiplier=1
    headers = {headers_mod.FROM: agent_id}
    publish_address = 'ipc:///tmp/volttron-lite-agent-publish'
    subscribe_address = 'ipc:///tmp/volttron-lite-agent-subscribe'
    topic_delim = '/'  # topic delimiter

    # 3. @params agent & DB interfaces
    # @params DB interfaces
    db_database = settings.DATABASES['default']['NAME']
    db_host = settings.DATABASES['default']['HOST']
    db_port = settings.DATABASES['default']['PORT']
    db_user = settings.DATABASES['default']['USER']
    db_password = settings.DATABASES['default']['PASSWORD']
    db_table_device_info = settings.DATABASES['default']['TABLE_device_info']
    db_table_supported_devices = settings.DATABASES['default']['TABLE_supported_devices']
    db_table_device_type = settings.DATABASES['default']['TABLE_device_type']

    device_monitor_time = settings.DEVICES['device_monitor_time']

    # @paths
    PROJECT_DIR = settings.PROJECT_DIR
    Applications_Launch_DIR = settings.Applications_Launch_DIR
    Agents_Launch_DIR = settings.Agents_Launch_DIR

    class DiscoveryAgent(BEMOSSAgent):

        def __init__(self, **kwargs):
            super(DiscoveryAgent, self).__init__(**kwargs)
            # Connect to database

            self.agent_id = agent_id
            sys.path.append(PROJECT_DIR)

            self.device_scan_time = device_scan_time
            self.scan_for_devices = True

            self.discovery_list = list()
            #self.discovery_list.append('ICM100')
            print self.discovery_list


            self.new_discovery=True
            self.no_new_discovery_count=0

            try:
                # Find total number of devices in the dashboard_device_info table
                self.curcon.execute("SELECT * FROM "+db_table_device_info)
                self.device_num = self.curcon.rowcount  # count no. of devices discovered by Device Discovery Agent
                print "{} >> there are existing {} device(s) in database".format(agent_id, self.device_num)
                #if self.device_num != 0:  # change network status of devices to OFF (OFFLINE)
                #    rows = self.curcon.fetchall()
                #    for row in rows:
                #        self.curcon.execute("UPDATE "+db_table_device_info+" SET device_status=%s", ("OFF",))
                #        self.curcon.commit()
            except Exception as er:
                print "exception: ",er
                self.device_num = 0

        @Core.receiver('onsetup')
        def setup(self,sender,**kwargs):
            #super(DiscoveryAgent, self).setup()
            '''Discovery Processes'''
            pass
            #self.deviceDiscoveryBehavior(self.discovery_list)

        def deviceDiscoveryBehavior(self,discoverylist):
            print "Start Discovery Process--------------------------------------------------"
            # Update bemossdb miscellaneous and bemoss_notify tables with discovery start
            self.curcon.execute("UPDATE miscellaneous SET value = 'ON' WHERE key = 'auto_discovery'")
            self.curcon.commit()

            # Send message to UI about discovery start
            topic = 'from/devicediscoveryagent/discovery_request_response'
            headers = {
                'AgentID': agent_id,
                headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.JSON,
                # headers_mod.DATE: now,
                headers_mod.FROM: agent_id,
                headers_mod.TO: 'UI'
            }
            message = 'ON'
            message = message.encode(encoding='utf_8')
            #self.vip.pubsub.publish('pubsub',topic, headers, message)

            # Run Discovery Process
            while self.scan_for_devices:
                #run one discovery cycle for selected devices
                self.deviceScannerCycle(discoverylist)
                # keep track of consecutive discovery cycles with no new discovered device
                if not self.new_discovery:
                    self.no_new_discovery_count +=1
                else:
                    self.no_new_discovery_count = 0
                # Stop after some cycles
                if self.no_new_discovery_count >= 2:
                    self.scan_for_devices = False

                    # Update bemossdb miscellaneous and bemoss_notify tables with discovery end
                    self.curcon.execute("UPDATE miscellaneous SET value = 'OFF' WHERE key = 'auto_discovery'")
                    self.curcon.commit()
                    print "Stop Discovery Process--------------------------------------------------"
                time.sleep(self.device_scan_time)
            print "Exit Function"

        #deviceScannerBehavior (TickerBehavior)
        def deviceScannerCycle(self,discoverylist):
            self.new_discovery=False
            print "Start Discovery Cycle--------------------------------------------------"
            print "{} >> device next scan time in {} sec".format(agent_id, str(self.device_scan_time ))
            self.device_discovery_start_time = datetime.datetime.now()
            print "{} >> start_time {}".format(agent_id, str(self.device_discovery_start_time))
            print "{} >> is trying to discover all available devices\n".format(agent_id)
            api_map=dict()
            baseclassdict= dict()
            for discover_device_model in discoverylist:
                self.curcon.execute("SELECT api_name from "+db_table_supported_devices
                                             +" where device_model=%s",(discover_device_model,))
                if self.curcon.rowcount:
                    deviceapi = self.curcon.fetchone()[0]
                    api_class = self.return_APImodule(deviceapi).__class__
                    while api_class and "discover" not in api_class.__dict__:
                        api_class=api_class.__base__
                    if api_class not in baseclassdict:
                        baseclassdict[api_class] = deviceapi
                        if deviceapi not in api_map:
                            api_map[deviceapi] = [discover_device_model]
                        else:
                            api_map[deviceapi] += [discover_device_model]
                    else:
                        sibling_api = baseclassdict[api_class]
                        api_map[sibling_api] += [discover_device_model]

                else:
                    print discover_device_model + " is not supported"
            self.findDevices(api_map)
            print "Stop Discovery Cycle---------------------------------------------------"

        def findDevices(self, api_map):
            #******************************************************************************************************

            for API, modellist in api_map.iteritems():
                num_new_Devices = 0
                print "{} API is finding available devices ...".format(API)
                discovery_module = self.return_APImodule(API)
                self.curcon.execute("SELECT is_cloud_device from " + db_table_supported_devices
                                 + " where api_name=%s", (API,))
                is_cloud = self.curcon.fetchone()
                self.curcon.execute("SELECT address from " + db_table_supported_devices
                                    + " where api_name=%s", (API,))
                address = self.curcon.fetchone()[0]

                if is_cloud is not None:
                    is_cloud = is_cloud[0]
                if is_cloud:
                    for model in modellist:
                        try:
                            self.curcon.execute("SELECT * from passwords_manager where device_model=%s",(model,))
                            device_login_data = self.curcon.fetchall()
                            if device_login_data:
                                login_infos = list()
                                for entry in device_login_data:
                                    login_infos.append({'username':entry[1].encode('utf8'),'password':entry[2].encode('utf8')})

                                for login_info in login_infos:
                                    if address != None:
                                        self.curcon.execute("SELECT device_model from " + db_table_supported_devices
                                                            + " where api_name=%s", (API,))
                                        model = self.curcon.fetchone()
                                        try:
                                            discovered_devices = discovery_module.discover(login_info['username'],decrypt_value(login_info['password']),address,model[0])
                                        except Exception as e:   #if address is not required for API or "" go to old discovery
                                            discovered_devices = discovery_module.discover(login_info['username'],
                                                                                           decrypt_value(
                                                                                               login_info['password']))
                                    else:
                                        discovered_devices = discovery_module.discover(login_info['username'],decrypt_value(login_info['password']))
                                    for discovered_device in discovered_devices:
                                        discovered_device['username']=login_info['username']
                                        discovered_device['password']=login_info['password']
                            else:
                                discovered_devices=list()
                                print "DeviceDiscoveryAgent: Couldn't find login info while trying to discover cloud device "+model
                        except Exception as er:
                            print er
                            print "DeviceDiscoveryAgent: ERROR occurred while trying to discover devices in " + API + ":" + str(
                                er)
                elif address != None:
                    self.curcon.execute("SELECT device_model from " + db_table_supported_devices
                                        + " where api_name=%s", (API,))
                    model = self.curcon.fetchone()
                    try:
                        discovered_devices = discovery_module.discover(address,model[0])
                    except Exception as e: #if address is not required for API or "" go to old discovery
                        discovered_devices = discovery_module.discover()
                else:
                        discovered_devices = discovery_module.discover()

                if not discovered_devices: #no devices discovered for this API
                    continue

                for discovered_device in discovered_devices:
                    devicemodel = discovered_device["model"]
                    if devicemodel in modellist:

                        address = discovered_device["address"]
                        macaddress = discovered_device["mac"]
                        print "{} >> Device discovered with address: {} and macaddress: {}".format(agent_id,address,macaddress)

                        if self.checkMACinDB(self.curcon, macaddress):
                            newdeviceflag = False
                            print '{} >> Device with macaddress {} was previously discovered, ignoring it now'\
                                .format(agent_id, macaddress)
                        #case2: new device has been discovered
                        else:
                            print '{} >> Device discovered with macaddress {} is a new find!'\
                                .format(agent_id, macaddress)
                            newdeviceflag = True

                        if newdeviceflag:
                            deviceModel = discovered_device["model"]
                            deviceVendor = discovered_device["vendor"]

                            print "{} >> Model: {} and Vendor: {}".format(agent_id,deviceModel,deviceVendor)

                            try:
                                self.curcon.execute("SELECT * from "+db_table_supported_devices
                                                 +" where vendor_name=%s and device_model=%s",(deviceVendor,deviceModel))
                                supported_entry = self.curcon.fetchone()[0]
                                supported=True
                            except Exception as er:
                                print "exception: ",er
                                supported=False

                            if (supported):


                                self.device_num+=1
                                self.curcon.execute("SELECT device_type_id from "+db_table_supported_devices
                                                 +" where vendor_name=%s and device_model=%s",(deviceVendor,deviceModel))
                                device_type_id = self.curcon.fetchone()[0]

                                self.curcon.execute("SELECT device_type from "+db_table_device_type
                                                 +" where id=%s",(str(device_type_id)))
                                device_type = self.curcon.fetchone()[0]

                                device_id = deviceModel[:4]+"_"+macaddress

                                self.curcon.execute("SELECT identifiable from "+db_table_supported_devices
                                                 +" where vendor_name=%s and device_model=%s",(deviceVendor,deviceModel))
                                identifiable = self.curcon.fetchone()[0]

                                self.curcon.execute("SELECT authorizable from "+db_table_supported_devices
                                                 +" where vendor_name=%s and device_model=%s",(deviceVendor,deviceModel))
                                authorizable = self.curcon.fetchone()[0]

                                self.curcon.execute("SELECT communication from "+db_table_supported_devices
                                                 +" where vendor_name=%s and device_model=%s",(deviceVendor,deviceModel))
                                communication = self.curcon.fetchone()[0]

                                deviceNickname = discovered_device.get('nickname') if 'nickname' in discovered_device.keys() else device_type + str(self.device_num)
                                username = discovered_device.get('username') if 'username' in discovered_device.keys() else None
                                password = discovered_device.get('password') if 'password' in discovered_device.keys() else None

                                self.curcon.execute("INSERT INTO "+db_table_device_info+"(agent_id,vendor_name,device_model,mac_address,nickname,address,username,password,min_range,max_range,identifiable,authorizable,communication,date_added,factory_id,approval_status,device_type_id,node_id) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                                                         (device_id, deviceVendor, deviceModel, macaddress, deviceNickname, address,username,password,
                                                  None, None, identifiable, authorizable, communication, str(datetime.datetime.now()), macaddress, 'PND',device_type_id,0))
                                self.curcon.commit()

                                num_new_Devices+=1
                                self.new_discovery=True
                            else:
                                print "{} >> This device currently is not supported by BEMOSS".format(agent_id)
                        else:
                            pass

                #Print how many WiFi devices this DeviceDiscoverAgent found!
                print("{} >> Found {} new with {} API".format(agent_id,num_new_Devices,API))
                print " "

            return num_new_Devices

        def return_APImodule(self, API):
            api_module = importlib.import_module("DeviceAPI." + API)
            discovery_module = api_module.API(parent=self, vip=self.vip, core=self.core)
            return discovery_module

        @PubSub.subscribe('pubsub', 'to/devicediscoveryagent/discovery_request')
        def manualDiscoveryBehavior(self, peer, sender, bus, topic,headers,message):
            print "DeviceDiscoveryAgent got\nTopic: {topic}".format(topic=topic)
            print "Headers: {headers}".format(headers=headers)
            print "Message: {message}\n".format(message=message)

            discovery_model_names = message
            #print discovery_model_names

            self.scan_for_devices = True
            self.deviceDiscoveryBehavior(discovery_model_names)
            # Send message to UI about discovery end
            headers = {
                'AgentID': agent_id,
                headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.JSON,
                # headers_mod.DATE: now,
                headers_mod.FROM: agent_id,
                headers_mod.TO: 'UI'
            }
            message = 'OFF'
            message = message.encode(encoding='utf_8')

            self.bemoss_publish('discovery_request_response','ui',message,headers=headers)


        def checkMACinDB(self, conn, macaddr):
            cur = conn
            cur.execute("SELECT agent_id FROM "+db_table_device_info+" WHERE mac_address=%(id)s",
                        {'id': macaddr})
            if cur.rowcount != 0:
                mac_already_in_db = True
            else:
                mac_already_in_db = False
            return mac_already_in_db

        def device_agent_still_running(self,agent_launch_filename):
            statusreply = subprocess.check_output( settings.PROJECT_DIR + '/env/bin/volttron-ctl status',shell=True)
            statusreply = statusreply.split('\n')
            agent_still_running = False
            reg_search_term = agent_launch_filename
            for line in statusreply:
                #print(line, end='') #write to a next file name outfile
                match = re.search(reg_search_term, line) and re.search('running', line)
                if match:  # The agent for this device is running
                    agent_still_running = True
                else:
                    pass
            return agent_still_running

        def write_launch_file(self, executable, deviceID, device_monitor_time, deviceModel, deviceVendor, deviceType,
                              api, address, macaddress, db_host, db_port, db_database, db_user, db_password):
            try:
                host_ip_address = ni.ifaddresses('eth0')[2][0]['addr']
            except Exception as er:
                print "exception: ",er
                host_ip_address = None
            if host_ip_address is None:
                try:
                    host_ip_address = ni.ifaddresses('wlan0')[2][0]['addr']
                except Exception as er:
                    print "exception: ",er
                    pass

            else: pass
            data= {
                    "agent": {
                        "exec": executable+"-0.1-py2.7.egg --config \"%c\" --sub \"%s\" --pub \"%p\""
                    },
                    "agent_id": deviceID,
                    "device_monitor_time": device_monitor_time,
                    "model": deviceModel,
                    "vendor":deviceVendor,
                    "type": deviceType,
                    "api": api,
                    "address": address,
                    "macaddress": macaddress,
                    "db_host": db_host,
                    # "db_host": host_ip_address,
                    "db_port": db_port,
                    "db_database": db_database,
                    "db_user": db_user,
                    "db_password": db_password,
                    "building_name": "bemoss",
                    "zone_id" : 999
                }
            if 'ZigBee' in api:
                discovery_module = importlib.import_module("DeviceAPI.discoverAPI."+'ZigBee')
                gatewayid = discovery_module.getGateWayId()
                data['gateway_id'] = gatewayid
            __launch_file = os.path.join(Agents_Launch_DIR+deviceID+".launch.json")
            #print(__launch_file)
            with open(__launch_file, 'w') as outfile:
                json.dump(data, outfile, indent=4, sort_keys=True)

    DiscoveryAgent.__name__ = 'DeviceDiscoveryAgent'
    return DiscoveryAgent(**kwargs)

def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    utils.vip_main(DeviceDiscoveryAgent)

if __name__ == '__main__':
    # Entry point for script
    try:
        sys.exit(main())
    except KeyboardInterrupt as er:
        print "KeyboardInterrupt", er
        pass