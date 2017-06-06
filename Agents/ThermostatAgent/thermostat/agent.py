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

import sys
import json
import logging
import os
from volttron.platform.agent import utils
from volttron.platform.messaging import headers as headers_mod
import datetime


from volttron.platform.vip.agent import Core
from Agents.BasicAgent.basic.agent import BasicAgent
from bemoss_lib.utils.BEMOSS_ONTOLOGY import BEMOSS_ONTOLOGY


import time
import uuid
from bemoss_lib.utils import db_helper
from bemoss_lib.utils.offline_table_init import *

utils.setup_logging()
_log = logging.getLogger(__name__)


# Step1: Agent Initialization
class ThermostatAgent(BasicAgent):

    def __init__(self, **kwargs):
        super(ThermostatAgent, self).__init__(**kwargs)
        # 1. initialize all agent variables
        self.variables = kwargs
        if hasattr(self.Device, 'getDeviceSchedule'):
            self.device_supports_schedule = True
        else:
            self.device_supports_schedule = False
        if hasattr(self.Device, 'device_supports_auto'):
            self.device_supports_auto = self.Device.device_supports_auto
        else:
            self.device_supports_auto = False
        self.authorized_active_schedule = []
        self.time_sent_notifications_device_tampering = datetime.datetime.now()
        self.first_time_detect_device_tampering = True
        self.event_ids = list()
        self.time_sent_notifications = {}
        self.changed_variables = None
        self.lastUpdateTime = datetime.datetime.now()
        self.runningSeconds = 0
        self.variables['anti_tampering'] = 'DISABLED'
        self.first_time_update = True
        self.get_sch_day = datetime.datetime.now().day
        self.already_offline = False
        self.oldschpoints = {}
        self.offline_id = None
        self.thermostat_mode = ''
        try:
            self.curcon.execute("SELECT device_model FROM device_info WHERE agent_id=%s", (self.agent_id,))
            self.device_model = self.curcon.fetchone()[0]
        except Exception as er:
            print er
            print 'Failure @ get device model in init.'
        if self.device_supports_schedule:
            try:
                self.Device.getDeviceSchedule()
            except:
                print('Failure @ thermostatagent init getDeviceSchedule.')

    # 2. agent setup method
    @Core.receiver('onsetup')
    def agent_setup(self, sender, **kwargs):
        super(ThermostatAgent, self).agent_setup(sender, **kwargs)
        # Do a one time push when we start up so we don't have to wait for the periodic
        # self.timer(1, self.deviceMonitorBehavior)
        self.core.periodic(self.device_monitor_time, self.deviceMonitorBehavior)
        try:
            self.curcon.execute("SELECT data FROM " + self.db_table_device + " WHERE agent_id=%s", (self.agent_id,))
            data = self.curcon.fetchone()[0]
            if data == {} or 'anti_tampering' not in data.keys() or data['anti_tampering'] is None:
                # update initial value of anti_tampering column of a thermostat to 'DISABLED'
                self.variables['anti_tampering'] = 'DISABLED'
                post_data = {'anti_tampering': self.variables['anti_tampering']}
                self.curcon.execute("UPDATE " + self.db_table_device + " SET data=%s WHERE agent_id=%s",
                                 (json.dumps(post_data), self.agent_id))
                self.curcon.commit()
            else:
                self.variables['anti_tampering'] = data['anti_tampering']
        except:
            print "{} >> cannot update anti_tampering field of thermostat data".format(self.agent_id)

        # TODO: changes need to be done on UI side.
        topic_ui_app = 'to/scheduler_' + self.agent_id + '/update/'

        self.vip.pubsub.subscribe(peer='pubsub', prefix=topic_ui_app, callback=self.updateScheduleMsgFromUI)


    def updateScheduleMsgFromUI(self,peer, sender, bus, topic,headers,message):
        _data = json.loads(message)
        schedule = _data['content']
        result = 'failure'
        topic_app_ui = 'to/ui/from/scheduler/' + self.agent_id + '/update/response'
        if self.device_supports_schedule:
            result = self.updateScheduleToDevice(schedule=schedule)

        _headers = {
            'AppName': 'scheduler',
            'AgentID': self.agent_id,
            headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.JSON,
            headers_mod.FROM: self.agent_id,
            headers_mod.TO: 'ui'
        }
        _message = result
        self.vip.pubsub.publish('pubsub', topic_app_ui, _headers, _message)

    def updateScheduleToDevice(self,schedule=None):

        _time_receive_update_from_ui = datetime.datetime.now()
        print "Agent {} Speaking:  >> got new update from UI at {}".format(self.agent_id,
                                                                           _time_receive_update_from_ui)
        try:
            # 1. get schedule from UI
            _new_schedule_object = schedule

            # set self.current_schedule_object to be the new schedule
            self.current_schedule_object = _new_schedule_object['thermostat']
            weeklySchedule = self.current_schedule_object[self.agent_id]['schedulers']['everyday']

            days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            newSchedule = dict()
            for day in days:
                newSchedule[day] = [
                    [x['nickname'], int(x['at']), int(float(x['cool_setpoint'])), int(float(x['heat_setpoint']))]
                    for x in weeklySchedule[day]]

            newSchedule['Enabled'] = 'everyday' in self.current_schedule_object[self.agent_id]['active']

            self.authorized_scheduleData = newSchedule
            self.set_variable('scheduleData', newSchedule)
            self.Device.setDeviceSchedule(newSchedule)
            # 3. get currently active schedule
            return 'success'
        except Exception as er:
            print "Update Schedule to device failed"
            print er
            return 'failure'

    def updateScheduleFromDevice(self):

        #self.Device.getDeviceSchedule()
        scheduleData = self.Device.get_variable('scheduleData')

        if scheduleData is None or len(scheduleData) == 0:
            raise ValueError("Scheduledata is empty")

        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        index = 0
        everyday = dict()
        for day in days:
            everyday[day] = list()
            id = 0
            for entry in scheduleData[day]:
                everyday[day].append(dict(
                    {"at": str(entry[1]), "id": str(id), "nickname": entry[0], "cool_setpoint": str(entry[2]),
                     "heat_setpoint": str(entry[3])}))
                id += 1

        self.curcon.execute("select schedule from schedule_data where agent_id=%s",(self.agent_id,))
        if self.curcon.rowcount:
            # file already exists
            _old_schedule_object = self.curcon.fetchone()[0]
            old_active = _old_schedule_object['thermostat'][self.agent_id]['active']
            if scheduleData['Enabled'] == False:
                if 'everyday' in old_active:
                    _old_schedule_object['thermostat'][self.agent_id]['active'].remove('everyday')
            else:
                if 'everyday' not in old_active:
                    _old_schedule_object['thermostat'][self.agent_id]['active'].append('everyday')

            _old_schedule_object['thermostat'][self.agent_id]['schedulers']['everyday'] = everyday
            _json_data = json.dumps(_old_schedule_object)
            self.curcon.execute("UPDATE schedule_data SET schedule=%s WHERE agent_id=%s",(_json_data,self.agent_id))
            self.curcon.commit()
        else:
            active_schedule = ['everyday'] if scheduleData['Enabled'] else []

            _json_data = json.dumps({"thermostat": {
                self.agent_id: {
                    "active": active_schedule,
                    "inactive": [],
                    "schedulers": {"everyday": everyday}
                }}})

            self.curcon.execute("insert into schedule_data (agent_id, schedule) VALUES (%s, %s)",(self.agent_id,_json_data))
            self.curcon.commit()



    # 3. deviceMonitorBehavior (TickerBehavior)
    def deviceMonitorBehavior(self):
        # step1: get current status of a thermostat, then map keywords and variables to agent knowledge
        try:
            self.Device.getDeviceStatus()

            if self.device_supports_schedule:
                # For RadioThermostat, everytime when queried with schedule information,
                # it will automatically change the setpoint to schedule setpoint from current setpoint back and forth
                # for several times. This breaks temporary hold. As a result, we only query RadioThermostat
                # once a day during mid-night about the schedule on device. This behavior of RadioThermostat
                # has been reported to the manufacturer to see if this is a device bug.
                if 'CT30' in self.device_model or 'CT50' in self.device_model:
                    hour = datetime.datetime.now().hour
                    day = datetime.datetime.now().day
                    if self.first_time_update or hour == 2 and self.get_sch_day != day:
                        self.Device.getDeviceSchedule()
                        self.get_sch_day = day
                        if self.Device.get_variable('thermostat_mode') == 'HEAT':
                            setpoint = "heat_setpoint"
                            setpoint_value = self.Device.get_variable('heat_setpoint')
                        elif self.Device.get_variable('thermostat_mode') == 'COOL':
                            setpoint = "cool_setpoint"
                            setpoint_value = self.Device.get_variable('cool_setpoint')
                        try:
                            self.Device.setDeviceStatus({"thermostat_mode":self.Device.get_variable('thermostat_mode'),setpoint:setpoint_value,"hold":self.Device.get_variable('hold')})
                            thermovars = dict(self.Device.variables)
                            thermovars['user']='radio-hack'
                            self.TSDInsert(self.agent_id,thermovars,self.log_variables)
                        except:
                            print('Error @ setDeviceStatus after Radiothermostat getDeviceSchedule')
                else:
                    self.Device.getDeviceSchedule()
            else:
                pass

        except Exception as er:
            print er
            print("device connection is not successful")

        self.changed_variables = dict()
        try:
            self.curcon.execute("SELECT data FROM " + self.db_table_device + " WHERE agent_id=%s", (self.agent_id,))
            if self.curcon.rowcount != 0:
                self.variables['anti_tampering'] = self.curcon.fetchone()[0]['anti_tampering']
            else:
                pass
        except Exception as er:
            print "Error accessing anti_tampering field", er

        if self.device_supports_schedule:
            if self.get_variable('scheduleData') != self.Device.get_variable('scheduleData'):
                self.variables['scheduleData'] = self.Device.get_variable('scheduleData')
                if self.variables['anti_tampering'] == 'DISABLED' or self.first_time_update:
                    self.authorized_scheduleData = self.variables['scheduleData']
                    try:
                        self.updateScheduleFromDevice()
                        print "Device schedule updated from Device", self.agent_id
                    except Exception as er:
                        print 'Schedule Update failed'
                        print er

                elif self.variables['anti_tampering'] == 'ENABLED':
                    print "Device Schedule Change detected."
                    self.device_tampering_detection()
                    pass  # device tampering will take care to set it back.

        for v in self.log_variables:
            if v in self.Device.variables:
                if v not in self.variables or self.variables[v] != self.Device.variables[v]:
                    self.variables[v] = self.Device.variables[v]
                    self.changed_variables[v] = self.log_variables[v]
            else:
                if v not in self.variables:  # it won't be in self.variables either (in the first time)
                    self.changed_variables[v] = self.log_variables[v]
                    self.variables[v] = None

        if self.device_supports_schedule:
            temp_schpoints = self.Device.getScheduleSetpoint(datetime.datetime.now())
            if temp_schpoints is not None:
                if type(temp_schpoints) != dict: #it must be a list, if not dict, with [cool_setpoint,heat_setpoint]
                    schpoints =  dict()
                    schpoints['cool_setpoint']=temp_schpoints[0]
                    schpoints['heat_setpoint']=temp_schpoints[1]
                else:
                    schpoints = dict(temp_schpoints)

                transit = False
                if schpoints != self.oldschpoints:
                    transit = True
                for v in ['heat_setpoint','cool_setpoint']:
                    
                    if v not in self.Device.variables:
                        #for the hidden setpoint, copy from schedule for the first time, or if hold is None, or
                        #if the schedule has just changed, and hold is temporary
                        if self.variables[v] is None or self.variables['hold'] in [0,'0'] \
                                or (self.variables['hold'] in [1,'1'] and transit):
                            self.variables[v] = schpoints[v]
                            if transit is True:
                                self.changed_variables[v] = self.log_variables[v]
                                # self.updateDB(self.db_table_device, v, 'agent_id', self.variables[v], self.agent_id)

                if transit is True:
                    self.updatePostgresDB()
                self.oldschpoints = dict(schpoints)

        if self.first_time_update:

            if self.get_variable('heat_setpoint') is None:
                self.curcon.execute("SELECT data FROM " + self.db_table_device + " WHERE agent_id=%s", (self.agent_id,))
                if self.curcon.rowcount != 0:
                    try:
                        self.variables['heat_setpoint'] = self.curcon.fetchone()[0]['heat_setpoint']
                    except KeyError:
                        self.variables['heat_setpoint'] = 72
                else:
                    self.variables['heat_setpoint'] = 72 # default when device is in cool mode, no heat_setpoint provided

            if self.get_variable('cool_setpoint') is None:
                self.curcon.execute("SELECT data FROM " + self.db_table_device + " WHERE agent_id=%s", (self.agent_id,))
                if self.curcon.rowcount != 0:
                    try:
                        self.variables['cool_setpoint'] = self.curcon.fetchone()[0]['cool_setpoint']
                    except KeyError:
                        self.variables['cool_setpoint'] = 75
                else:
                    self.variables['cool_setpoint'] = 75 # default when device is in heat mode, no cool_setpoint provided

            # if self.get_variable('thermostat_mode') is not None:
            #     self.authorized_bemoss_mode = self.get_variable('thermostat_mode')
            # else:
            #     pass
            if self.get_variable('thermostat_mode') is not None:
                self.curcon.execute("SELECT data FROM " + self.db_table_device + " WHERE agent_id=%s", (self.agent_id,))

                if self.curcon.rowcount != 0:
                    try:
                        mode = self.curcon.fetchone()[0]['thermostat_mode']
                    except KeyError:
                        mode = 'COOL'
                    self.variables['bemoss_mode'] = mode
                else:
                    self.variables['bemoss_mode'] = self.variables['thermostat_mode']
            else:
                self.variables['bemoss_mode'] = 'COOL'

            if self.get_variable('fan_mode') is not None:
                self.authorized_fan_mode = self.get_variable('fan_mode')
            else:
                pass
            # heat_setpoint and cool_setpoint should not be None because they are initialized already above
            self.authorized_heat_setpoint = self.get_variable('heat_setpoint')
            self.authorized_cool_setpoint = self.get_variable('cool_setpoint')
            self.first_time_update = False
            self.changed_variables = self.log_variables  # log everything the first time


        self.onlineOfflineDetection()
        try:
            # put the last scan time on database
            _time_stamp_last_scanned = str(datetime.datetime.now())
            self.curcon.execute("UPDATE "+self.db_table_device+" SET last_scanned_time=%s "
                             "WHERE agent_id=%s",
                             (_time_stamp_last_scanned, self.agent_id))
            self.curcon.commit()
        except Exception as er:
            print er
            print("ERROR: {} failed to update bemoss database".format(self.agent_id))

        if len(self.changed_variables) == 0:
            print 'nothing changed'
            return
        else:
            print 'These things changed:'
            for key in self.changed_variables.keys():
                print key +':'+str(self.variables[key])
        self.updateUI()

        # step2: determine whether device is tampered by unauthorized action

        if self.variables['anti_tampering'] == 'DISABLED':  # set points of device can be changed
            print "{} >> allow user change thermostat settings".format(self.agent_id)
            pass
        else:
            print "{} >> doesn't allow user change thermostat settings".format(self.agent_id)
            self.device_tampering_detection()

        # step3: update PostgresQL (meta-data) database
        self.updatePostgresDB()

        # step4: update cassandra database
        self.saveCassandraDB()

    # 5. deviceControlBehavior (generic behavior)
    def deviceControlBehavior(self,peer, sender, bus, topic,headers,message):
        print self.agent_id + " got\nTopic: {topic}".format(topic=topic)
        print "Headers: {headers}".format(headers=headers)
        print "Message: {message}\n".format(message=message)
        # step1: change device status according to the receive message
        topic_list = topic.split('/')
        return_index = topic_list.index('from') + 1
        return_entity = topic_list[return_index]

        setDeviceStatusResult=True
        UIdata = dict()
        if self.isPostmsgValid(message):  # check if the data is valid
            # _data = json.dumps(message[0])
            _data = message
            UIdata = dict(_data)
            if 'thermostat_mode' in UIdata: #convert thermostat_mode to bemoss_mode
                UIdata['bemoss_mode']=UIdata.pop('thermostat_mode')

            if 'user' in _data:
                self.variables['user'] = _data.pop('user')
            else:
                self.variables['user'] = 'unknown-UI'
                UIdata['user'] = 'unknonw-UI'

            for k, v in _data.items():
                if k == 'thermostat_mode':
                    self.variables['bemoss_mode'] = _data.get('thermostat_mode')

                    for k2, v2 in _data.items():
                        if k2 == 'heat_setpoint':
                            self.authorized_heat_setpoint = _data.get('heat_setpoint')
                            self.variables['heat_setpoint'] = _data.get('heat_setpoint')
                        elif k2 == 'cool_setpoint':
                            self.authorized_cool_setpoint = _data.get('cool_setpoint')
                            self.variables['cool_setpoint'] = _data.get('cool_setpoint')
                elif k == 'fan_mode':
                    self.authorized_fan_mode = _data.get('fan_mode')
                elif k == 'anti_tampering':
                    self.variables['anti_tampering'] = _data.get('anti_tampering')
                    # try:
                    #     self.curcon.execute("UPDATE " + self.db_table_device + " SET override=%s WHERE agent_id=%s",
                    #                  (self._override, self.agent_id))
                    #     self.curcon.commit()
                    # except Exception as er:
                    #     print 'override value not updated in db ' + str(er)
                elif k=='hold':
                    self.variables['hold'] = _data.get('hold')
                else:
                    pass
            print "{} >> self.authorized_bemoss_mode {}".format(self.agent_id, self.get_variable('bemoss_mode'))
            print "{} >> self.authorized_heat_setpoint {}".format(self.agent_id, self.authorized_heat_setpoint)
            print "{} >> self.authorized_cool_setpoint {}".format(self.agent_id, self.authorized_cool_setpoint)
            print "{} >> self.authorized_fan_mode {}".format(self.agent_id, self.authorized_fan_mode)
            try:
                if self.variables['bemoss_mode'].upper() in ['HEAT','COOL','OFF','AUTO'] or self.device_supports_auto:
                    self.variables['thermostat_mode'] = self.variables['bemoss_mode']
                    setDeviceStatusResult = self.Device.setDeviceStatus(_data)  # convert received message from string to JSON
                # elif self.variables['bemoss_mode'].upper() == 'AUTO':
                #     #get new modes and set-points if necessary to implement Auto mode
                #     newmodes = self.manualAuto()
                #     if 'thermostat_mode' in newmodes and newmodes['thermostat_mode'] == 'HEAT':
                #         #If the thermostat mode needs to be changed to Heat, apply cool setpoint first, then heat setpoint
                #         cool_priority = 1
                #     else:
                #         cool_priority = 2
                #
                #     for i in range(1,3): #apply cool_setpoints or heat_setpoints first depending upon priority
                #         #warning: Don't change the order of the ifs. It will break things.
                #         if i==2:
                #             time.sleep(5)
                #         if i==cool_priority:
                #             if 'cool_setpoint' in newmodes:
                #                 _data['cool_setpoint'] = newmodes['cool_setpoint']
                #             _data['thermostat_mode'] = 'COOL'
                #             settings = {'thermostat_mode':'COOL','cool_setpoint':_data['cool_setpoint']\
                #                         ,'fan_mode':_data['fan_mode']}
                #             if 'hold' in _data:
                #                 settings['hold']=_data['hold']
                #             setDeviceStatusResult = self.Device.setDeviceStatus(settings)
                #
                #
                #         else:
                #             if 'heat_setpoint' in newmodes:
                #                 _data['heat_setpoint'] = newmodes['heat_setpoint']
                #             settings = {'thermostat_mode':'HEAT','heat_setpoint':_data['heat_setpoint']\
                #                         ,'fan_mode':_data['fan_mode']}
                #             if 'hold' in _data:
                #                 settings['hold']=_data['hold']
                #             setDeviceStatusResult = self.Device.setDeviceStatus(settings)
                #


                else:
                    setDeviceStatusResult = False
                #TODO need to do additional checking whether the device setting is actually success!!!!!!!!
            except Exception as er:
                print "Agent id: "+self.agent_id
                print "Error accessing device. Error:" + str(er)
                setDeviceStatusResult = False
            # step3: send reply message back to the UI
            topic = 'from/' + self.agent_id + '/update_response'
            # now = datetime.utcnow().isoformat(' ') + 'Z'
            headers = {
                'AgentID': self.agent_id,
                headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
                # headers_mod.DATE: now,
            }
            if setDeviceStatusResult:
                message = 'success'
            else:
                message = 'failure'
        else:
            print("The POST message is invalid, check thermostat_mode, heat_setpoint, cool_setpoint "
                  "setting and try again\n")
            message = 'failure'
            setDeviceStatusResult=False

        if setDeviceStatusResult:
            # self.updateDBall()
            self.updatePostgresDB()
        #insert the new data into cassandraDB
        self.TSDInsert(self.agent_id, UIdata, self.log_variables)
        self.bemoss_publish('update_response', return_entity, message)

    def isPostmsgValid(self, _data):  # check validity of postmsg
        dataValidity = True
        try:
            # _data = json.dumps(postmsg)
            if type(_data) in [str, unicode]:
                _data = json.loads(_data)
            for k, v in _data.items():
                if k == 'thermostat_mode':
                    #self.authorized_bemoss_mode = _data.get('thermostat_mode')
                    if _data.get('thermostat_mode') == "HEAT":
                        for k, v in _data.items():
                            if k == 'heat_setpoint':
                                self.authorized_heat_setpoint = _data.get('heat_setpoint')
                            elif k == 'cool_setpoint':
                                dataValidity = False
                                break
                            else:
                                pass
                    elif _data.get('thermostat_mode') == "COOL":
                        for k, v in _data.items():
                            if k == 'cool_setpoint':
                                self.authorized_cool_setpoint = _data.get('cool_setpoint')
                            elif k == 'heat_setpoint':
                                dataValidity = False
                                break
                            else:
                                pass
                elif k == 'fan_mode':
                    self.authorized_fan_mode = _data.get('fan_mode')
                else:
                    pass
        except:
            dataValidity = True
            print("dataValidity failed to validate data comes from UI")
        return dataValidity

    def updatePostgresDB(self):
        try:
            post_data = dict()
            for k in self.log_variables.keys():
                if k == 'offline_count' or k == 'user':
                    pass
                else:
                    post_data[k] = self.get_variable(k)

            self.updateDB(self.db_table_device, 'data', 'agent_id', json.dumps(post_data), self.agent_id)

            if self.variables['thermostat_mode'] != self.thermostat_mode:
                self.thermostat_mode = self.variables['thermostat_mode']
                dashboard_view = self.Device.dashboard_view()
                dashboard_view['bottom'] = self.thermostat_mode.lower()+'_setpoint'
                self.updateDB(self.db_table_device, 'dashboard_view', 'agent_id', json.dumps(dashboard_view), self.agent_id)

            print("{} updates the Postgresql during deviceMonitorBehavior successfully".format(self.agent_id))
        except Exception as er:
            print er
            print("ERROR: {} failed to update the Postgresql.".format(self.agent_id))

    def device_tampering_detection(self):
        allowance = 0
        self.unauthorized_settings = {}  # dict to store key value of unauthorized setting

        if (self.device_supports_schedule and self.get_variable('scheduleData') != self.authorized_scheduleData
            and self.authorized_scheduleData is not None and len(self.authorized_scheduleData) > 0):
            print "Schedule (mode) has been tampered"
            self._unauthorized_scheduleData = self.get_variable('scheduleData')
            self.unauthorized_settings['scheduleData'] = self.get_variable('scheduleData')
            self.set_variable('scheduleData', self.authorized_scheduleData)
            self.Device.setDeviceSchedule(self.authorized_scheduleData)
            return
        if self.get_variable('bemoss_mode').upper() in ['HEAT','COOL']:
            if self.get_variable('thermostat_mode')!= self.get_variable('bemoss_mode'):
                # collect this result for alarm notification & device control
                _unauthorized_bemoss_mode = self.get_variable('thermostat_mode')
                print_out = "Unauthorized thermostat mode changed to " + str(_unauthorized_bemoss_mode)
                print print_out
                self.set_variable('thermostat_mode', self.get_variable('bemoss_mode'))
                self.unauthorized_settings['thermostat_mode'] = self.get_variable('bemoss_mode')

        if self.get_variable('fan_mode') != self.authorized_fan_mode \
                and self.authorized_fan_mode is not None:
            # collect this result for alarm notification & device control
            _unauthorized_fan_mode = self.get_variable('fan_mode')
            print_out = "Unauthorized fan mode changed to " + str(_unauthorized_fan_mode)
            print print_out
            self.set_variable('fan_mode', self.authorized_fan_mode)
            self.unauthorized_settings['fan_mode'] = self.get_variable('fan_mode')

        if self.get_variable('heat_setpoint') != self.authorized_heat_setpoint \
                and self.authorized_heat_setpoint is not None:
            validChange = False

            #if the set-point change matches with the setpoint in the schedule, and we are close to the schedule change time, then this change is not treated as tampering
            if self.get_variable('hold') in [BEMOSS_ONTOLOGY.HOLD.POSSIBLE_VALUES.NONE, BEMOSS_ONTOLOGY.HOLD.POSSIBLE_VALUES.TEMPORARY]:
                #This means run on schedule, or schedule_override, or no hold function
                current_schedule_setpoints = self.getScheduleSetpoint(datetime.datetime.now())
                ahead_schedule_setpoints = self.getScheduleSetpoint(datetime.datetime.now()+datetime.timedelta(minutes=10))
                if self.get_variable('heat_setpoint') in  [current_schedule_setpoints[1], ahead_schedule_setpoints[1]]:
                    self.authorized_heat_setpoint = self.get_variable('heat_setpoint')
                    validChange = True

            if validChange == False:
                # collect this result for alarm notification & device control
                if self.get_variable('cool_setpoint'):
                    _unauthorized_change = self.get_variable('heat_setpoint') - self.authorized_heat_setpoint
                else:
                    _unauthorized_change = None
                temp_tolerance = 2
                if _unauthorized_change is None or (abs(_unauthorized_change) > temp_tolerance):
                    _unauthorized_heat_setpoint = self.get_variable('heat_setpoint')
                    print_out = "Unauthorized heat setpoint changed to " + str(_unauthorized_heat_setpoint)
                    print print_out

                    if _unauthorized_change is None:
                        allowance = 0
                    elif _unauthorized_change > 0:
                        allowance = 2
                    elif _unauthorized_change > 0:
                        allowance = -2

                    self.Device.variables['heat_setpoint'] = self.authorized_heat_setpoint + allowance
                    self.set_variable('heat_setpoint', self.authorized_heat_setpoint + allowance)

                    self.unauthorized_settings['heat_setpoint'] = _unauthorized_heat_setpoint
                else:
                    # Change within the range, allow the change.
                    pass

        if self.get_variable('cool_setpoint') != self.authorized_cool_setpoint \
                and self.authorized_cool_setpoint is not None:
            # collect this result for alarm notification & device control
            validChange = False

            #if the set-point change matches with the setpoint in the schedule, and we are close to the schedule change time, then this change is not treated as tampering
            if self.get_variable('hold') in [BEMOSS_ONTOLOGY.HOLD.POSSIBLE_VALUES.NONE, BEMOSS_ONTOLOGY.HOLD.POSSIBLE_VALUES.TEMPORARY]:
                #This means run on schedule
                current_schedule_setpoints = self.getScheduleSetpoint(datetime.datetime.now())
                ahead_schedule_setpoints = self.getScheduleSetpoint(datetime.datetime.now()+datetime.timedelta(minutes=10))
                if self.get_variable('cool_setpoint') in  [current_schedule_setpoints[0], ahead_schedule_setpoints[0]]:
                    self.authorized_cool_setpoint = self.get_variable('cool_setpoint')
                    validChange = True

            if validChange == False:
                temp_tolerance = 2
                if self.get_variable('cool_setpoint'):
                    _unauthorized_change = self.get_variable('cool_setpoint') - self.authorized_cool_setpoint
                else:
                    _unauthorized_change = None #assume None unauthorized change if there is no cool_setpoint defined
                if _unauthorized_change is None or abs(_unauthorized_change) > temp_tolerance:
                    _unauthorized_cool_setpoint = self.get_variable('cool_setpoint')
                    print_out = "Unauthorized cool setpoint changed to " + str(_unauthorized_cool_setpoint)
                    print print_out
                    if _unauthorized_change is None:
                        allowance = 0
                    elif _unauthorized_change > 0:
                        allowance = 2
                    elif _unauthorized_change > 0:
                        allowance = -2

                    self.Device.variables['cool_setpoint'] = self.authorized_cool_setpoint + allowance
                    self.set_variable('cool_setpoint', self.authorized_cool_setpoint + allowance)
                    self.unauthorized_settings['cool_setpoint'] = _unauthorized_cool_setpoint
                else:
                    pass

        if len(self.unauthorized_settings) != 0:


            _tampering_device_msg = ""
            _device_control_msg = {}
            for k, v in self.unauthorized_settings.items():
                if k == 'thermostat_mode':
                    _tampering_device_msg += 'set point: {}, authorized setting: {}, tampering setting: {}\n' \
                        .format(k, self.get_variable('bemoss_mode'), _unauthorized_bemoss_mode)
                    _device_control_msg[k] = self.get_variable('bemoss_mode')
                    if self.get_variable('bemoss_mode') == 'HEAT':
                        if self.authorized_heat_setpoint != None:
                            _device_control_msg['heat_setpoint'] = self.authorized_heat_setpoint + allowance
                    elif self.get_variable('bemoss_mode') == 'COOL':
                        if self.authorized_cool_setpoint != None:
                            _device_control_msg['cool_setpoint'] = self.authorized_cool_setpoint + allowance
                    else:
                        pass
                elif k == 'heat_setpoint':
                    _tampering_device_msg += 'tampered parameter: {}, authorized setting: {}, tampering setting: {}\n' \
                        .format(k, self.authorized_heat_setpoint, _unauthorized_heat_setpoint)
                    if 'thermostat_mode' not in self.unauthorized_settings:
                        _device_control_msg[k] = self.authorized_heat_setpoint + allowance
                elif k == 'cool_setpoint':
                    _tampering_device_msg += 'tampered parameter: {}, authorized setting: {}, tampering setting: {}\n' \
                        .format(k, self.authorized_cool_setpoint, _unauthorized_cool_setpoint)
                    if 'thermostat_mode' not in self.unauthorized_settings:
                        _device_control_msg[k] = self.authorized_cool_setpoint + allowance
                elif k == 'fan_mode':
                    _tampering_device_msg += 'tampered parameter: {}, authorized setting: {}, tampering setting: {}\n' \
                        .format(k, self.authorized_fan_mode, _unauthorized_fan_mode)
                    _device_control_msg[k] = self.authorized_fan_mode
                elif k == 'activeSchedule':
                    _tampering_device_msg += 'tampered parameter: {}, authorized setting: {}, tampering setting:\
                     {}\n'.format(k,self.authorized_scheduleData,self._unauthorized_scheduleData)
                else:
                    pass
            # TODO 1 set all settings back to previous state
            print "type(_device_control_msg)" + str(type(_device_control_msg))
            print "_device_control_msg " + str(_device_control_msg)
            self.Device.setDeviceStatus(json.loads(json.dumps(_device_control_msg)))
            self.variables['user']='anti-tampering'
            self.TSDInsert(self.agent_id,self.variables,self.log_variables)
            print "{} >> set points have been tampered but already set back to the authorized settings" \
                .format(self.agent_id)

        else:
            pass

    def getScheduleSetpoint(self,testDate):
        schData = self.get_variable('scheduleData')
        daysofweek=['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
        todayDay = daysofweek[testDate.weekday()]
        if todayDay != 'monday':
            yesterdayDay = daysofweek[testDate.weekday()-1]
        else:
            yesterdayDay = 'sunday'

        TodaysSchedule = schData[todayDay]
        YesterdaysSchedule = schData[yesterdayDay]
        setPoints = YesterdaysSchedule[-1][2:] #yesterday's last setpoint
        nowminute = testDate.hour*60+testDate.minute
        for entries in TodaysSchedule:
            if int(entries[1]) <= nowminute:
                setPoints = [int(entries[2]), int(entries[3])]
            else:
                break
        return setPoints




def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    try:
        utils.vip_main(ThermostatAgent)
    except Exception as e:
        _log.exception('unhandled exception')

if __name__ == '__main__':
    # Entry point for script
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
