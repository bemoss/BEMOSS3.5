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

#UDP server responds to broadcast packets
#you can have only one instance of this running as a BEMOSS core!!

import os
import json
import sys
import settings
from bemoss_lib.databases.cassandraAPI import cassandraDB
import psycopg2
import datetime
import netifaces as ni
import fcntl, socket, struct

address = ('', 54545)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(address)
Agents_DIR = settings.Agents_DIR
db_database = settings.DATABASES['default']['NAME']
db_host = settings.DATABASES['default']['HOST']
db_port = settings.DATABASES['default']['PORT']
db_user = settings.DATABASES['default']['USER']
db_password = settings.DATABASES['default']['PASSWORD']
db_table_node_info = settings.DATABASES['default']['TABLE_node_info']
db_table_building_zone = settings.DATABASES['default']['TABLE_building_zone']
db_table_global_zone_setting = settings.DATABASES['default']['TABLE_global_zone_setting']
db_table_node_device = settings.DATABASES['default']['TABLE_node_device']

conn = psycopg2.connect(host=db_host, port=db_port, database=db_database,
                        user=db_user, password=db_password)
cur = conn.cursor()  # open a cursor to perform database operations
print "{} >> Done 1: connect to database name {}".format("Multi-node server", db_database)

def getHwAddr(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', ifname[:15]))
    return ''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1]

def add_building_zone(_zone_nickname, _zone_id):
    if _zone_id == None:
        cur.execute("SELECT zone_id FROM "+db_table_building_zone+" WHERE zone_nickname=%s", (_zone_nickname,))
        if cur.rowcount == 0:
            cur.execute("INSERT INTO "+db_table_building_zone+"(zone_nickname) VALUES(%s)", (_zone_nickname,))
            conn.commit()
    else:
        cur.execute("SELECT zone_id FROM "+db_table_building_zone+" WHERE zone_nickname=%s", (_zone_nickname,))
        if cur.rowcount == 0:
            cur.execute("INSERT INTO "+db_table_building_zone+"(zone_nickname,zone_id) VALUES(%s,%s)", (_zone_nickname,_zone_id))
            conn.commit()

def add_global_zone_setting(_id, _zone_id, _heat_setpoint, _cool_setpoint, _illuminance):
    cur.execute("SELECT id FROM "+db_table_global_zone_setting+" WHERE zone_id=%s", (_zone_id,))
    if cur.rowcount == 0:
        cur.execute("INSERT INTO "+db_table_global_zone_setting+"(id, zone_id, heat_setpoint, cool_setpoint, illuminance)"
                                                                " VALUES(%s,%s,%s,%s,%s)", (_id,_zone_id,_heat_setpoint,
                                                                                            _cool_setpoint, _illuminance,))
        conn.commit()

def insertNodeInfo(node_name,node_type,node_model,node_status,building_name, ip_address,
                   mac_address,associated_zone,date_added,communication,last_scanned_time):
    cur.execute("SELECT mac_address FROM "+db_table_node_info+" WHERE mac_address=%s", (mac_address,))
    if cur.rowcount == 0:
        cur.execute("INSERT INTO "+db_table_node_info+"(node_name,node_type,node_model,node_status,building_name,"
                                                    "ip_address,mac_address,date_added,communication,last_scanned_time)"
                                                    " VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                                                    (node_name,node_type,node_model,node_status,building_name,
                                                     ip_address,mac_address,date_added,communication,last_scanned_time))
        conn.commit()
        cur.execute("UPDATE "+db_table_node_info+" SET associated_zone=%s WHERE mac_address=%s", (associated_zone, mac_address))
        conn.commit()
        return 1
    else:
        cur.execute("UPDATE "+db_table_node_info+" SET ip_address=%s WHERE mac_address=%s",(ip_address, mac_address))
        conn.commit()
        return 0

node_name = settings.PLATFORM['node']['name']
init_zone_name = node_name
node_type = settings.PLATFORM['node']['type']
node_model = settings.PLATFORM['node']['model']
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
core_location = building_name+"/"+"".join(str(mac_address).split(':'))

cur.execute("SELECT zone_id FROM "+db_table_building_zone+" WHERE zone_nickname=%s", (node_name,))
if cur.rowcount != 0:  # this APP used to be launched before
    associated_zone = cur.fetchone()[0]
else:
    associated_zone=999
insertNodeInfo(node_name,node_type,node_model,node_status,building_name, ip_address,
               mac_address,associated_zone,date_added,communication,last_scanned_time)

if not os.path.isfile(os.path.join(Agents_DIR+"MultiBuilding/multibuildingagent.launch.json")):
    #If no launch file, create it
    data= {
            "agent": {
                "exec": "multibuildingagent-0.1-py2.7.egg --config \"%c\" --sub \"%s\" --pub \"%p\""
            },
            'building-publish-address': "tcp://"+ip_address+":9163",
            'building-subscribe-address': "tcp://"+ip_address+":9162",
            "hosts": {
                core_location:{"pub": "tcp://"+ip_address+":9163",
                                "sub": "tcp://"+ip_address+":9162",
                                "allow": "sub",
                                "type": "core",
                                "building_name": building_name,
                                "zone_id": associated_zone,
                                "mac_address": mac_address
                }
            },
            'cleanup-period': 600000000,
            'uuid': "MultiBuildingService"
    }
    _launch_file = os.path.join(Agents_DIR+"MultiBuilding/multibuildingagent.launch.json")
    with open(_launch_file, 'w') as outfile:
        json.dump(data, outfile, indent=4, sort_keys=True)


cur.execute("SELECT building_name FROM "+db_table_node_info)
node_count = cur.rowcount


current_system_auth_replication = cassandraDB.get_replication('system_auth')
while True:
    print("BEMOSS core >> Listening to connection from BEMOSS node: ")
    recv_data, addr = server_socket.recvfrom(2048)
    print "got something-->:"
    print str(addr)+":"+str(recv_data) +  ":<--"
    #1. add new node to node_info table
    #try:
    node_info = json.loads(recv_data)

    remote_node_name = node_info['node_name']
    if node_info['main_core'] != node_name:
        print 'Got broadcast message from stranger node. Ignoring'
        continue



    remote_init_zone_name = remote_node_name
    remote_node_type = node_info['node_type']
    remote_node_model = node_info['node_model']
    remote_node_status = "ONLINE"
    remote_building_name = node_info['building_name']
    remote_ip_address = addr[0]
    remote_mac_address = node_info['mac_address']
    remote_date_added = datetime.datetime.now()
    remote_communication = "WiFi"
    remote_last_scanned_time = datetime.datetime.now()
    remote_node_location = node_info['node_location']
    add_building_zone(remote_init_zone_name, None)
    #cur = conn.cursor()
    cur.execute("SELECT zone_id FROM "+db_table_building_zone+" WHERE zone_nickname=%s", (remote_init_zone_name,))
    if cur.rowcount != 0:
        _zone_id = int(cur.fetchone()[0])
        add_global_zone_setting(_zone_id, _zone_id, 74, 78, 80)
        remote_associated_zone = _zone_id
        isNew = insertNodeInfo(remote_node_name,remote_node_type,remote_node_model,remote_node_status,remote_building_name,
               remote_ip_address,remote_mac_address, remote_associated_zone, remote_date_added,remote_communication,remote_last_scanned_time)
        node_count += isNew #Add node count only if it is a new node.
        if node_count > current_system_auth_replication:
            cassandraDB.set_replication('system_auth',node_count)

    else: #something wrong with database, ignore this node
        continue
    #2. send message back to client once bemoss client discovered bemoss node
    '''construct message to send to bemoss node '''
    message = json.dumps({
            "node_name": node_name,
            "node_type": node_type,
            "node_model": node_model,
            "node_status": node_status,
            "building_name": building_name,
            "mac_address": mac_address,
            "node_location": core_location,
            "zone_id": associated_zone,
            "remote_node_zone_id": remote_associated_zone
        })
    server_socket.sendto(message, addr)

    #3. update multibuidling agent launch file
    _launch_file = os.path.join(Agents_DIR+"MultiBuilding/multibuildingagent.launch.json")
    with open(_launch_file, 'r+') as f:
        data = json.load(f)
        data['hosts'][remote_node_location] = {"pub": "tcp://"+remote_ip_address+":9163",
                            "sub": "tcp://"+remote_ip_address+":9162",
                            "allow": "sub",
                            "type": "node",
                            "building_name": remote_building_name,
                            "zone_id": remote_associated_zone,
                            "mac_address": remote_mac_address}
        f.seek(0)
        print data
        json.dump(data, f, indent=4, sort_keys=True)

    #Repackage and Re-launch Multibuilding Agent

    with open(_launch_file, 'r') as infile:
        data=json.load(infile)
        agent_id = 'multibuildingagent'
        agentname ='multibuilding'

    os.chdir(os.path.expanduser(settings.PROJECT_DIR + "/env/bin"))
    os.system(#". env/bin/activate"
                  "./volttron-ctl stop --tag " + agent_id+
                  ";./volttron-ctl remove --tag " + agent_id+
                  ";./volttron-ctl clear"+
                  ";./volttron-pkg configure /tmp/volttron_wheels/"+agentname+"agent-0.1-py2-none-any.whl "+ _launch_file+
                  ";./volttron-ctl install "+agent_id+"=/tmp/volttron_wheels/"+agentname+"agent-0.1-py2-none-any.whl"+
                  ";./volttron-ctl start --tag " + agent_id
                  )

    print "UDP server has successfully repackaged and launched Multibuilding Agent"

    os.system(#". env/bin/activate"
                  "./volttron-ctl stop --tag networkagent"+
                  ";./volttron-ctl start --tag networkagent"+
                  ";./volttron-ctl status"
              )

    print "The network agent has also been restarted"


