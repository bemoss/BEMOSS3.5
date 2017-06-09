from volttron.platform.vip.agent import Agent
import re
import pytz
from datetime import datetime
from bemoss_lib.utils import date_converter
from bemoss_lib.utils import db_helper
import uuid
from bemoss_lib.utils.offline_table_init import *
import settings
import os

class BEMOSSAgent(Agent):
    def __init__(self, **kwargs):
        super(BEMOSSAgent, self).__init__(**kwargs)
        self.multinode_data = db_helper.get_multinode_data()
        self.node_name = self.multinode_data['this_node']
        if not os.path.isfile(settings.MULTINODE_PARENT_IP_FILE):  # but parent file doesn't exists
            parent_addr = self.multinode_data['known_nodes'][0]['address']
            parent_ip = self.extract_ip(parent_addr)
            with open(settings.MULTINODE_PARENT_IP_FILE, 'w') as f:
                f.write(parent_ip)
        self.curcon = db_helper.db_connection()

    def bemoss_publish(self,topic,target,message,headers=None):
        topic1 = 'to/'+target+'/'+topic+'/from/'+self.agent_id
        topic2 = 'to/' +target +  '/from/' + self.agent_id + '/' + topic
        self.vip.pubsub.publish('pubsub', topic1, headers, message)
        self.vip.pubsub.publish('pubsub', topic2, headers, message)

    def TSDInsert(self,agentID,all_vars,log_vars,cur_timeLocal=None,tablename=None):
        message = dict()
        all_vars = dict(all_vars)  # make a copy to prevent the source from being modified
        for key in all_vars.keys():
            if key not in log_vars:
                all_vars.pop(key)

        message['agentID'] = agentID
        message['all_vars'] = all_vars
        message['log_vars'] = log_vars
        message['cur_timeLocal'] = cur_timeLocal
        message['tablename'] = tablename
        self.vip.pubsub.publish('pubsub','to/tsdagent/insert',message=message)

    def TSDCustomInsert(self, all_vars, log_vars, tablename):
        all_vars = dict(all_vars) #make a copy to prevent the source from being modified
        for key in all_vars.keys():
            if key not in log_vars:
                all_vars.pop(key)
        for key, val in all_vars.items():
            if log_vars[key] == "TIMESTAMP":
                all_vars[key] = date_converter.serialize(val)
            if log_vars[key] == 'UUID':
                all_vars[key] = str(val)

        message = dict()
        message['all_vars'] = all_vars
        message['log_vars'] = log_vars
        message['tablename'] = tablename
        self.vip.pubsub.publish('pubsub', 'to/tsdagent/custominsert', message=message)

    def EventRegister(self,event,reason=None,source=None,event_time=None,notify=True):
        evt_vars = dict()

        event_time = date_converter.localToUTC(event_time) if event_time else datetime.now(pytz.UTC)
        source = source if source else self.agent_id
        reason = reason if reason else 'Unknown'
        logged_by = self.agent_id

        evt_vars['date_id'] = str(event_time.date())
        evt_vars['logged_time'] = datetime.now(pytz.UTC)
        evt_vars['event_id'] = uuid.uuid4()
        evt_vars['time'] = event_time
        evt_vars['source'] = source
        evt_vars['event'] = event
        evt_vars['reason'] = reason
        evt_vars['logged_by']=logged_by
        evt_vars['node_name'] = self.node_name

        #save to cassandra
        self.TSDCustomInsert(all_vars=evt_vars, log_vars=EVENTS_TABLE_VARS,tablename=EVENTS_TABLE_NAME)
        if notify:
            #save to notification table
            localTime = date_converter.UTCToLocal(event_time)
            message = source + ' ' + event + '. Reason: ' + reason
            self.curcon.execute("select id from possible_events where event_name=%s", (event,))
            event_id = self.curcon.fetchone()[0]
            self.curcon.execute(
                "insert into notification (dt_triggered, seen, event_type_id, message) VALUES (%s, %s, %s, %s)",
                (localTime, False, event_id, message))
            self.curcon.commit()

    def extract_ip(self,addr):
        return re.search(r'([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})', addr).groups()[0]

