from volttron.platform.vip.agent import Core, Agent
import gevent
import json
import zmq
from bemoss_lib.utils.BEMOSS_globals import *
import time
def vip_publish(topic,message):
    context = zmq.Context()
    pub_socket = context.socket(zmq.PUB)
    pub_socket.connect(SUB_ADDRESS)
    time.sleep(0.5) #need to wait for the pub_socket to fully connect. If messages from UI aren't reaching to Agents(VIP)
    #try increasing this delay. Also, consider sending dummy messages before real messages (sometimes first message is
    #  lost, no matter what). A much better solution is to keep sending sync message until a feedback is obtained. However,
    # this requires also setting up two way communication and is complicated. Hopefully, you never get to that point.
    # If you don't like this, complain to the ZMQ people, because its how they designed this thing.
    pub_socket.send_string(topic+ZMQ_SEPARATOR+json.dumps(message))
    time.sleep(0.1)
    pub_socket.close()
    context.term()



