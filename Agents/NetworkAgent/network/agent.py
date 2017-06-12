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

import base64
import datetime
import json
import logging
from subprocess import Popen, PIPE
import subprocess
import uuid
import sys
import psycopg2
import re
import settings

from bemoss_lib.utils import find_own_ip
from bemoss_lib.utils.BEMOSS_globals import *
from bemoss_lib.utils.agentstats import agentstats
from bemoss_lib.utils.catcherror import catcherror
from volttron import platform
from volttron.platform.agent import utils
from volttron.platform.vip.agent import Agent, Core, PubSub, compat
from bemoss_lib.utils import db_helper
from bemoss_lib.utils.BEMOSSAgent import BEMOSSAgent
import random
from bemoss_lib.utils import db_helper
#initiliazation
utils.setup_logging()
_log = logging.getLogger(__name__)
Agents_DIR = settings.Agents_DIR
clock_time = 20 #frequency of polling nodes
Agents_Launch_DIR = settings.Agents_Launch_DIR
building_name = settings.PLATFORM['node']['building_name']
db_database = settings.DATABASES['default']['NAME']

my_ip_address = find_own_ip.getIPs()[-1] #use the last IP in the list for host ip

debug_agent = settings.DEBUG
host_name = settings.PLATFORM['node']['name']
db_host = settings.DATABASES['default']['HOST']
db_port = settings.DATABASES['default']['PORT']
db_user = settings.DATABASES['default']['USER']
db_password = settings.DATABASES['default']['PASSWORD']
db_table_node_info = settings.DATABASES['default']['TABLE_node_info']
db_table_node_device = settings.DATABASES['default']['TABLE_node_device']
db_table_device_info = settings.DATABASES['default']['TABLE_device_info']
db_table_device_data = settings.DATABASES['default']['TABLE_device']
db_table_active_alert = settings.DATABASES['default']['TABLE_active_alert']
db_table_device_type = settings.DATABASES['default']['TABLE_device_type']
db_table_bemoss_notify = settings.DATABASES['default']['TABLE_bemoss_notify']
db_table_alerts_notificationchanneladdress = settings.DATABASES['default']['TABLE_alerts_notificationchanneladdress']
db_table_temp_time_counter = settings.DATABASES['default']['TABLE_temp_time_counter']
db_table_temp_failure_time = settings.DATABASES['default']['TABLE_temp_failure_time']
db_table_priority = settings.DATABASES['default']['TABLE_priority']

node_type = settings.PLATFORM['node']['type']
node_name = settings.PLATFORM['node']['name']
my_zone = settings.PLATFORM['node']['zone']

if node_type == "core":
    node_offline_timeout = settings.PLATFORM['node']['node_offline_timeout']
    node_monitor_time = settings.PLATFORM['node']['node_monitor_time']
else:
    node_monitor_time = 60000000  # arbitrary large number since it's not required for type "node"
    node_offline_timeout = 60000000  # arbitrary large number since it's not required for type "node"

#offline_event var


class NetworkAgent(BEMOSSAgent):

    def __init__(self, config_path, **kwargs):
        kwargs['identity'] = 'networkagent'
        super(NetworkAgent, self).__init__(**kwargs)
        self.config = utils.load_config(config_path)
        def get_config(name):
            try:
                kwargs.pop(name)
            except KeyError:
                return self.config.get(name, '')

        self.agent_id = get_config('agent_id')

        self.building_name = building_name
        self.host_ip_address = my_ip_address
        self.db_host = db_host
        self.host_name = host_name
        self.host_type = settings.PLATFORM['node']['type']
        self.host_building_name = building_name

        self.my_node_id = db_helper.get_node_id()

        print "host_zone_id "+str(self.my_node_id)

        self.time_sent_notifications = {}




    @Core.receiver('onsetup')
    def setup(self,sender,**kwargs):
        #super(NetworkAgent, self).setup()
        pass
        #self.multibuilting_subscribe() #can't do this because VIP isn't setup?

    @PubSub.subscribe('pubsub', '')
    def on_match(self, peer, sender, bus,  topic, headers, message):
        '''Use match_all to receive all messages and print them out.'''
        if sender == 'pubsub.compat':
            message = compat.unpack_legacy_message(headers, message)
        _log.debug(
            "Peer: %r, Sender: %r:, Bus: %r, Topic: %r, Headers: %r, "
            "Message: %r", peer, sender, bus, topic, headers, message)

    @PubSub.subscribe('pubsub', 'from/multinodeagent/update_parent')
    def updateParent(self,peer,sender,bus,topic, headers, message):
        print "Updating Connection to database"
        self.curcon.close()  # close old connection
        self.curcon = db_helper.db_connection()  # start new connection using new parent_ip

    # Behavior to listen to message from UI when user change zone of a device
    @PubSub.subscribe('pubsub', 'to/networkagent/status_change')
    #@catcherror('Failed ui-to-networkagent')
    def on_match_change(self,peer,sender,bus,topic, headers, message):
        #can approve or make pending a list of agents
        if debug_agent:
            print "{} >> received the message at {}".format(self.agent_id, datetime.datetime.now())
            print "Topic: {topic}".format(topic=topic)
            print "Headers: {headers}".format(headers=headers)
            print "Message: {message}\n".format(message=message)

        for entry in message:
            volttron_agents_status = agentstats()
            agent_status = entry[STATUS_CHANGE.AGENT_STATUS]
            if STATUS_CHANGE.NODE in entry:
                requested_node_id = int(entry[STATUS_CHANGE.NODE])
            agent_id = entry[STATUS_CHANGE.AGENT_ID]
            is_app=False
            self.curcon.execute('select agent_id from device_info where agent_id=%s',(agent_id,))
            if self.curcon.rowcount:
                is_app = False
            self.curcon.execute('select app_agent_id from application_running where app_agent_id=%s',(agent_id,))
            if self.curcon.rowcount:
                is_app = True

            if 'is_app' in entry:
                is_app = entry['is_app']


            zone_assignment_type = ZONE_ASSIGNMENT_TYPES.TEMPORARY #default zone assignment type

            if STATUS_CHANGE.NODE_ASSIGNMENT_TYPE in entry:
                zone_assignment_type =  entry[STATUS_CHANGE.NODE_ASSIGNMENT_TYPE]

            running = False
            installed = False
            if agent_id in volttron_agents_status:
                installed = True
                running = volttron_agents_status[agent_id] == 'running'

            if agent_status == 'start' and requested_node_id == self.my_node_id:
                if not running:
                    if not is_app:
                        self.initialize_devicedata(agent_id)
                    self.launch_agent(agent_id,installed,is_app)
            elif running and (requested_node_id != self.my_node_id or agent_status == 'stop'):
                self.stopAgent(agent_id)
                continue
            else:
                continue
            self.curcon.execute("SELECT assigned_node_id FROM "+db_table_node_device+ " WHERE agent_id=%s",  (agent_id,))
            if self.curcon.rowcount == 0:
                # update node_device_table with the new zone of a device
                self.curcon.execute("INSERT INTO "+db_table_node_device+" (agent_id, assigned_node_id,current_node_id,date_move) "
                                                                     "VALUES(%s,%s,%s,%s)",
                                 (agent_id, requested_node_id, requested_node_id, datetime.datetime.now()))
                self.curcon.commit()
            else:
                existing_assigned_node_id = self.curcon.fetchone()
                if zone_assignment_type == ZONE_ASSIGNMENT_TYPES.PERMANENT:
                    new_assigned_node_id = requested_node_id
                else:
                    new_assigned_node_id = existing_assigned_node_id
                self.curcon.execute("UPDATE "+db_table_node_device+" SET assigned_node_id=(%s),current_node_id=(%s), \
                date_move=(%s) WHERE agent_id=(%s)",(new_assigned_node_id, requested_node_id, datetime.datetime.now(), agent_id))
                self.curcon.commit()



    def initialize_devicedata(self, agent_id):

        if agent_id in settings.SYSTEM_AGENTS:
            return #System agents already have configuration json file
        self.curcon.execute("SELECT data FROM " + db_table_device_data + " WHERE agent_id=%s", (agent_id,))
        if self.curcon.rowcount == 0:
            # no entry made for this agent
            json_temp = '{}'
            self.curcon.execute(
                "INSERT INTO " + db_table_device_data + " (agent_id, data,network_status,last_scanned_time,last_offline_time,dashboard_view) "
                                                        "VALUES(%s,%s,%s,%s,%s,%s)",
                (agent_id, json_temp, 'ONLINE', datetime.datetime.now(), None, json_temp))
            self.curcon.commit()

    def launch_agent(self,agent_id, installed, is_app=False):
        #_launch_file = os.path.join(dir, launch_file)
        env_path = settings.PROJECT_DIR+'/env/bin/'

        def is_agent_installed(agent_id):
            statusreply = subprocess.check_output(env_path+'volttron-ctl status',shell=True)
            statusreply = statusreply.split('\n')
            agent_installed = False
            reg_search_term = " "+agent_id+" "
            for line in statusreply:
                #print(line, end='') #write to a next file name outfile
                match = re.search(reg_search_term, line)
                if match:  # The agent for this device is running
                    agent_installed = True
                else:
                    pass
            return agent_installed

        if agent_id in settings.SYSTEM_AGENTS:
            #find the case-insensetive match for the folder name
            files_and_folders = os.listdir(settings.PROJECT_DIR+'/Agents/')
            folders = [folder for folder in files_and_folders if os.path.isdir(settings.PROJECT_DIR + '/Agents/' + folder)]
            for folder in folders:
                if agent_id.lower() == folder.lower():
                    agent_folder = folder
                    agent_path = "/Agents/" + agent_folder
                    break
            else:
                raise ValueError('no matching agent folder exists for system agent:'+ agent_id)

            _launch_file = settings.PROJECT_DIR + "/Agents/" + agent_folder + "/" + agent_id+'.launch.json'

        else:
            _launch_file = Agents_Launch_DIR + "/" + agent_id + '.launch'
            with open(_launch_file, 'w') as outfile:
                data = {
                    "agent_id": agent_id,
                }
                json.dump(data, outfile)
            if not is_app:
                self.curcon.execute("select device_model from device_info where agent_id=(%s)", (agent_id,))
                if not self.curcon.rowcount:
                    print "Bad agent_id name"
                    return
                device_model = self.curcon.fetchone()[0]

                self.curcon.execute("select agent_type from supported_devices where device_model=(%s)",(device_model,))
                if not self.curcon.rowcount:
                    print "Non supported device"
                    return
                agent_folder = self.curcon.fetchone()[0]
                agent_path = "/Agents/" + agent_folder
            else:
                self.curcon.execute("select app_type_id from application_running where app_agent_id=(%s)", (agent_id,))
                app_type_id = self.curcon.fetchone()[0]
                self.curcon.execute("select app_folder from application_registered where application_id=(%s)", (app_type_id,))
                agent_folder = self.curcon.fetchone()[0]
                agent_path = "/Applications/code/" + agent_folder
        if not installed:
            os.system(#". env/bin/activate"
                          env_path + "volttron-pkg package " + settings.PROJECT_DIR + agent_path+";"+\
                          env_path+"volttron-pkg configure "+platform.get_home()+"/packaged/"+agent_folder.lower()+"-3.0-py2-none-any.whl "+ _launch_file+";"+\
                          env_path+"volttron-ctl install "+agent_id+"="+platform.get_home()+"/packaged/"+agent_folder.lower()+"-3.0-py2-none-any.whl;"+\
                          env_path+"volttron-ctl start --tag " + agent_id + ";"+\
                          env_path+"volttron-ctl status")
        else:
            os.system(#". env/bin/activate"
                          env_path+"volttron-ctl start --tag " + agent_id +";"+
                          env_path+"volttron-ctl status")


        # p = Popen([  # ". env/bin/activate"
        #         env_path + "volttron-ctl auth-update 0 ;"], stdin=PIPE, shell=True)
        # p.communicate("\n".join(["BEMOSSAGENT", "", "", "BEMOSS_BASIC_AGENT", "", "", "", "", "", "", ""]))

        print "{} >> has successfully launched {} located in {}".format(self.agent_id, agent_id, dir)

    def stopAgent(self, agent_id):
        env_path = settings.PROJECT_DIR + '/env/bin/'
        os.system(  # ". env/bin/activate"
            env_path + "volttron-ctl stop --tag " + agent_id+"; volttron-ctl remove --tag " + agent_id)
        _launch_file = Agents_Launch_DIR + "/" + agent_id + '.launch'
        try:
            os.remove(_launch_file)
        except OSError:
            pass


def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    try:
        utils.vip_main(NetworkAgent)
    except Exception as e:
        _log.exception('unhandled exception')

if __name__ == '__main__':
    # Entry point for script
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
