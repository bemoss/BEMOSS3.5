# -*- coding: utf-8 -*- {{{
# vim: set fenc=utf-8 ft=python sw=4 ts=4 sts=4 et:
#
# Copyright (c) 2015, Battelle Memorial Institute
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation are those
# of the authors and should not be interpreted as representing official policies,
# either expressed or implied, of the FreeBSD Project.
#

# This material was prepared as an account of work sponsored by an
# agency of the United States Government.  Neither the United States
# Government nor the United States Department of Energy, nor Battelle,
# nor any of their employees, nor any jurisdiction or organization
# that has cooperated in the development of these materials, makes
# any warranty, express or implied, or assumes any legal liability
# or responsibility for the accuracy, completeness, or usefulness or
# any information, apparatus, product, software, or process disclosed,
# or represents that its use would not infringe privately owned rights.
#
# Reference herein to any specific commercial product, process, or
# service by trade name, trademark, manufacturer, or otherwise does
# not necessarily constitute or imply its endorsement, recommendation,
# r favoring by the United States Government or any agency thereof,
# or Battelle Memorial Institute. The views and opinions of authors
# expressed herein do not necessarily state or reflect those of the
# United States Government or any agency thereof.
#
# PACIFIC NORTHWEST NATIONAL LABORATORY
# operated by BATTELLE for the UNITED STATES DEPARTMENT OF ENERGY
# under Contract DE-AC05-76RL01830

#}}}

from __future__ import absolute_import

from datetime import datetime
import logging
import sys
from collections import deque

import gevent
from volttron.platform.vip.agent import Agent, Core, PubSub, compat
from volttron.platform.agent import utils
from volttron.platform.messaging import headers as headers_mod
import zmq
from zmq.eventloop.zmqstream import ZMQStream

import random
import sys
import time
from bemoss_lib.utils.BEMOSSAgent import BEMOSSAgent
from bemoss_lib.utils.BEMOSS_globals import *
import settings
#from . import settings
import json
from bemoss_lib.utils import date_converter
from bemoss_lib.databases.cassandraAPI import cassandraDB

import uuid

utils.setup_logging()
_log = logging.getLogger(__name__)
__version__ = '3.0'



class TSDAgent(Agent):
    '''Listens to everything and publishes a heartbeat according to the
    heartbeat period specified in the settings module.
    '''

    def __init__(self, config_path, **kwargs):
        super(TSDAgent, self).__init__(**kwargs)
        self.config = utils.load_config(config_path)
        self.agent_id = self.config['agentid']
        self.insert_message_queue = deque()
        self.custom_insert_message_queue = deque()
    #
    # @Core.receiver('onsetup')
    # def onsetup(self, sender, **kwargs):
    #     # Demonstrate accessing a value from the config file
    #     pass

    @PubSub.subscribe('pubsub', 'to/tsdagent/insert')
    def insert(self, peer, sender, bus, topic, headers, message):
        self.insert_message_queue.append(message)
        print "Insert Message queued for: " + message['agentID'] + " Total Queue: " + str(len(self.insert_message_queue))

    @PubSub.subscribe('pubsub', 'to/tsdagent/custominsert')
    def customInsert(self, peer, sender, bus, topic, headers, message):
        self.custom_insert_message_queue.append(message)
        print "CustomInsert message queued for: " + message['tablename']+ " Total Queue: " + str(len(self.custom_insert_message_queue))

    def deserialize_date(self,message):
        for key, val in message['all_vars'].items():
            if message['log_vars'][key] == "TIMESTAMP":
                message['all_vars'][key] = date_converter.deserialize(val)
            if message['log_vars'][key] == "UUID":
                try:
                    message['all_vars'][key] = uuid.UUID(val)
                except ValueError:
                    message['all_vars'][key] = None

    @Core.periodic(5)
    def do_insertion_jobs(self):
        while self.insert_message_queue or self.custom_insert_message_queue:
            print "Inserting: ", len(self.insert_message_queue), len(self.custom_insert_message_queue)
            try:
                if self.insert_message_queue:
                    message = self.insert_message_queue.popleft()
                    self.deserialize_date(message)
                    cassandraDB.insert(message['agentID'], message['all_vars'], message['log_vars'],
                                       cur_timeLocal=message['cur_timeLocal'], tablename=message['tablename'])
                if self.custom_insert_message_queue:
                    message = self.custom_insert_message_queue.popleft()
                    self.deserialize_date(message)
                    cassandraDB.customInsert(message['all_vars'], message['log_vars'], tablename=message['tablename'])
            except Exception as er:
                print er
                print "TSD data entry failure"
            time.sleep(0.001)

def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    try:
        utils.vip_main(TSDAgent)
    except Exception as e:
        _log.exception('unhandled exception')


if __name__ == '__main__':
    # Entry point for script
    sys.exit(main())
