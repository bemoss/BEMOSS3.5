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
        self.authorized_variables = dict()
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
        self.setpoint_tampering_allowance = 2


        try:
            self.curcon.execute("SELECT device_model FROM device_info WHERE agent_id=%s", (self.agent_id,))
            self.device_model = self.curcon.fetchone()[0]
        except Exception as er:
            print er
            print 'Failure @ get device model in init.'
        # if self.device_supports_schedule:
        #     try:
        #         self.Device.getDeviceSchedule()
        #     except:
        #         print('Failure @ thermostatagent init getDeviceSchedule.')

    # 2. agent setup method
    @Core.receiver('onsetup')
    def agent_setup(self, sender, **kwargs):
        super(ThermostatAgent, self).agent_setup(sender, **kwargs)
        # Do a one time push when we start up so we don't have to wait for the periodic
        # self.timer(1, self.deviceMonitorBehavior)
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
        if self.first_time_update:
            self.curcon.execute("SELECT data FROM " + self.db_table_device + " WHERE agent_id=%s", (self.agent_id,))
            if self.curcon.rowcount != 0:
                data = self.curcon.fetchone()[0]
                for k,v in data.items():
                    self.variables[k]=v
                    self.authorized_variables[k] = v


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
                    if self.Device.get_variable('scheduleData') is None or hour == 2 and self.get_sch_day != day:
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
        self.tampered_variables_correction = dict()  #key=tampered variable name, value = its tampered value ; only for tampered variables
        self.tampered_variables_values = dict()
        self.tampered_schedule = dict() #key='scheduleData' , value its tampered value; present only if schedule is tampered
        try:
            self.curcon.execute("SELECT data FROM " + self.db_table_device + " WHERE agent_id=%s", (self.agent_id,))
            if self.curcon.rowcount != 0:
                self.variables['anti_tampering'] = self.curcon.fetchone()[0]['anti_tampering']
            else:
                pass
        except Exception as er:
            print "Error accessing anti_tampering field", er

        #self.device_tampering_detection()
        #self.variables['scheduleData'] = self.Device.get_variable('scheduleData')# I added
        if self.device_supports_schedule:
            if self.get_variable('scheduleData') != self.Device.get_variable('scheduleData'):
                if self.variables['anti_tampering'] == 'DISABLED' or self.get_variable('scheduleData') is None :
                    self.variables['scheduleData'] = self.Device.get_variable('scheduleData')
                    try:
                        self.updateScheduleFromDevice()
                        print "Device schedule updated from Device", self.agent_id
                    except Exception as er:
                        print 'Schedule Update failed'
                        print er

                elif self.variables['anti_tampering'] == 'ENABLED': #schedule is tampered
                    print "Device Schedule Tampering detected."
                    self.tampered_schedule['scheduleData'] = self.variables['scheduleData']

        for v in self.log_variables:
            if v in self.Device.variables and self.Device.variables[v] is not None:
                if v not in self.variables or self.variables[v] != self.Device.variables[v]:
                    if v in ['cool_setpoint','heat_setpoint','thermostat_mode','fan_mode','hold']:
                        validChange = False
                        #if the cool_setpoint and heat_setpoint changed because of thermostat's schedule, then it is not tampering
                        if v in ['cool_setpoint','heat_setpoint']:
                            current_schedule_setpoints = self.getScheduleSetpoint(datetime.datetime.now())
                            ahead_schedule_setpoints = self.getScheduleSetpoint(datetime.datetime.now()+datetime.timedelta(minutes=10))
                            if self.Device.variables[v] in  [current_schedule_setpoints[v], ahead_schedule_setpoints[v]] and self.variables['hold'] in [BEMOSS_ONTOLOGY.HOLD.POSSIBLE_VALUES.NONE,BEMOSS_ONTOLOGY.HOLD.POSSIBLE_VALUES.TEMPORARY]:
                                validChange = True #the setpoint matches the schedule, so its valid
                                self.authorized_variables[v] = self.Device.variables[v]

                            elif v in self.authorized_variables:
                                diff = self.Device.variables[v] - self.authorized_variables[v]
                                if abs(diff) <= self.setpoint_tampering_allowance :
                                    validChange = True #the difference in setpoint is less than tolerance, so we accept it as valid change
                            else:
                                validChange = True
                                if self.get_variable(v) is None:
                                    self.authorized_variables[v] = self.Device.variables[v]
                                else:
                                    self.authorized_variables[v] = self.variables[v]
                        if v == 'hold':
                            if self.Device.variables[v] in [BEMOSS_ONTOLOGY.HOLD.POSSIBLE_VALUES.NONE,BEMOSS_ONTOLOGY.HOLD.POSSIBLE_VALUES.TEMPORARY] and\
                                    self.variables[v] in [BEMOSS_ONTOLOGY.HOLD.POSSIBLE_VALUES.NONE,BEMOSS_ONTOLOGY.HOLD.POSSIBLE_VALUES.TEMPORARY]:
                                #changes from NONE to TEMPORARY or vice versa is accepted. It cannot happen without change of set-point.
                                validChange = True

                        if v in self.variables and self.variables[v] is not None and self.variables['anti_tampering']=="ENABLED" and not validChange:
                            #tampering case
                            if v in ['cool_setpoint', 'heat_setpoint']:
                                sign = 1 if self.Device.variables[v] > self.variables[v] else -1
                                self.variables[v] = self.authorized_variables[v] + self.setpoint_tampering_allowance*sign
                                self.tampered_variables_values[v] = self.Device.variables[v]
                                self.tampered_variables_correction[v] = self.variables[v]
                                self.changed_variables[v] = self.log_variables[v]
                            else:
                                self.tampered_variables_values[v] = self.Device.variables[v]
                                self.tampered_variables_correction[v] = self.variables[v]
                        else:
                            self.variables[v] = self.Device.variables[v]
                            if self.variables['anti_tampering']=="DISABLED":
                                self.authorized_variables[v] = self.variables[v]
                            self.changed_variables[v] = self.log_variables[v]
                    else:
                        self.variables[v] = self.Device.variables[v]
            else:
                if v not in self.variables:  # it won't be in self.variables either (in the first time)
                    self.changed_variables[v] = self.log_variables[v]
                    self.variables[v] = None
        
        if 'scheduleData' in self.tampered_schedule:
            self.Device.setDeviceSchedule(self.variables['scheduleData']) #original value is at self.variables
        
        if self.tampered_variables_correction:
            self.Device.setDeviceStatus(self.tampered_variables_correction)
            # self.tampered_variables_values['user'] = 'Tamperer'
            # #self.TSDInsert(self.agent_id,self.tampered_variables_values,self.log_variables) #record the tampering in DB
            # self.tampered_variables_values.pop('user')
            message = []
            for k,v in self.tampered_variables_values.items():
                message += [k + " to " + str(v)]
            message = 'Tampered ' + ' and '.join(message)
            self.curcon.execute("select nickname from device_info where agent_id=%s",(self.agent_id,))
            nickname = self.curcon.fetchone()[0]
            self.EventRegister('device-tampering',reason=message,source=nickname)

        if self.first_time_update:
            self.curcon.execute("SELECT data FROM " + self.db_table_device + " WHERE agent_id=%s", (self.agent_id,))
            if self.curcon.rowcount != 0:
                data = self.curcon.fetchone()[0]
                if self.get_variable('heat_setpoint') is None and 'heat_setpoint' in data:
                    self.variables['heat_setpoint'] = data['heat_setpoint']
                else:
                    self.variables['heat_setpoint'] = 72 # default when device is in cool mode, no heat_setpoint provided
                
                if self.get_variable('cool_setpoint') is None and 'cool_setpoint' in data:
                    self.variables['cool_setpoint'] = data['cool_setpoint']
                else:
                    self.variables['cool_setpoint'] = 72 # default when device is in cool mode, no cool_setpoint provided

                self.first_time_update = False
                self.changed_variables = self.log_variables  # log everything the first time


        self.onlineOfflineDetection()
        _time_stamp_last_scanned = str(datetime.datetime.now())
        self.curcon.execute("UPDATE "+self.db_table_device+" SET last_scanned_time=%s "
                         "WHERE agent_id=%s",
                         (_time_stamp_last_scanned, self.agent_id))
        self.curcon.commit()

        if len(self.changed_variables) == 0:
            print 'nothing changed'
            return
        else:
            print 'These things changed:'
            for key in self.changed_variables.keys():
                print key +':'+str(self.variables[key])

        self.updateUI()

        # update PostgresQL (meta-data) database
        self.updatePostgresDB()

        # update cassandra database
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
        try:
            # _data = json.dumps(message[0])
            _data = message
            UIdata = dict(_data)
            if 'user' in _data:
                self.variables['user'] = _data.pop('user')
            else:
                self.variables['user'] = 'unknown-UI'
                UIdata['user'] = 'unknown-UI'

            for k, v in _data.items():
                if k in ['thermostat_mode','heat_setpoint','cool_setpoint','fan_mode','anti_tampering','hold']:
                    self.variables[k] = v
                    self.authorized_variables[k] = v

            try:
                setDeviceStatusResult = self.Device.setDeviceStatus(_data)  # convert received message from string to JSON
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
        except Exception as er:
            print("Some Error while controlling device " + str(er))
            message = 'failure'
            setDeviceStatusResult=False

        if setDeviceStatusResult:
            # self.updateDBall()
            self.updatePostgresDB()
        #insert the new data into cassandraDB
        self.TSDInsert(self.agent_id, UIdata, self.log_variables)
        self.bemoss_publish('update_response', return_entity, message)


    def updatePostgresDB(self):
        try:
            post_data = dict()


            for k in self.log_variables.keys()+['scheduleData']:
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
        setPoints = {'cool_setpoint':YesterdaysSchedule[-1][2],'heat_setpoint':YesterdaysSchedule[-1][3]} #yesterday's last setpoint
        nowminute = testDate.hour*60+testDate.minute
        for entries in TodaysSchedule:
            if int(entries[1]) <= nowminute:
                setPoints = {'cool_setpoint':int(entries[2]), 'heat_setpoint':int(entries[3])}
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
