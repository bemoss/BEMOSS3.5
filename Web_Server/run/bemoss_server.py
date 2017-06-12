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


import json
from zmq.eventloop import ioloop

ioloop.install()
from zmq.eventloop.zmqstream import ZMQStream

import zmq
import os
import sys
sys.path.insert(0,os.path.dirname(os.path.realpath(__file__)).replace('/run', ''))
print sys.path
from tornado import websocket
from tornado import web
from django_web_server.settings import BASE_DIR
from _utils import messages as _
from tornado.options import options, define
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.wsgi
import os
import getpass

import tornado.httpserver
import tornado.ioloop
import tornado.wsgi
from django.core.wsgi import get_wsgi_application
from bemoss_lib.utils.BEMOSS_globals import *
import time

from volttron.platform.vip.agent import Core, Agent
import gevent


ctx = zmq.Context()

current_path = BASE_DIR
# current_path = current_path.replace("/workspace/bemoss_web_ui", "")
# print current_path
#
# push_socket = "ipc://" + current_path + "/.volttron/run/publish"
# sub_socket = "ipc://" + current_path + "/.volttron/run/subscribe"
# print push_socket
# print sub_socket

define('port', type=int, default=8082)
define('host', type=str, default="localhost")

def mysleep():
    gevent.sleep(0.3)

def main():
    print os.path.expanduser("~")
    os.environ['DJANGO_SETTINGS_MODULE'] = 'django_web_server.settings'
    wsgi_app = tornado.wsgi.WSGIContainer(get_wsgi_application())
    tornado_app = tornado.web.Application(
        [
            (r"/socket_agent/(.*)", MainHandler),
            (r"/generic_socket/(.*)", GenericHandler),
            (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': BASE_DIR +
                                                                      "/static/"}),
            ('.*', tornado.web.FallbackHandler, dict(fallback=wsgi_app)),
        ])
    server = tornado.httpserver.HTTPServer(tornado_app)
    server.listen(options.port)
    print _.SERVER_STARTUP.format(options.host, options.port)
    x = tornado.ioloop.PeriodicCallback(mysleep, 4000)
    x.start()
    tornado.ioloop.IOLoop.instance().start()

class WebHandler(web.RequestHandler):
    def get(self):
        pass
        #self.render("/home/kruthika/workspace/bemoss_web_ui/template.html", title="My new title")


class MainHandler(websocket.WebSocketHandler):
    _first = True

    @property
    def ref(self):
        return id(self)

    def initialize(self):
        print 'Initializing tornado websocket'

        self.context = zmq.Context()
        self.sub_socket = self.context.socket(zmq.SUB)
        self.sub_socket.connect(PUB_ADDRESS)
        self.zmq_stream = ZMQStream(self.sub_socket)
        self.zmq_stream.on_recv(self.recv_func)


    def check_origin(self, origin):
        return True

    def open(self, *args, **kwargs):
        self.write_message("Open_Success")
        self.zmq_subscribe(args[0])

    def on_message(self, message):
        if self._first:
            msg = {'message': message, 'id':self.ref, 'action':'connect'}
            print 'in if part - tornado server'
            self._first = False

        else:
            msg = {'message': message, 'id':self.ref, 'action':'message'}
            print 'in else part - tornado server'
            print msg

        self.write_message(msg)

    def on_close(self):
        print("WebSocket closed")
        self.sub_socket.setsockopt(zmq.LINGER, 0)
        self.sub_socket.close()
        self.zmq_stream.close()
        self.context.term()


    def recv_func(self,message):
        #self.process_data(message)
        try:
            message = message[0]
            topic, messagedata = message.split(ZMQ_SEPARATOR)
            messagedata = json.loads(messagedata)
            # self.vip.pubsub.publish('pubsub',topic,message=messagedata)
            print topic, messagedata
            self.write_message({'message':messagedata,'topic':topic})
        except Exception as er:
            print er
            pass

    def process_data(self, data):
        print data
        zmessage = {'topic': '', 'headers': {}, 'message': ''}
        for item in data:
            if '/agent/ui' in item or '/app/ui' in item:
                zmessage['topic'] = item
            elif 'Date' in str(item):
                mesg = json.loads(item)
                zmessage['headers'] = mesg
            else:
                if '[' in item:
                    item = eval(item)
                    print type(item)
                    item = item[0]
                    if item[0] == '{':
                        item = json.loads(item)
                    zmessage['message'] = item
                else:
                    zmessage['message'] = item

        self.write_message(zmessage)

    def zmq_subscribe(self,agent_id):
        #self.sub_socket.setsockopt(zmq.SUBSCRIBE, "")
        topicfilter = "to/ui/"
        self.sub_socket.setsockopt_string(zmq.SUBSCRIBE, "to/ui/from/"+agent_id)
        #self.sub_socket.setsockopt_string(zmq.SUBSCRIBE, u'')


class GenericHandler(MainHandler):
    def zmq_subscribe(self,topic):
        #self.sub_socket.setsockopt_string(zmq.SUBSCRIBE, u'')
        self.sub_socket.setsockopt_string(zmq.SUBSCRIBE, "to/ui/" + topic)

if __name__ == "__main__":
    tornado.options.parse_command_line()
    main()
