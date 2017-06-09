from __future__ import absolute_import

from datetime import datetime
import logging
import sys

from volttron.platform.vip.agent import Agent, Core, PubSub, compat
from volttron.platform.agent import utils
from volttron.platform.messaging import headers as headers_mod
import base64
#from . import settings

import logging
import os
import sys

import uuid
import zmq
import zmq.auth
from zmq.auth.thread import ThreadAuthenticator
import json
import re
import settings
from bemoss_lib.utils.BEMOSS_globals import *
#from bemoss_lib.databases.cassandraAPI import cassandraDB
import subprocess
# address_list = ['tcp://192.168.10.77:9000','tcp://192.168.10.77:9001','tcp://192.168.10.77:9002']
# node_list = ['Node1','Node2','Node3']
from bemoss_lib.utils.BEMOSSAgent import BEMOSSAgent
from bemoss_lib.utils.offline_table_init import *
from bemoss_lib.utils import date_converter
from bemoss_lib.utils import db_helper

utils.setup_logging()
_log = logging.getLogger(__name__)
__version__ = '3.0'

def jsonify(topic, msg):
    """ json encode the message and prepend the topic """
    return topic + ' ' + json.dumps({'message':msg})

def dejsonify(topicmsg):
    """ Inverse of """
    json0 = topicmsg.find('{')
    topic = topicmsg[0:json0].strip()
    msg = json.loads(topicmsg[json0:])
    return topic, msg['message']
import gevent
import time


node_devices_table = settings.DATABASES['default']['TABLE_node_device']

class MultiNodeAgent(BEMOSSAgent):
    '''Listens to everything and publishes a heartbeat according to the
    heartbeat period specified in the settings module.
    '''

    def __init__(self, config_path, **kwargs):
        super(MultiNodeAgent, self).__init__(**kwargs)
        #self.node_health = dict()
        #self.node_last_sync = dict()

        self.agent_id = 'multinodeagent'
        self.identity = self.agent_id

        self.multinode_status = dict()
        self.is_parent = False
        self.last_sync_with_parent = datetime(1991, 1, 1) #equivalent to -ve infinitive
        self.parent_node = None
        self.recently_online_node_list = []  # initialize to lists to empty
        self.recently_offline_node_list = []  # they will be filled as nodes are discovered to be online/offline


    def getMultinodeData(self):
        self.multinode_data = db_helper.get_multinode_data()

        self.nodelist_dict = {node['name']:node for node in self.multinode_data['known_nodes']}
        self.node_name_list = [node['name'] for node in self.multinode_data['known_nodes']]
        self.address_list = [node['address'] for node in self.multinode_data['known_nodes']]
        self.server_key_list = [node['server_key'] for node in self.multinode_data['known_nodes']]
        self.node_name = self.multinode_data['this_node']

        for index,node in enumerate(self.multinode_data['known_nodes']):
            if node['name'] == self.node_name:
                self.node_index = index
                break
        else:
            raise ValueError('"this_node:" entry on the multinode_data json file is invalid')


        for node_name in self.node_name_list: #initialize all nodes data
            if node_name not in self.multinode_status: #initialize new nodes. There could be already the node if this getMultiNode
                # data is being called later
                self.multinode_status[node_name] = dict()
                self.multinode_status[node_name]['health'] = -10 #initialized; never online/offline
                self.multinode_status[node_name]['last_sync_time'] = datetime(1991,1,1)
                self.multinode_status[node_name]['last_online_time'] = None
                self.multinode_status[node_name]['last_offline_time'] = None
                self.multinode_status[node_name]['last_scanned_time'] = None


    def configure_authenticator(self):
        self.auth.allow()
        # Tell authenticator to use the certificate in a directory
        self.auth.configure_curve(domain='*', location=self.public_keys_dir)

    @Core.receiver('onsetup')
    def onsetup(self, sender, **kwargs):
        print "Setup"
        self.getMultinodeData()

        base_dir = settings.PROJECT_DIR + "/Agents/MultiNodeAgent/"
        public_keys_dir = os.path.abspath(os.path.join(base_dir, 'public_keys'))
        secret_keys_dir = os.path.abspath(os.path.join(base_dir, 'private_keys'))

        self.secret_keys_dir = secret_keys_dir
        self.public_keys_dir = public_keys_dir

        if not (os.path.exists(public_keys_dir) and
                    os.path.exists(secret_keys_dir)):
            logging.critical("Certificates are missing - run generate_certificates.py script first")
            sys.exit(1)

        ctx = zmq.Context.instance()
        self.ctx = ctx
        # Start an authenticator for this context.
        self.auth = ThreadAuthenticator(ctx)
        self.auth.start()
        self.configure_authenticator()

        server = ctx.socket(zmq.PUB)

        server_secret_key_filename = self.multinode_data['known_nodes'][self.node_index]['server_secret_key']
        server_secret_file = os.path.join(secret_keys_dir, server_secret_key_filename)
        server_public, server_secret = zmq.auth.load_certificate(server_secret_file)
        server.curve_secretkey = server_secret
        server.curve_publickey = server_public
        server.curve_server = True  # must come before bind
        server.bind(self.multinode_data['known_nodes'][self.node_index]['address'])
        self.server = server

    def check_if_parent(self):
        if self.node_name == self.node_name_list[0]: #The first entry is the parent; always
            self.is_parent = True
            self.node_index = 0
            print "I am the boss now, " + self.node_name
            # start the web-server
            subprocess.check_output(settings.PROJECT_DIR + "/start_webserver.sh " + settings.PROJECT_DIR, shell=True)
            message = dict()
            message[STATUS_CHANGE.AGENT_ID] = 'devicediscoveryagent'
            message[STATUS_CHANGE.NODE] = str(self.node_index)
            message[STATUS_CHANGE.AGENT_STATUS] = 'start'
            message[STATUS_CHANGE.NODE_ASSIGNMENT_TYPE] = ZONE_ASSIGNMENT_TYPES.PERMANENT
            self.bemoss_publish('status_change', 'networkagent', [message])
            self.updateParent(self.node_name)
            print "discoveryagent started"

    def disperseMessage(self, topic, header, message):
        for node_name in self.node_name_list:
            if node_name == self.node_name:
                continue
            self.server.send(jsonify(node_name+'/republish/'+topic,message))

    def republishToParent(self,topic,header,message):
        if self.is_parent:
            return #if I am parent, the message is already published
        for node_name in self.node_name_list:
            if self.multinode_status[node_name]['health'] == 2: #health = 2 is the parent node
                self.server.send(jsonify(node_name+'/republish/'+topic,message))

    @Core.periodic(20)
    def send_heartbeat(self):
        # self.vip.pubsub.publish('pubsub', 'listener', None, {'message': 'Hello Listener'})
        # print 'publishing'
        print "Sending heartbeat"

        last_sync_string = self.last_sync_with_parent.strftime('%B %d, %Y, %H:%M:%S')
        self.server.send(
            jsonify('heartbeat/' + self.node_name + '/' + str(self.is_parent) + '/' + last_sync_string, ""))

    def extract_ip(self,addr):
        return re.search(r'([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})', addr).groups()[0]

    def getNodeId(self, node_name):

        for index, node in enumerate(self.multinode_data['known_nodes']):
            if node['name'] == node_name:
                node_index = index
                break
        else:
            raise ValueError('the node name: ' + node_name + ' is not found in multinode data')

        return node_index

    def getNodeName(self, node_id):
        return self.multinode_data['known_nodes'][node_id]['name']

    def handle_offline_nodes(self, node_name_list):
        if self.is_parent:
            # start all the agents belonging to that node on this node
            command_group = []
            for node_name in node_name_list:
                node_id = self.getNodeId(node_name)
                #put the offline event into cassandra events log table, and also create notification
                self.EventRegister('node-offline',reason='communication-error',source=node_name)
                # get a list of agents that were supposedly running in that offline node
                self.curcon.execute("SELECT agent_id FROM " + node_devices_table + " WHERE assigned_node_id=%s",
                            (node_id,))

                if self.curcon.rowcount:
                    agent_ids = self.curcon.fetchall()

                    for agent_id in agent_ids:
                        message = dict()
                        message[STATUS_CHANGE.AGENT_ID] = agent_id[0]
                        message[STATUS_CHANGE.NODE] = str(self.node_index)
                        message[STATUS_CHANGE.AGENT_STATUS] = 'start'
                        message[STATUS_CHANGE.NODE_ASSIGNMENT_TYPE] = ZONE_ASSIGNMENT_TYPES.TEMPORARY
                        command_group += [message]
            print "moving agents from offline node to parent: " + str(node_name_list)
            print command_group
            if command_group:
                self.bemoss_publish('status_change','networkagent',command_group)

    def handle_online_nodes(self, node_name_list):
        if self.is_parent:
            # start all the agents belonging to that nodes back on them
            command_group = []
            for node_name in node_name_list:

                node_id = self.getNodeId(node_name)

                self.EventRegister('node-online',reason='communication-restored',source=node_name)

                #get a list of agents that were supposed to be running in that online node
                self.curcon.execute("SELECT agent_id FROM " + node_devices_table + " WHERE assigned_node_id=%s",
                                    (node_id,))
                if self.curcon.rowcount:
                    agent_ids = self.curcon.fetchall()
                    for agent_id in agent_ids:
                        message = dict()
                        message[STATUS_CHANGE.AGENT_ID] = agent_id[0]
                        message[STATUS_CHANGE.NODE_ASSIGNMENT_TYPE] = ZONE_ASSIGNMENT_TYPES.PERMANENT
                        message[STATUS_CHANGE.NODE] = str(self.node_index)
                        message[STATUS_CHANGE.AGENT_STATUS] = 'stop'  #stop in this node
                        command_group += [message]
                        message = dict(message) #create another copy
                        message[STATUS_CHANGE.NODE] = str(node_id)
                        message[STATUS_CHANGE.AGENT_STATUS] = 'start' #start in the target node
                        command_group += [message]


            print "Moving agents back to the online node: " + str(node_name_list)
            print command_group

            if command_group:
                self.bemoss_publish('status_change','networkagent',command_group)

    def updateParent(self,parent_node_name):
        parent_ip = self.extract_ip(self.nodelist_dict[parent_node_name]['address'])
        write_new = False
        if not os.path.isfile(settings.MULTINODE_PARENT_IP_FILE):  # but parent file doesn't exists
            write_new = True
        else:
            with open(settings.MULTINODE_PARENT_IP_FILE, 'r') as f:
                read_ip = f.read()
            if read_ip != parent_ip:
                write_new = True
        if write_new:
            with open(settings.MULTINODE_PARENT_IP_FILE, 'w') as f:
                f.write(parent_ip)
            if self.curcon:
                self.curcon.close() #close old connection
            self.curcon = db_helper.db_connection() #start new connection using new parent_ip
            self.vip.pubsub.publish('pubsub','from/multinodeagent/update_parent')

    @Core.periodic(60)
    def check_health(self):

        for node_name, node in self.multinode_status.items():
            if node['health'] > 0 : #initialize all online nodes to 0. If they are really online, they should change it
                #  back to 1 or 2 (parent) within 30 seconds throught the heartbeat.
                node['health'] = 0

        gevent.sleep(30)
        parent_node_name = None #initialize parent node
        online_node_exists = False
        for node_name, node in self.multinode_status.items():
            node['last_scanned_time'] = datetime.now()
            if node['health'] == 0:
                node['health'] = -1
                node['last_offline_time'] = datetime.now()
                self.recently_offline_node_list += [node_name]
            elif node['health'] == -1: #offline since long
                pass
            elif node['health'] == -10: #The node was initialized to -10, and never came online. Treat it as recently going
                # offline for this iteration so that the agents that were supposed to be running there can be migrated
                node['health'] = -1
                self.recently_offline_node_list += [node_name]
            elif node['health'] == 2: #there is some parent node present
                parent_node_name = node_name
            if node['health'] >0:
                online_node_exists = True #At-least one node (itself) should be online, if not some problem

        assert online_node_exists, "At least one node (current node) must be online"
        if parent_node_name: #parent node exist
            self.updateParent(parent_node_name)

        for node in self.multinode_data['known_nodes']:
            print node['name'] + ': ' + str(self.multinode_status[node['name']]['health'])

        if self.is_parent:
            #if this is a parent node, update the node_info table
            if self.curcon is None: #if no database connection exists make connection
                self.curcon = db_helper.db_connection()

            tbl_node_info =  settings.DATABASES['default']['TABLE_node_info']
            self.curcon.execute('select node_id from '+ tbl_node_info)
            to_be_deleted_node_ids = self.curcon.fetchall()
            for index, node in enumerate(self.multinode_data['known_nodes']):
                if (index,) in to_be_deleted_node_ids:
                    to_be_deleted_node_ids.remove((index,)) #don't remove this current node
                result = self.curcon.execute('select * from ' + tbl_node_info + ' where node_id=%s',(index,))
                node_type = 'parent' if self.multinode_status[node['name']]['health'] == 2 else "child"
                node_status = "ONLINE" if self.multinode_status[node['name']]['health'] > 0 else "OFFLINE"
                ip_address = self.extract_ip(node['address'])
                last_scanned_time = self.multinode_status[node['name']]['last_online_time']
                last_offline_time = self.multinode_status[node['name']]['last_offline_time']
                last_sync_time = self.multinode_status[node['name']]['last_sync_time']

                var_list = "(node_id,node_name,node_type,node_status,ip_address,last_scanned_time,last_offline_time,last_sync_time)"
                value_placeholder_list = "(%s,%s,%s,%s,%s,%s,%s,%s)"
                actual_values_list = (index, node['name'],node_type, node_status, ip_address, last_scanned_time, last_offline_time, last_sync_time)

                if self.curcon.rowcount == 0:
                    self.curcon.execute("insert into " + tbl_node_info + " " + var_list +" VALUES" + value_placeholder_list, actual_values_list )
                else:
                    self.curcon.execute(
                        "update " + tbl_node_info + " SET " + var_list + " = " + value_placeholder_list + " where node_id = %s",
                        actual_values_list+(index,))
            self.curcon.commit()

            for id in to_be_deleted_node_ids:
                self.curcon.execute('delete from accounts_userprofile_nodes where nodeinfo_id=%s',id) #delete entries in user-profile for the old node
                self.curcon.commit()
                self.curcon.execute('delete from ' + tbl_node_info + ' where node_id=%s',id) #delete the old nodes
                self.curcon.commit()



            if self.recently_online_node_list: #Online nodes should be handled first because, the same node can first be
                #on both recently_online_node_list and recently_offline_node_list, when it goes offline shortly after
                #coming online
                self.handle_online_nodes(self.recently_online_node_list)
                self.recently_online_node_list = []  # reset after handling
            if self.recently_offline_node_list:
                self.handle_offline_nodes(self.recently_offline_node_list)
                self.recently_offline_node_list = []  # reset after handling


    def connect_client(self,node):
        server_public_file = os.path.join(self.public_keys_dir, node['server_key'])
        server_public, _ = zmq.auth.load_certificate(server_public_file)
        # The client must know the server's public key to make a CURVE connection.
        self.client.curve_serverkey = server_public
        self.client.setsockopt(zmq.SUBSCRIBE, 'heartbeat/')
        self.client.setsockopt(zmq.SUBSCRIBE, self.node_name)
        self.client.connect(node['address'])

    def disconnect_client(self,node):
        self.client.disconnect(node['address'])


    @Core.receiver('onstart')
    def onstart(self, sender, **kwargs):

        self.check_if_parent()
        print "Starting to receive Heart-beat"
        self.vip.heartbeat.start_with_period(15)
        client = self.ctx.socket(zmq.SUB)
        # We need two certificates, one for the client and one for
        # the server. The client must know the server's public key
        # to make a CURVE connection.

        client_secret_key_filename = self.multinode_data['known_nodes'][self.node_index]['client_secret_key']
        client_secret_file = os.path.join(self.secret_keys_dir,client_secret_key_filename)
        client_public, client_secret = zmq.auth.load_certificate(client_secret_file)
        client.curve_secretkey = client_secret
        client.curve_publickey = client_public

        self.client = client

        for node in self.multinode_data['known_nodes']:
            self.connect_client(node)

        print "Starting to listen"
        try:
            while True: #read messages
                if client.poll(1000):
                    topic,msg = dejsonify(client.recv())
                    topic_list = topic.split('/')
                    if topic_list[0]=='heartbeat':
                        node_name = topic_list[1]
                        is_parent = topic_list[2]
                        last_sync_with_parent =  topic_list[3]
                        if self.multinode_status[node_name]['health'] < 0: #the node health was <0 , means offline
                            print node_name + " is back online"
                            self.recently_online_node_list += [node_name]

                        if is_parent.lower() in ['false','0']:
                            self.multinode_status[node_name]['health'] = 1
                        elif is_parent.lower() in ['true','1']:
                            self.multinode_status[node_name]['health'] = 2
                            self.parent_node = node_name
                        else:
                            raise ValueError('Invalid is_parent string in heart-beat message')

                        self.multinode_status[node_name]['last_online_time'] = datetime.now()

                    if topic_list[0]==self.node_name:
                        #message addressed to this node

                        if topic_list[1] == 'republish':
                            new_topic = '/'.join(topic_list[2:]+['repub-by-'+self.node_name,'republished'])
                            self.vip.pubsub.publish('pubsub',new_topic,None,msg)

                    print self.node_name+": "+topic, str(msg)

                else:
                    gevent.sleep(2)

        except Exception as er:
            print "error"
            print er

        # stop auth thread
        self.auth.stop()


    @PubSub.subscribe('pubsub', 'to/multinodeagent/')
    def updateMultinodeData(self, peer, sender, bus, topic, headers, message):
        print "Updating Multinode data"
        topic_list = topic.split('/')
        self.configure_authenticator()
        #to/multinodeagent/from/<doesn't matter>/update_multinode_data
        if topic_list[4] == 'update_multinode_data':
            old_multinode_data = self.multinode_data
            self.getMultinodeData()
            for node in self.multinode_data['known_nodes']:
                if node not in old_multinode_data['known_nodes']:
                    print "New node has been added to the cluster: " + node['name']
                    print "We will connect to it"
                    self.connect_client(node)

            for node in old_multinode_data['known_nodes']:
                if node not in self.multinode_data['known_nodes']:
                    print "Node has been removed from the cluster: " + node['name']
                    print "We will disconnect from it"
                    self.disconnect_client(node)
                    # TODO: remove it from the node_info table

        print "yay! got it"

    @PubSub.subscribe('pubsub','to/')
    def relayToMessage(self, peer, sender, bus, topic, headers, message):
        print topic
        topic_list = topic.split('/')
        #to/<some_agent_or_ui>/topic/from/<some_agent_or_ui>
        to_index = topic_list.index('to') + 1
        if 'from' in topic_list:
            from_index = topic_list.index('from') + 1
            from_entity = topic_list[from_index]

        to_entity = topic_list[to_index]
        last_field = topic_list[-1]
        if last_field == 'republished': #it is already a republished message, no need to republish
            return

        if to_entity in settings.PARENT_NODE_SYSTEM_AGENTS :
            if not self.is_parent:
                self.republishToParent(topic,headers,message)
        else:
            self.curcon.execute("SELECT current_node_id FROM " + node_devices_table + " WHERE agent_id=%s",
                                (to_entity,))
            if self.curcon.rowcount:
                node_id = self.curcon.fetchone()[0]
                if node_id != self.node_index:
                    self.server.send(jsonify(self.getNodeName(node_id) + '/republish/' + topic, message))
            else:
                self.disperseMessage(topic, headers, message) #republish to all nodes if we don't know where to send

    @PubSub.subscribe('pubsub','from/')
    def relayFromMessage(self, peer, sender, bus, topic, headers, message):
        topic_list = topic.split('/')
        #from/<some_agent_or_ui>/topic
        from_entity = topic_list[1]
        last_field = topic_list[-1]
        if last_field == 'republished': #it is a republished message, no need to publish
            return
        self.disperseMessage(topic, headers, message) #republish to all nodes

    # @PubSub.subscribe('pubsub', '')
    # def on_match(self, peer, sender, bus,  topic, headers, message):
    #     '''Use match_all to receive all messages and print them out.'''
    #     # if sender == 'pubsub.compat':
    #     #     message = compat.unpack_legacy_message(headers, message)
    #     # _log.debug(
    #     #     "Peer: %r, Sender: %r:, Bus: %r, Topic: %r, Headers: %r, "
    #     #     "Message: %r", peer, sender, bus, topic, headers, message)



def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    try:
        utils.vip_main(MultiNodeAgent)
    except Exception as e:
        _log.exception('unhandled exception')


if __name__ == '__main__':
    # Entry point for script
    sys.exit(main())
