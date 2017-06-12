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

# settings file for BEMOSS project.

import os

print "OS settings imported"
DEBUG = True
TEMPLATE_DEBUG = DEBUG
TIME_ZONE = 'America/New_York'

ADMINS = ()

PROJECT_DIR = os.path.dirname(__file__)
Agents_DIR = os.path.join(PROJECT_DIR, 'Agents/')
Agents_Launch_DIR = os.path.join(PROJECT_DIR, 'Agents/LaunchFiles/')
Applications_DIR = os.path.join(PROJECT_DIR, 'Applications/')
Applications_Launch_DIR = os.path.join(PROJECT_DIR, 'Applications/launch/')
Loaded_Agents_DIR = os.path.expanduser("~/.volttron/agents/")
Autostart_Agents_DIR = os.path.expanduser("~/.config/volttron/lite/autostart/")
Communications_DIR = os.path.join(PROJECT_DIR, 'bemoss_lib/communication/')
Custom_eggs_DIR = os.path.join(PROJECT_DIR, 'bemoss_lib/custom-eggs/')
Schedule_DIR = os.path.join(PROJECT_DIR, 'Web_Server/resources/scheduler_data/')

MANAGERS = ADMINS

PLATFORM = {
    'node': {
        'name': 'BEMOSS core',
        'type': 'core',
        'model': 'Odroid3',
        'building_name': 'bemoss',
        'node_monitor_time': 60,
        'node_offline_timeout': 0,
        'main_core': 'BEMOSS core',
        'zone':999
    }
}

DEVICES = {
    'device_monitor_time': 60,'max_monitor_time':1800
}

SYSTEM_AGENTS = ['networkagent','platformmonitoragent','multinodeagent','devicediscoveryagent'] #
PARENT_NODE_SYSTEM_AGENTS = ['ui','vipagent'] #message to this agents only be sent to core
NO_FORWARD_AGENTS = ['tsdagent'] #messages to this agent will not be forwarded
MULTINODE_PARENT_IP_FILE = PROJECT_DIR + '/parent_ip.txt'
MULTINODE_DATA_PATH = '/multinode_data.json'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'bemossdb',                      # Or path to database file if using sqlite3.
        'USER': 'admin',                      # Not used with sqlite3.
        'PASSWORD': 'admin',                  # Not used with sqlite3.
        'HOST': 'localhost',
        'PORT': '5432',                    # Set to empty string for default. Not used with sqlite3.
        'TABLE_dashboard_device_info': 'dashboard_device_info',
        'TABLE_dashboard_current_status': 'dashboard_current_status',
        'TABLE_building_zone': 'building_zone',
        'TABLE_global_zone_setting': 'global_zone_setting',
        'TABLE_device_info': 'device_info',
        'TABLE_device_model': 'device_model',
        'TABLE_dashboard_building_zones': 'building_zone',
        'TABLE_holiday': 'holiday',
        'TABLE_application_running': 'application_running',
        'TABLE_application_registered': 'application_registered',
        'TABLE_device': 'devicedata',
        'TABLE_supported_devices': 'supported_devices',
        'TABLE_node_info': 'node_info',
        'TABLE_node_device': 'node_device',
        'TABLE_bemoss_notify': 'notification',
        'TABLE_active_alert': 'alerts',
        'TABLE_device_type': 'device_type',
        'TABLE_alerts_notificationchanneladdress': 'alerts_notificationchanneladdress',
        'TABLE_temp_time_counter': 'temp_time_counter',
        'TABLE_temp_failure_time': 'temp_failure_time',
        'TABLE_priority': 'priority',
        'TABLE_seen_notifications_counter': 'seen_notifications_counter'
    }
}

NOTIFICATION = {
    'heartbeat': 24*60,  # heartbeat period to resend a message
    'heartbeat_device_tampering': 130,  # heartbeat period to resend a message
    'email': {
        'fromaddr': 'Your Email',
        'recipients': [],
        'username': 'Your Email',
        'password': 'Your Email password',
        'subject' : 'Message from',
        'mailServer': 'smtp.gmail.com:587'
    },
    'plugload':{
        'status': "ON",
        'power': 200
    },
    'thermostat':{
        'too_hot': 90,
        'too_cold': 60
    },
    'lighting':{
        'too_dark': 10  # % of brightness
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'b4nr@$=^2)_g!_vz-nm_1$_!!jfh&2yn$6#a9klqyh28g*vjl%'

# Alexa Authentication PIN:
ALEXA_KEY = '93712'

#Weather Underground Key
WUNDERGROUND_KEY = 'underground-key'

#Default Zipcode
zip_code = 22203

#don't change this
weather_agent = 'BEMO_WUG' + str(zip_code)

FIND_DEVICE_SETTINGS = {
    'findWiFi': True,
    'findWiFiNest': True,
    'findWiFiParticle': True,
    'findWiFiHue': True,
    'findWiFiWeMo': True,
    'findWiFiXW110': True,
    'findBACnet': True,
    'findModbus': True,
    'findAcquiSuite': False,
    'findWiFiNetatmo': True,
    'findSmartThings': False,
    'findProteus': False,
    'findWiFiICM': True,
    'findWiFiHoneywell': True,
    'findZigBee': True
	
}

DUMMY_SETTINGS = {
    'dummy_discovery': False,
    'number_of_hvac': 30,
    'number_of_lighting': 0,
    'number_of_plugload': 0,
    'number_of_sensor': 0,
    'number_of_powermeter': 0
}
