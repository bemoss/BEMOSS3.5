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
#__created__ = "2017-09-12 12:04:50"
#__lastUpdated__ = "2016-03-14 11:23:33"
'''

import os
import sys
import json
import importlib
import settings
os.chdir(os.path.expanduser( settings.PROJECT_DIR + "/"))
#os.system("service postgresql restart")
current_working_directory = os.getcwd()
sys.path.append(current_working_directory)
import psycopg2
import datetime
import netifaces as ni
import socket
import struct
import fcntl
import shutil
# CONFIGURATION ---------------------------------------------------------------------------------------------
#@params agent
agent_id = 'PlatformInitiator'

# @params DB interfaces
db_database = settings.DATABASES['default']['NAME']
db_host = settings.DATABASES['default']['HOST']
db_port = settings.DATABASES['default']['PORT']
db_user = settings.DATABASES['default']['USER']
db_password = settings.DATABASES['default']['PASSWORD']
db_table_building_zone = settings.DATABASES['default']['TABLE_building_zone']
db_table_global_zone_setting = settings.DATABASES['default']['TABLE_global_zone_setting']
db_table_holiday = settings.DATABASES['default']['TABLE_holiday']
db_table_device_info = settings.DATABASES['default']['TABLE_device_info']
db_table_device_model = settings.DATABASES['default']['TABLE_device_model']
db_table_application_running = settings.DATABASES['default']['TABLE_application_running']
db_table_application_registered = settings.DATABASES['default']['TABLE_application_registered']
db_table_device = settings.DATABASES['default']['TABLE_device']

db_table_alerts_notificationchanneladdress = settings.DATABASES['default'][
        'TABLE_alerts_notificationchanneladdress']
db_table_active_alert = settings.DATABASES['default']['TABLE_active_alert']
db_table_bemoss_notify = settings.DATABASES['default']['TABLE_bemoss_notify']
db_table_node_info = settings.DATABASES['default']['TABLE_node_info']

PROJECT_DIR = settings.PROJECT_DIR
Agents_Launch_DIR = settings.Agents_Launch_DIR
Loaded_Agents_DIR = settings.Loaded_Agents_DIR

# Autostart_Agents_DIR = settings.Autostart_Agents_DIR
Applications_Launch_DIR = settings.Applications_Launch_DIR
#----------------------------------------------------------------------------------------------------------

# Clear temp folder
temp_path = os.path.expanduser(settings.PROJECT_DIR + "/.temp")
shutil.rmtree(temp_path)
os.mkdir(temp_path)

os.system("clear")
#1. Connect to bemossdb database
conn = psycopg2.connect(host=db_host, port=db_port, database=db_database,
                            user=db_user, password=db_password)
cur = conn.cursor()  # open a cursor to perform database operations
print "{} >> Done 1: connect to database name {}".format(agent_id, db_database)

#2. clean tables
cur.execute("DELETE FROM node_device")
cur.execute("DELETE FROM "+db_table_device)
cur.execute("DELETE FROM "+db_table_device_info)
cur.execute("DELETE FROM "+db_table_global_zone_setting)
conn.commit()

#
# cur.execute("select * from information_schema.tables where table_name=%s", (db_table_alerts_notificationchanneladdress,))
# print bool(cur.rowcount)
# if bool(cur.rowcount):
#     cur.execute("DELETE FROM "+db_table_alerts_notificationchanneladdress)
#     conn.commit()
#
# cur.execute("select * from information_schema.tables where table_name=%s", (db_table_active_alert,))
# print bool(cur.rowcount)
# if bool(cur.rowcount):
#     cur.execute("DELETE FROM "+db_table_active_alert)
#     conn.commit()
#


cur.execute("select * from information_schema.tables where table_name=%s", (db_table_bemoss_notify,))
print bool(cur.rowcount)
if bool(cur.rowcount):
    cur.execute("DELETE FROM "+db_table_bemoss_notify)
    conn.commit()

cur.execute("select * from information_schema.tables where table_name=%s", ('holiday',))
print bool(cur.rowcount)
if bool(cur.rowcount):
    cur.execute("DELETE FROM "+db_table_holiday)
    conn.commit()

cur.execute("select * from information_schema.tables where table_name=%s", ('devicedata',))
print bool(cur.rowcount)
if bool(cur.rowcount):
    cur.execute("DELETE FROM "+db_table_device)
    conn.commit()


#3. adding holidays ref www.archieves.gov/news/federal-holidays.html
cur.execute("INSERT INTO "+db_table_holiday+" VALUES(%s,%s)",
            (datetime.datetime(2017, 01, 01).date(), "New Year's Day"))
cur.execute("INSERT INTO "+db_table_holiday+" VALUES(%s,%s)",
            (datetime.datetime(2017, 1, 16).date(), "Birthday of Martin Luther King Jr."))
cur.execute("INSERT INTO "+db_table_holiday+" VALUES(%s,%s)",
            (datetime.datetime(2017, 2, 20).date(), "President's Day"))
cur.execute("INSERT INTO "+db_table_holiday+" VALUES(%s,%s)",
            (datetime.datetime(2017, 5, 29).date(), "Memorial Day"))
cur.execute("INSERT INTO "+db_table_holiday+" VALUES(%s,%s)",
            (datetime.datetime(2017, 7, 4).date(), "Independence Day"))
cur.execute("INSERT INTO "+db_table_holiday+" VALUES(%s,%s)",
            (datetime.datetime(2017, 9, 4).date(), "Labor Day"))
cur.execute("INSERT INTO "+db_table_holiday+" VALUES(%s,%s)",
            (datetime.datetime(2017, 10, 9).date(), "Columbus Day"))
cur.execute("INSERT INTO "+db_table_holiday+" VALUES(%s,%s)",
            (datetime.datetime(2017, 11, 10).date(), "Veterans Day"))
cur.execute("INSERT INTO "+db_table_holiday+" VALUES(%s,%s)",
            (datetime.datetime(2017, 11, 23).date(), "Thanksgiving Day"))
cur.execute("INSERT INTO "+db_table_holiday+" VALUES(%s,%s)",
            (datetime.datetime(2017, 12, 25).date(), "Christmas Day"))
conn.commit()
print "{} >> Done 2: added holidays to {}".format(agent_id, db_table_holiday)




#4. clear all previous agent launch files
loaded_agents = os.listdir(Loaded_Agents_DIR)
if len(loaded_agents) != 0:
    os.system("rm -rf "+Loaded_Agents_DIR+"*")
    print "{} >> Done 3: agent launch files are removed from {}".format(agent_id, Loaded_Agents_DIR)
else:
    pass

agent_launch_files = os.listdir(Agents_Launch_DIR)
if len(agent_launch_files) != 0:
    os.system("rm "+Agents_Launch_DIR+"*.launch")
    print "{} >> Done 4: agent launch files are removed from {}".format(agent_id, Agents_Launch_DIR)
else:
    pass

#7. check and confirm zone id:999 (unassigned for newly discovered devices) is in table
core_name = settings.PLATFORM['node']['name']
cur.execute("SELECT zone_id FROM "+db_table_building_zone+" WHERE zone_id=999")
if cur.rowcount == 0:
    cur.execute("INSERT INTO "+db_table_building_zone+" VALUES(%s, %s)", (999, core_name))
    conn.commit()
    print "{} >> Done 5: default columns zone_id 999 and load zone_nickname from settings file. " \
          "is inserted into {} successfully".format(agent_id, db_table_building_zone)
else:
    # Update zone nickname from default value set in ui side.
    cur.execute("UPDATE "+db_table_building_zone+" SET zone_nickname='"+core_name+"' WHERE zone_id=999")
    conn.commit()
    print "{} >> Warning: default zone 999 already exists, zone_nickname updated".format(agent_id)

#7. check and confirm zone id:999 (BEMOSS Core for newly discovered devices) is in table
cur.execute("SELECT id FROM "+db_table_global_zone_setting+" WHERE zone_id=%s", (999,))
if cur.rowcount == 0:  # this APP used to be launched before
    cur.execute("INSERT INTO "+db_table_global_zone_setting+"(id, zone_id, heat_setpoint, cool_setpoint, illuminance)"
                                                            " VALUES(%s,%s,%s,%s,%s)", (999,999,70,78,80,))
    conn.commit()

#8. create tables
cur.execute("select * from information_schema.tables where table_name=%s", ('application_running',))
print bool(cur.rowcount)
if bool(cur.rowcount):
    cur.execute("DROP TABLE application_running")
    conn.commit()
else:
    pass

cur.execute('''CREATE TABLE application_running
       (APPLICATION_ID SERIAL   PRIMARY KEY   NOT NULL,
       APP_AGENT_ID   VARCHAR(50)   NOT NULL,
       START_TIME     TIMESTAMP,
       STATUS        VARCHAR(10),
       APP_SETTING   VARCHAR(200));''')
print "Table application_running created successfully"
conn.commit()

cur.execute("select * from information_schema.tables where table_name=%s", ('application_registered',))
print bool(cur.rowcount)
if bool(cur.rowcount):
    cur.execute("DROP TABLE application_registered")
    conn.commit()
else:
    pass

cur.execute('''CREATE TABLE application_registered
       (APPLICATION_ID SERIAL   PRIMARY KEY   NOT NULL,
       APP_NAME VARCHAR (30) NOT NULL,
       EXECUTABLE VARCHAR (35) NOT NULL,
       AUTH_TOKEN VARCHAR (20) NOT NULL,
       APP_USER TEXT,
       DESCRIPTION  VARCHAR (200) NOT NULL,
       REGISTERED_TIME  TIMESTAMP  NOT NULL,
       LAST_UPDATED_TIME  TIMESTAMP NOT NULL);''')
print "Table application_registered created successfully"
conn.commit()




cur.execute("select * from information_schema.tables where table_name=%s", ('passwords_manager',))
print bool(cur.rowcount)
if bool(cur.rowcount):
    print "table already exits. Clearing"
    cur.execute("DELETE FROM passwords_manager")
    conn.commit()

cur.execute("select * from information_schema.tables where table_name=%s", ('supported_devices',))
print bool(cur.rowcount)
if bool(cur.rowcount):
    print "table already exits. Dropping"
    cur.execute("DELETE FROM supported_devices")
    conn.commit()

# cur.execute("select * from information_schema.tables where table_name=%s", ('node_device',))
# print bool(cur.rowcount)
# if bool(cur.rowcount):
#     cur.execute("DELETE FROM node_device")
#     conn.commit()
# else:
#     pass
#
#     cur.execute('''CREATE TABLE node_device
#            (TRANS_NO SERIAL PRIMARY KEY   NOT NULL,
#            DEVICE_ID  VARCHAR(50),
#            assigned_zone_ID INT,
#            CURRENT_ZONE_ID INT,
#            DATE_MOVE TIMESTAMP);''')
#     print "Table node_device created successfully"
# conn.commit()


for file in os.listdir(os.path.expanduser(settings.PROJECT_DIR + "/DeviceAPI")):
    if file.startswith('API_') and file.endswith('.py'):
        try:
            file = file.split('.')[0]
            print file
            APImodule = importlib.import_module("DeviceAPI."+file)
            APIinstance = APImodule.API()
            API_infos = APIinstance.API_info()
            for API_info in API_infos:
                #TODO: Change column name device_type to device_type_id
                cur.execute("INSERT INTO supported_devices (device_model,vendor_name,communication,device_type_id,api_name,html_template,chart_template,agent_type,identifiable,authorizable,is_cloud_device,schedule_weekday_period,schedule_weekend_period,allow_schedule_period_delete) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (API_info["device_model"],API_info["vendor_name"],API_info["communication"],API_info["device_type_id"],
                 API_info["api_name"],API_info["html_template"],API_info["chart_template"],API_info["agent_type"],API_info["identifiable"],
                 API_info["authorizable"],API_info["is_cloud_device"],API_info["schedule_weekday_period"],
                 API_info["schedule_weekend_period"],API_info["allow_schedule_period_delete"]))
            conn.commit()
        except Exception as er:
            print er
            print ("Error occurred while filling {} into supported_device table".format(file))

print "Table supported_devices populated successfully!"

# cur.execute("INSERT INTO node_info (node_id,node_name,node_type,node_model,node_status, building_name, ip_address, mac_address, associated_zone, date_added, communication, last_scanned_time, last_offline_time, node_resources_score) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
#                 (1, core_name, 'core', 'Odroid', 'ONLINE', 'blding', '192.168.10.234', 'test123abc', '999', datetime.datetime.now(), 'WiFi', None, None, 0.8))
# conn.commit()


cur.execute("UPDATE miscellaneous SET value='OFF' WHERE key='auto_discovery'")
conn.commit()

#8. close database connection
try:
    if conn:
        conn.close()
        print "{} >> Done 6: database {} connection is closed".format(agent_id, db_database)
except:
    print "{} >> database {} connection has already closed".format(agent_id, db_database)

#9. clear volttron log file, kill volttron process, kill all BEMOSS processes


#TODO make a backup of log files
os.system("rm " + settings.PROJECT_DIR + "/log/volttron.log")
os.system("rm " + settings.PROJECT_DIR + "/log/cassandra.log")

#Delete schedule files
schedule_dir = settings.Schedule_DIR
dev_folders = os.listdir(schedule_dir)
for folder in dev_folders:
    schedule_files = os.listdir((schedule_dir+folder))
    schedule_files.remove('readme.txt')
    for file in schedule_files:
        os.remove(schedule_dir+folder+'/'+file)
print "{} >> Done 7: clear volttron log file, kill volttron process, kill all " \
      "BEMOSS processes".format(agent_id)

