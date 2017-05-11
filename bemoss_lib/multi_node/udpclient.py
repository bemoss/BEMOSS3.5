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

import os
import json
import sys
import settings
os.chdir(os.path.expanduser(settings.PROJECT_DIR ))
current_working_directory = os.getcwd()
sys.path.append(current_working_directory)
import settings
import fcntl, socket, struct
import datetime
import netifaces as ni
import time
import select
from bemoss_lib.databases.cassandraAPI import cassandraHelper

#find broadcast address automatically from script
interfaces=ni.interfaces()
interfaces.reverse()

broadcast_address = ''
for interface in interfaces:
    if interface == 'lo':
        pass
    else:
        try:
            if broadcast_address != '' and 'wlan' not in interface:
                continue
            broadcast_address = ni.ifaddresses(interface)[2][0]['broadcast']
        except:
            pass

print "Broadcast address: "+ broadcast_address
address = (broadcast_address, 54545)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 2)
Agents_DIR = settings.Agents_DIR

def getHwAddr(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', ifname[:15]))
    return ''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1]

node_name = settings.PLATFORM['node']['name']
node_type = settings.PLATFORM['node']['type']
node_model = settings.PLATFORM['node']['model']
main_core = settings.PLATFORM['node']['main_core']
node_status = "ONLINE"
building_name = settings.PLATFORM['node']['building_name']

interfaces=ni.interfaces()
interfaces.reverse()
ip_address = ''
for interface in interfaces:
    if interface == 'lo':
        pass
    else:
        try:
            if ip_address != '' and 'wlan' not in interface:
                continue
            ip_address = ni.ifaddresses(interface)[2][0]['addr']
            mac_address = getHwAddr(interface)
        except:
            pass

date_added = datetime.datetime.now()
communication = "WiFi"
last_scanned_time = datetime.datetime.now()
node_location = building_name+"/"+"".join(str(mac_address).split(':'))
message = json.dumps({
                        "node_name": node_name,
                        "node_type": node_type,
                        "main_core": main_core,
                        "node_model": node_model,
                        "node_status": node_status,
                        "building_name": building_name,
                        "mac_address": mac_address,
                        "node_location": node_location
})

try:
    os.remove(os.path.join(Agents_DIR+"MultiBuilding/multibuildingagent.launch.json"))
except: pass

found_bemoss_core = False

while True:
    print "found_bemoss_core {}".format(found_bemoss_core)
    if found_bemoss_core == False:
        print "trying to find core"
        time.sleep(2)
        add = ('', 54545) # IP_address of '' makes it broadcast on all interface.
        client_socket.sendto(message, address)

        client_socket.setblocking(0)
        ready = select.select([client_socket], [], [], 10)
        if ready[0]:
            recv_data, addr = client_socket.recvfrom(2048)
            node_info = json.loads(recv_data)
            core_name = node_info['node_name']
            if main_core != core_name:
                print 'Wrong core found '+core_name
                continue
            found_bemoss_core = True
        else:
            pass
    else:
        break

print "found_bemoss_core {}".format(found_bemoss_core)
print str(addr)+":"+str(recv_data)

#add the ip address of the core as a seed node for the cassandra cluster
cassandraHelper.addSeed(addr[0])

#add new node to node_info table
node_info = json.loads(recv_data)
core_name = node_info['node_name']
core_init_zone_name = core_name
core_type = node_info['node_type']
core_model = node_info['node_model']
core_status = "ONLINE"
core_building_name = node_info['building_name']
core_ip_address = addr[0]
core_mac_address = node_info['mac_address']
core_zone_id = node_info['zone_id']
core_date_added = datetime.datetime.now()
core_communication = "WiFi"
core_last_scanned_time = datetime.datetime.now()
core_location = node_info['node_location']
this_node_zone_id = node_info['remote_node_zone_id']
#create multibuidling agent launch file
data= {
    "agent": {
        "exec": "multibuildingagent-0.1-py2.7.egg --config \"%c\" --sub \"%s\" --pub \"%p\""
    },
    'building-publish-address': "tcp://"+ip_address+":9163",
    'building-subscribe-address': "tcp://"+ip_address+":9162",
    "hosts": {
        core_location:{"pub": "tcp://"+core_ip_address+":9163",
                        "sub": "tcp://"+core_ip_address+":9162",
                        "allow": "sub",
                        "type": core_type,
                        "building_name": core_building_name,
                        "zone_id": core_zone_id,
                        "mac_address": core_mac_address,
        }
    },
    'cleanup-period': 600000000,
    'uuid': "MultiBuildingService"
}
_launch_file = os.path.join(Agents_DIR+"MultiBuilding/multibuildingagent.launch.json")
#print(__launch_file)
with open(_launch_file, 'w') as outfile:
    json.dump(data, outfile, indent=4, sort_keys=True)

with open(_launch_file, 'r+') as f:
    data = json.load(f)
    data['hosts'][node_location] = {"pub": "tcp://"+ip_address+":9163",
                                    "sub": "tcp://"+ip_address+":9162",
                                    "allow": "sub",
                                    "building_name": building_name,
                                    "zone_id": this_node_zone_id,  # get zone_id from core discovery
                                    "mac_address": mac_address,
                                    "type": "node"}
    data['building-publish-address'] = "tcp://"+ip_address+":9163"
    data['building-subscribe-address'] = "tcp://"+ip_address+":9162"
    data['cleanup-period'] = 600000
    f.seek(0)
    json.dump(data, f, indent=4, sort_keys=True)
