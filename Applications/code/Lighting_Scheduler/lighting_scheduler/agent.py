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

#__author__ =  "BEMOSS Team"
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
from volttron.platform.vip.agent import Agent, Core
from volttron.platform.agent import utils
from volttron.platform.messaging import headers as headers_mod
from bemoss_lib.utils import db_helper
import time
import datetime
import settings
import re

utils.setup_logging()
_log = logging.getLogger(__name__)


class SchedulerAgent(Agent):

    def __init__(self, config_path, **kwargs):

        super(SchedulerAgent, self).__init__(**kwargs)
        self.variables = kwargs
        config = utils.load_config(config_path)
        def get_config(name):
            try:
                kwargs.pop(name)
            except KeyError:
                return config.get(name, '')
        self.app_name = "lighting_scheduler"
        self.building_name = settings.PLATFORM['node']['building_name']
        # 2. @params agent
        self.agent_id = get_config('agent_id')
        self.clock_time = 60  # schedule is updated every minute
        self.debug_agent = False
        self.timeStatusBrightnessColor = kwargs
        self.timeStatusBrightnessColor.clear()
        self.flag_time_to_change_status = False
        self.current_use_schedule = None
        self.schedule_first_run = False
        self.weekday_list = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
        self.weekend_list = ['saturday', 'sunday']
        self.old_day = self.find_day()
        self.active_scheduler_mode = list()
        self.time_next_schedule_sec = int(24 * 3600)
        self.current_schedule_object = None

        self.curcon = db_helper.db_connection()

        try:
            app_agent_id = self.agent_id
            self.curcon.execute("select app_data from application_running where app_agent_id=%s", (self.agent_id,))
            if self.curcon.rowcount:
                self.app_data = self.curcon.fetchone()[0]
                self.device_agent_id = self.app_data['device_agent_id']
                self.topic_ui_app = 'to/' + self.agent_id + '/update/from/ui'
                self.topic_app_ui = 'to/ui/update/from/' + self.agent_id
            else:
                raise ValueError("No entry in application running for this scheduler")

            self.curcon.execute("SELECT schedule FROM schedule_data WHERE agent_id=%s", (self.device_agent_id,))
            if self.curcon.rowcount != 0:
                _new_schedule_object = self.curcon.fetchone()[0]
                self.current_schedule_object = _new_schedule_object['lighting']
                # 3. get currently active schedule
                self.active_scheduler_mode = list()
                print '{} for Agent: {} >> new active schedule are as follows:'.format(self.app_name, self.device_agent_id)
                for each1 in self.current_schedule_object[self.device_agent_id]:
                    if each1 == 'active':
                        for each2 in self.current_schedule_object[self.device_agent_id][each1]:
                            self.active_scheduler_mode.append(each2)

                for index in range(len(self.active_scheduler_mode)):
                    print "- " + self.active_scheduler_mode[index]

                # 4. RESTART Scheduler Agent **************** IMPORTANT
                self.set_query_mode_all_day()
                self.schedule_first_run = True
                # ******************************************* IMPORTANT
                print("{} for Agent: {} >> DONE getting data from applications_running".format(self.app_name, self.device_agent_id))
            else:
                print("{} for Agent: {} >> has no previous setting before".format(self.app_name, self.device_agent_id))



        except:
            print("{} for Agent: {} >> error getting data from applications_running"
                  .format(self.app_name, self.device_agent_id))

    #2. agent setup method
    @Core.receiver('onsetup')
    def setup(self, sender, **kwargs):
        self.core.periodic(self.clock_time, self.clockBehavior)
        self.vip.pubsub.subscribe(peer='pubsub', prefix=self.topic_ui_app, callback=self.updateScheduleBehavior)


    def clockBehavior(self):
        #1. check current time
        self.htime = datetime.datetime.now().hour
        self.mtime = datetime.datetime.now().minute
        self.stime = datetime.datetime.now().second
        self.now_decimal = int(self.htime)*60 + int(self.mtime)
        self.time_now_sec = int(self.htime*3600) + int(self.mtime)*60 + int(self.stime)

        #2. update self.schedule_first_run to True if day has change
        self.new_day = self.find_day()
        if self.new_day != self.old_day:
            if self.current_schedule_object != None:
                #RESTART Scheduler Agent ******************* IMPORTANT
                self.set_query_mode_all_day()
                self.schedule_first_run = True
                self.old_day = self.new_day
                #******************************************* IMPORTANT
                print '{} for Agent: {} >> today: {} is  a new day (yesterday: {}), load new schedule for today'\
                    .format(self.app_name, self.device_agent_id, self.new_day, self.old_day)
            else:
                print '{} for Agent: {} >> today: {} is  a new day (yesterday: {}), but no schedule has been set yet'\
                    .format(self.app_name, self.device_agent_id, self.new_day, self.old_day)
        else: #same day no reset is required
            pass

        #3. self.schedule_first_run to True is triggered by 1. setting from UI or 2. Day change
        if self.schedule_first_run is True:
            self.schedule_action()
            self.schedule_first_run = False
        else:
            pass

        #4. if next schedule comes up, run self.schedule_action()
        if self.time_now_sec >= self.time_next_schedule_sec:
            if self.debug_agent: print "{} for Agent: >> {} now _time_now_sec= {}, self.time_next_schedule_sec ={}"\
                .format(self.app_name, self.device_agent_id, self.time_now_sec, self.time_next_schedule_sec)
            print "{} for Agent: {} >> is now woken up".format(self.app_name, self.device_agent_id)
            self.schedule_action()


    def updateScheduleBehavior(self,peer, sender, bus, topic,headers,message):
        _time_receive_update_from_ui = datetime.datetime.now()
        print "{} for Agent: {} >> got new update from UI at {}".format(self.app_name, self.device_agent_id,
                                                                        _time_receive_update_from_ui)
        #1. get path to the new launch file from the message sent by UI
        try:
            _data = json.loads(message)
            app_agent_id = self.agent_id
            print "app_agent_id = {}".format(app_agent_id)
            self.curcon.execute("SELECT schedule FROM schedule_data WHERE agent_id=%s", (self.device_agent_id,))
            if self.curcon.rowcount != 0:
                _new_schedule_object = self.curcon.fetchone()[0]
                self.current_schedule_object = _new_schedule_object['lighting']

            #3. get currently active schedule
            self.active_scheduler_mode = list()
            print '{} for Agent: {} >> new active schedule are as follows:'.format(self.app_name, self.device_agent_id)
            for each1 in self.current_schedule_object[self.device_agent_id]:
                if each1 == 'active':
                    for each2 in self.current_schedule_object[self.device_agent_id][each1]:
                        self.active_scheduler_mode.append(each2)

            for index in range(len(self.active_scheduler_mode)):
                print "- " + self.active_scheduler_mode[index]

            #4. RESTART Scheduler Agent **************** IMPORTANT
            self.set_query_mode_all_day()
            self.schedule_first_run = True
            #******************************************* IMPORTANT

            #reply message from app to ui
            _headers = {
                'AppName': self.app_name,
                'AgentID': self.device_agent_id,
                headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.JSON,
                headers_mod.FROM: self.device_agent_id,
                headers_mod.TO: 'ui'
            }
            _message = 'success'
            self.vip.pubsub.publish('pubsub', self.topic_app_ui, _headers, _message)
            print '{} for Agent: {} >> DONE update new active schedule received from UI'\
                .format(self.app_name, self.device_agent_id)
        except:
            print "{} for Agent: {} >> ERROR update new schedule received from UI at {}"\
                .format(self.app_name, self.device_agent_id, _time_receive_update_from_ui)
            print "{} for Agent: {} >> possible ERRORS are as follows: "\
                .format(self.app_name, self.device_agent_id, _time_receive_update_from_ui)
            print "{} for Agent: {} >> ERROR 1 : path to update schedule sent by UI is incorrect "\
                .format(self.app_name, self.device_agent_id, _time_receive_update_from_ui)
            print "{} for Agent: {} >> ERROR 2 : content inside schedule setting file (JSON) sent by UI" \
                  " is incorrect ".format(self.app_name, self.device_agent_id, _time_receive_update_from_ui)

    #Helper methods --------------------------------------
    def set_query_mode_all_day(self):
        if 'holiday' in self.active_scheduler_mode:
            #1. find whether today is a holiday by query db 'public.holiday'
            _date_today = str(datetime.datetime.now().date())
            self.curcon.execute("SELECT description FROM holiday WHERE date=%s", (_date_today,))
            if self.curcon.rowcount != 0:
                self.holiday_description = self.curcon.fetchone()[0]
                print '---------------------------------'
                print "{} for Agent: {} >> Hoorey! today is a holiday: {}"\
                    .format(self.app_name, self.device_agent_id, self.holiday_description)
                self.todayHoliday = True
            else:
                print '---------------------------------'
                print "{} for Agent: {} >> Today is not a holiday".format(self.app_name, self.device_agent_id)
                self.todayHoliday = False

            #2. select schedule according to the day
            if self.todayHoliday is True:
                self.today = self.find_day()
                print "{} for Agent: {} >> mode: holiday".format(self.app_name, self.device_agent_id)
                self.query_schedule_mode = 'holiday'
                self.query_schedule_point = 'holiday'
                self.get_schedule_time_status_brightness_color()
            else:
                self.set_query_mode_point_everyday_weekdayweekend()
                self.get_schedule_time_status_brightness_color()
        else:  # no holiday mode
            self.todayHoliday = False
            self.set_query_mode_point_everyday_weekdayweekend()
            self.get_schedule_time_status_brightness_color()

    def set_query_mode_point_everyday_weekdayweekend(self):
        # find the day of today then print the setting of the Scheduler Agent
        self.today = self.find_day()
        if 'everyday' in self.active_scheduler_mode:
            print '---------------------------------'
            print "{} for Agent: {} >> mode: everyday".format(self.app_name, self.device_agent_id)
            self.query_schedule_mode = 'everyday'
            self.query_schedule_point = self.today
        elif 'weekdayweekend' in self.active_scheduler_mode:
            print '---------------------------------'
            print '{} for Agent: {} >> mode: weekdayweekend'.format(self.app_name, self.device_agent_id)
            self.query_schedule_mode = 'weekdayweekend'
            # find whether today is a weekday or weekend
            if self.today in self.weekday_list:
                self.query_schedule_point = 'weekday'
            elif self.today in self.weekend_list:
                self.query_schedule_point = 'weekend'
            else:  #TODO change this default setting
                self.query_schedule_point = 'weekday'

    def get_schedule_time_status_brightness_color(self):
        #1. get time-related schedule including: 1.status 2.brightness 3.color
        self.newTimeScheduleChange = list()
        for eachtime in self.current_schedule_object[self.device_agent_id]['schedulers'][self.query_schedule_mode][self.query_schedule_point]:
            #time that scheduler need to change a light setting
            self.newTimeScheduleChange.append(int(eachtime['at']))
            #dictionary relate time with 1.status 2.brightness 3.color
            try:
                if eachtime['status'] is not None:
                    _status_to_store = str(eachtime['status'])
                else:
                    _status_to_store = "None"
            except:
                _status_to_store = "None"
            try:
                if eachtime['brightness'] is not None:
                    _brightness_to_store = str(eachtime['brightness'])
                else:
                    _brightness_to_store = "None"
            except:
                _brightness_to_store = "None"
            try:
                if eachtime['color'] is not None:
                    _color_to_store = str(eachtime['color'])
                else:
                    _color_to_store = "None"
            except:
                _color_to_store = "None"

            self.timeStatusBrightnessColor[str(eachtime['at'])] = str(_status_to_store + "|"
                                                                      + _brightness_to_store + "|"
                                                                      + _color_to_store)
            #TODO save historical setting of each mode 'holiday', 'weekdayweekend' or 'everyday' to Agent Knowledge

        #2. sort time to change the schedule in ascending order
        self.newTimeScheduleChange.sort()

        #3. get the schedule: reordered time and corresponding mode and temperature setting
        if self.todayHoliday is True:
            print "{} for Agent: {} >> Today is {} and here is the schedule for holiday:"\
                .format(self.app_name, self.device_agent_id, self.holiday_description)
        else:
            if self.query_schedule_mode is 'everyday':
                print "{} for Agent: {} >> Today is {} and here is the schedule for today:"\
                    .format(self.app_name, self.device_agent_id, self.today)
            elif self.query_schedule_point is 'weekday':
                print "{} for Agent: {} >> Today is {} and here is the schedule for the weekday:"\
                    .format(self.app_name, self.device_agent_id, self.today)
            elif self.query_schedule_point is 'weekend':
                print "{} for Agent: {} >> Today is {} and here is the schedule for the weekend:"\
                    .format(self.app_name, self.device_agent_id, self.today)
        for index in range(len(self.newTimeScheduleChange)):
            _time = self.newTimeScheduleChange[index]
            _hour = int(_time/60)
            _minute = int(_time - (_hour*60))
            _status_brightness_color = str(self.timeStatusBrightnessColor[str(self.newTimeScheduleChange[index])]).split('|')
            _status = _status_brightness_color[0]
            _brightness = _status_brightness_color[1]
            _color = _status_brightness_color[2]
            print "{} for Agent: {} >> At {} hr {} min status: {}, brightness: {}, color: {}"\
                .format(self.app_name, self.device_agent_id, str(_hour), str(_minute), str(_status), str(_brightness), str(_color))
        print ''

    def schedule_action(self):
        '''before call this method make sure that self.timeStatusBrightnessColor
        and self.newTimeScheduleChange has been updated!'''
        print '{} for Agent: {} >> current time {} hr {} min {} sec (decimal = {})'\
            .format(self.app_name, self.device_agent_id, self.htime, self.mtime, self.stime, str(self.now_decimal))

        # 1.2 check current and past schedule
        _pastSchedule = list()  # list to save times of previous schedules
        for index in range(len(self.newTimeScheduleChange)):
            if self.now_decimal >= self.newTimeScheduleChange[index]:
                _pastSchedule.append(self.newTimeScheduleChange[index])

        # if length of _pastSchedule is not 0, there is a previous schedule(s)
        if len(_pastSchedule) != 0:
            # previous schedule exists, use previous schedule to update thermostat to latest setting
            _latest_schedule = max(_pastSchedule)
            self.current_use_schedule = _latest_schedule
            _time_current_schedule = int(self.current_use_schedule)
            self.hour_current_schedule = int(_time_current_schedule/60)
            self.minute_current_schedule = int(_time_current_schedule - self.hour_current_schedule*60)
            self.status_brightness_color_current = str(self.timeStatusBrightnessColor[str(self.current_use_schedule)]).split('|')
            self.statusToChange_current = self.status_brightness_color_current[0]
            self.brightnessToChange_current = self.status_brightness_color_current[1]
            self.colorToChange_current = self.status_brightness_color_current[2]
            self.flag_time_to_change_status = True
            print "{} for Agent: {} >> Here is the new schedule: at {} hr {} min status: {}, " \
                  "brightness: {}, color: {}".format(self.app_name, self.device_agent_id, self.hour_current_schedule,
                                                     self.minute_current_schedule, str(self.statusToChange_current)
                                                     .upper(), str(self.brightnessToChange_current),
                                                     str(self.colorToChange_current))

        else:  # previous schedule does not exist
            # scheduler is trying to get setting from the old setting file
            if self.current_use_schedule is not None:  # previous schedule from old setting file exists
                _time_current_schedule = int(self.current_use_schedule)
                self.hour_current_schedule = int(_time_current_schedule/60)
                self.minute_current_schedule = int(_time_current_schedule - self.hour_current_schedule*60)
                self.status_brightness_color_current = str(self.timeStatusBrightnessColor[str(self.current_use_schedule)]).split('|')
                self.statusToChange_current = self.status_brightness_color_current[0]
                self.brightnessToChange_current = self.status_brightness_color_current[1]
                self.colorToChange_current = self.status_brightness_color_current[2]
                self.flag_time_to_change_status = True

                print "{} for Agent: {} >> previous schedule is at {} hr {} min status: {}, brightness: {}," \
                      " color: {}".format(self.app_name, self.device_agent_id, str(self.hour_current_schedule),
                                          str(self.minute_current_schedule), str(self.statusToChange_current).upper()
                                          , str(self.brightnessToChange_current), str(self.colorToChange_current))

            else:  # previous schedule from old setting file does not exist
                print "{} for Agent: {} >> There is no previous schedule from old setting file".format(self.app_name,
                                                                                                       self.device_agent_id)
                print '{} for Agent: {} >> Let''s check for the next schedule'.format(self.app_name, self.device_agent_id)

        #2.  take action based on current time
        # 2.1 case 1: time to change schedule is triggered
        if self.flag_time_to_change_status is True:
            if self.debug_agent: print "{} for Agent: {} >> is changing the lighting status, brightness, and color"\
                .format(self.app_name, self.device_agent_id)
            try:
                _headers = {
                    headers_mod.FROM: self.device_agent_id,
                    headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.JSON,
                }
                # case1: only 'status' is changed
                self.curcon.execute("SELECT current_node_id FROM node_device WHERE agent_id=%s",
                                 (self.device_agent_id,))
                if self.curcon.rowcount != 0:
                    zone_id = str(self.curcon.fetchone()[0])
                else:
                    zone_id = 999  # default core id TODO this has to be changed
                _topic_Agent_UI_tail = self.building_name + '/' + str(zone_id) + '/' + self.device_agent_id
                topic_app_agent = 'to/' + self.device_agent_id + '/update/from/lightingscheduler'

                if str(self.brightnessToChange_current) == "None" and str(self.colorToChange_current) == "None":
                    if str(self.statusToChange_current) != "None": #send only status
                        _status_to_publish = str(self.statusToChange_current).upper()
                        _content = {"status": _status_to_publish}
                        print "{} for Agent: {} >> published message to IEB with status: {}"\
                            .format(self.app_name, self.device_agent_id, _status_to_publish)
                        self.vip.pubsub.publish('pubsub', topic_app_agent, _headers, json.dumps(_content))
                    else: # nothing to publish
                        pass
                # case2: 'status' with 'brightness' or 'color' are changed
                elif str(self.brightnessToChange_current) == "None" or str(self.colorToChange_current) == "None":
                    if str(self.statusToChange_current) != "None" and str(self.brightnessToChange_current) != "None":
                        _status_to_publish = str(self.statusToChange_current).upper()
                        _brightness_to_publish = int(self.brightnessToChange_current)
                        _content = {"status": _status_to_publish, "brightness": _brightness_to_publish}
                        print "{} for Agent: {} >> published message to IEB with status: {}, brightness: {}"\
                            .format(self.app_name, self.device_agent_id, _status_to_publish, _brightness_to_publish)
                        self.vip.pubsub.publish('pubsub', topic_app_agent, _headers, _content)
                    elif str(self.statusToChange_current) != "None" and str(self.colorToChange_current) != "None":
                        _status_to_publish = str(self.statusToChange_current).upper()
                        _color_temp1 = str(self.colorToChange_current)
                        _color_temp2 = tuple(int(v) for v in re.findall("[0-9]+", _color_temp1))
                        _color_to_publish = _color_temp2
                        _content = {"status": _status_to_publish, "color": _color_to_publish}
                        print "{} for Agent: {} >> published message to IEB with status: {}, color: {}"\
                            .format(self.app_name, self.device_agent_id, _status_to_publish, _color_to_publish)
                        self.vip.pubsub.publish('pubsub', topic_app_agent, _headers, _content)
                    else:  # nothing to publish
                        pass
                # case3: 'status' with 'brightness' with 'color' are changed
                else:
                    _status_to_publish = str(self.statusToChange_current).upper()
                    _brightness_to_publish = int(self.brightnessToChange_current)
                    _color_temp1 = str(self.colorToChange_current)
                    _color_temp2 = tuple(int(v) for v in re.findall("[0-9]+", _color_temp1))
                    _color_to_publish = _color_temp2
                    _content = {"status": _status_to_publish, "color": _color_to_publish, "brightness": _brightness_to_publish}
                    print "{} for Agent: {} >> published message to IEB with status: {}, brightness: {}, color: {}"\
                        .format(self.app_name, self.device_agent_id, _status_to_publish, _brightness_to_publish, _color_to_publish)
                    self.vip.pubsub.publish('pubsub', topic_app_agent, _headers, json.dumps(_content))

                self.flag_time_to_change_status = False
            except:
                print "{} for Agent: {} >> ERROR changing status of a light"\
                    .format(self.app_name, self.device_agent_id)
        # 2.2 case2: time to change schedule is not triggered
        else:
            pass
            # print("Scheduler Agent takes no action")

        #3. check next schedule
        # 3.1 check whether there is a next schedule
        _nextSchedule = list()
        for index in range(len(self.newTimeScheduleChange)):
            if self.now_decimal < self.newTimeScheduleChange[index]:
                _nextSchedule.append(self.newTimeScheduleChange[index])

        if len(_nextSchedule) != 0:
            _time_next_schedule = int(min(_nextSchedule))
            self.hour_next_schedule = int(_time_next_schedule/60)
            self.minute_next_schedule = int(_time_next_schedule - (self.hour_next_schedule*60))
            self.status_brightness_color_next = str(self.timeStatusBrightnessColor[str(min(_nextSchedule))]).split('|')
            self.statusToChange_next = self.status_brightness_color_next[0]
            self.brightnessToChange_next = self.status_brightness_color_next[1]
            self.colorToChange_next = self.status_brightness_color_next[2]
            print "{} for Agent: {} >> Here is the next schedule: at {} hr {} min status: {}, brightness: {}, color: {}".\
                    format(self.app_name, self.device_agent_id, self.hour_next_schedule, self.minute_next_schedule,
                           str(self.statusToChange_next).upper(), self.brightnessToChange_next, self.colorToChange_next)
            self.time_next_schedule_sec = int(_time_next_schedule*60)
            _time_to_wait = self.time_next_schedule_sec - self.time_now_sec
            if _time_to_wait >= 3600:
                _hr_to_wait = int(_time_to_wait/3600)
                _min_to_wait = int((_time_to_wait - (_hr_to_wait*3600))/60)
                _sec_to_wait = int(_time_to_wait - (_hr_to_wait*3600) - (_min_to_wait*60))
            elif _time_to_wait > 60:
                _hr_to_wait = 0
                _min_to_wait = int(_time_to_wait/60)
                _sec_to_wait = int(_time_to_wait - (_min_to_wait*60))
            else:
                _hr_to_wait = 0
                _min_to_wait = 0
                _sec_to_wait = _time_to_wait
            print "{} for Agent: {} >> is going to sleep now until next schedule come up in {} hr {} min {} sec"\
                .format(self.app_name, self.device_agent_id, _hr_to_wait, _min_to_wait, _sec_to_wait)
        else:
            print "{} for Agent: {} >> There is no next schedule".format(self.app_name, self.device_agent_id)
            self.time_next_schedule_sec = int(24*3600)
        print '---------------------------------'

    def find_day(self):
        localtime = time.localtime(time.time())
        dow = self.weekday_list + self.weekend_list
        return dow[localtime.tm_wday]

    def set_variable(self, k, v):  # k=key, v=value
        self.variables[k] = v

    def get_variable(self, k):
        return self.variables.get(k, None)  # default of get_variable is none


def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    try:
        utils.vip_main(SchedulerAgent)
    except Exception as e:
        _log.exception('unhandled exception')

if __name__ == '__main__':
    # Entry point for script
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
