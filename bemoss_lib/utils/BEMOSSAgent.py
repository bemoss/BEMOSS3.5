from volttron.platform.vip.agent import Agent
import time
import datetime
from bemoss_lib.utils import date_converter
class BEMOSSAgent(Agent):
    def __init__(self, **kwargs):
        super(BEMOSSAgent, self).__init__(**kwargs)

    def bemoss_publish(self,topic,target,message,headers=None):
        topic1 = 'to/'+target+'/'+topic+'/from/'+self.agent_id
        topic2 = 'to/' +target +  '/from/' + self.agent_id + '/' + topic
        self.vip.pubsub.publish('pubsub', topic1, headers, message)
        self.vip.pubsub.publish('pubsub', topic2, headers, message)

    def TSDInsert(self,agentID,all_vars,log_vars,cur_timeLocal=None,tablename=None):
        message = dict()
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

