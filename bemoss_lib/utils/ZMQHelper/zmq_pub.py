# -*- coding: utf-8 -*-
# Authors: BEMOSS Team
# Version: 2.0
# Email: aribemoss@gmail.com
# Created: "2014-10-13 18:45:40"
# Updated: "2015-02-13 15:06:41"


# Copyright © 2014 by Virginia Polytechnic Institute and State University
# All rights reserved
#
# Virginia Polytechnic Institute and State University (Virginia Tech) owns the copyright for the BEMOSS software and
# and its associated documentation ("Software") and retains rights to grant research rights under patents related to
# the BEMOSS software to other academic institutions or non-profit research institutions.
# You should carefully read the following terms and conditions before using this software.
# Your use of this Software indicates your acceptance of this license agreement and all terms and conditions.
#
# You are hereby licensed to use the Software for Non-Commercial Purpose only.  Non-Commercial Purpose means the
# use of the Software solely for research.  Non-Commercial Purpose excludes, without limitation, any use of
# the Software, as part of, or in any way in connection with a product or service which is sold, offered for sale,
# licensed, leased, loaned, or rented.  Permission to use, copy, modify, and distribute this compilation
# for Non-Commercial Purpose to other academic institutions or non-profit research institutions is hereby granted
# without fee, subject to the following terms of this license.
#
# Commercial Use: If you desire to use the software for profit-making or commercial purposes,
# you agree to negotiate in good faith a license with Virginia Tech prior to such profit-making or commercial use.
# Virginia Tech shall have no obligation to grant such license to you, and may grant exclusive or non-exclusive
# licenses to others. You may contact the following by email to discuss commercial use:: vtippatents@vtip.org
#
# Limitation of Liability: IN NO EVENT WILL VIRGINIA TECH, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR REDISTRIBUTE
# THE PROGRAM AS PERMITTED ABOVE, BE LIABLE TO YOU FOR DAMAGES, INCLUDING ANY GENERAL, SPECIAL, INCIDENTAL OR
# CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE OR INABILITY TO USE THE PROGRAM (INCLUDING BUT NOT LIMITED TO
# LOSS OF DATA OR DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD PARTIES OR A FAILURE
# OF THE PROGRAM TO OPERATE WITH ANY OTHER PROGRAMS), EVEN IF VIRGINIA TECH OR OTHER PARTY HAS BEEN ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGES.
#
# For full terms and conditions, please visit https://bitbucket.org/bemoss/bemoss_os.
#
# Address all correspondence regarding this license to Virginia Tech's electronic mail address: vtippatents@vtip.org

from volttron.platform.agent import utils
from volttron.platform.agent import BaseAgent, PublishMixin
from volttron.platform.messaging import headers as headers_mod

import logging
import os

from datetime import datetime

#utils.setup_logging()
_log = logging.getLogger(__name__)

#TODO clean this file
class ZMQ_PUB(PublishMixin, BaseAgent):   
    
    def __init__(self, **kwargs):
        super(ZMQ_PUB, self).__init__(**kwargs)
  
    def setup(self):
        super(ZMQ_PUB, self).setup()
        #self.connectToZMQ()

    #Send message to agent
    def sendToAgent(self,topic, message, content_type, fromUI):
        print os.path.basename(__file__)+"inside sock"
        #sock = self.connectToZMQ();
        #while True:
        #message = constructMessage(topic, message,  content_type, fromUI);
        print os.path.basename(__file__)+"inside sock create connecttoZMQ"
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
            headers_mod.CONTENT_TYPE: content_type,
            headers_mod.DATE: now,
        }
        print "created headers"
        #if isinstance(message, dict):
            #message = str(message)

        self.publish_json(topic, headers, message)
        print "published"
        #return
    
    '''
    Requests the agent for current device status/schedule
    '''
    def requestAgent(self,topic, message, content_type, fromUI):
        print os.path.basename(__file__)+"inside sock of requestAgent"
        #sock = self.connectToZMQ();
        #while True:
        #message = constructMessage(topic, message,  content_type, fromUI);
        print os.path.basename(__file__)+"inside sock create connecttoZMQ"
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
            headers_mod.CONTENT_TYPE: content_type,
            headers_mod.DATE: now,
        }
        print "created headers"
        #message = json.loads(message)
        print topic
        #self.publish("test","test","test msg")
        self.publish(topic, headers, message)
        print "published"

    
    
'''   
from datetime import datetime
from volttron.lite.agent import BaseAgent, PublishMixin
from volttron.lite.messaging import headers as headers_mod
from volttron.lite.agent import utils
import logging

utils.setup_logging()
_log = logging.getLogger(__name__)


class ZMQ_PUB(PublishMixin, BaseAgent):
   
    def __init__(self, configpath,**kwargs):
        print "yeay..in"
        print "entering super"
        super(ZMQ_PUB, self).__init__(**kwargs)
        print "crossed super"
        #self.config = utils.load_config(configpath)
        print "config path crossed"
        #self.sendToAgent(self,topic, message, content_type, fromUI)

    def setup(self):
        # Always call the base class setup()
        print "entering setup"
        super(ZMQ_PUB, self).setup()
        print "setup done"
    
    def sendToAgent(self,topic, message, content_type, fromUI):
        print "inside sock"
        #sock = self.connectToZMQ();
        #while True:
        #message = constructMessage(topic, message,  content_type, fromUI);
        print "inside sock create connecttoZMQ"
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
            headers_mod.CONTENT_TYPE: content_type,
            headers_mod.DATE: now,
        }
        print "created headers"
        #PublishMixin.publish(topic, headers).publish('/ui/zone1/wifithermo3m50/qaz3m50/update/wifi_3m50_01/status', headers, "success")

        if isinstance(message, dict):
            message = str(message)
        self.publish(topic, headers, message)
        print "published"
        return
    
            
    def connectToZMQ(self):
        context = zmq.Context()
        sock = context.socket(zmq.PUSH)
        sock.connect('ipc:///tmp/volttron-lite-agent-publish')
        return sock
    
    def constructMessage(self,topic, message,  content_type, fromUI):
        header = "Headers({Content-Type:"+content_type+",From:"+fromUI+",Time:"+time.ctime()+"})"
        now = datetime.utcnow().isoformat(' ') + 'Z'
        print header
        headers = {
                headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
                headers_mod.DATE: now,
            }
        message = {"Topic:":topic,
                   "Headers":header,
                   "Message:":message}
        print message
        return message'''
