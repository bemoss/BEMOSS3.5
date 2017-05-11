from volttron.platform.vip.agent import Agent

class BEMOSSAgent(Agent):
    def __init__(self, **kwargs):
        super(BEMOSSAgent, self).__init__(**kwargs)

    def bemoss_publish(self,topic,target,message,headers=None):
        topic1 = 'to/'+target+'/'+topic+'/from/'+self.agent_id
        topic2 = 'to/' +target +  '/from/' + self.agent_id + '/' + topic
        self.vip.pubsub.publish('pubsub', topic1, headers, message)
        self.vip.pubsub.publish('pubsub', topic2, headers, message)
