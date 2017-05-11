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
import os
from setuptools import find_packages
import sys
import psycopg2  # PostgresQL database adapter
import time
import datetime

#APP CONFIGURATION-------------------------------------------------------------------------------
#TODO change auth_token
auth_token = 'bemoss'
#TODO change description
app_description = 'APP to launch new APPs'
#TODO change app_user
app_user = ["os"]
#------------------------------------------------------------------------------------------------

app_name = find_packages('.')
app_name = app_name[0]
# print app_name
app_exec = app_name+'agent-0.1-py2.7.egg'
exec_store = app_name + 'agent'
# print app_exec
app_working_directory = os.getcwd()
app_folder = os.path.basename(os.getcwd())
os.chdir(os.path.expanduser("~/volttron/"))  # = ~/volttron/
current_working_directory = os.getcwd()
# print 'current working directory: {}'.format(_current_working_directory)
#import settings.py file to get database information
sys.path.append(current_working_directory)
import settings

# @params agent & DB interfaces
db_host = settings.DATABASES['default']['HOST']
db_port = settings.DATABASES['default']['PORT']
db_database = settings.DATABASES['default']['NAME']
db_user = settings.DATABASES['default']['USER']
db_password = settings.DATABASES['default']['PASSWORD']
db_table_application_registered = settings.DATABASES['default']['TABLE_application_registered']

try:
    con = psycopg2.connect(host=db_host, port=db_port, database=db_database, user=db_user,
                                password=db_password)
    cur = con.cursor()  # open a cursor to perfomm database operations
    print("APP Installer >> connects to the database name {} successfully".format(db_database))
except:
    print("APP Installer >> ERROR: {} fails to connect to the database name {}".format(app_name, db_database))

cur.execute("SELECT executable FROM "+db_table_application_registered+" WHERE app_name=%s", (app_name,))
if cur.rowcount != 0:  # app has already been installed and registered
    print("APP Installer >> the APP name {} exists, this process will re-install the APP".format(app_name))
    cur.execute("DELETE FROM "+db_table_application_registered+" WHERE app_name=%s", (app_name,))
else:  # go ahead and add this app to database
    pass

# print app_folder
print 'APP Installer >> installing APP name {}, in folder {}, with exec {} ...'.format(app_name, app_folder, app_exec)
# print 'current working directory: {}'.format(_current_working_directory)
os.system(". env/bin/activate"
          ";volttron-pkg package "+app_working_directory)  # package the folder of app
# os.system("sudo bin/volttron-lite -c dev-config.ini -v -v &")
# time.sleep(1)
# os.system("sudo rm bin/"+app_exec)
# os.system("sudo rm bemoss/Applications/egg/"+app_exec)
# os.system("sudo volttron/scripts/build-app2.sh "+app_folder)
# os.system("sudo bin/volttron-ctrl install-executable bemoss/Applications/egg/" + app_exec)
print '-----------------------------------------------------'
print 'APP name {}, in folder {}, with exec {} is installed successfully'.format(app_name, app_folder, app_exec)
print '-----------------------------------------------------'
os.system("sudo chmod 777 -R "+app_working_directory)
os.system("sudo chmod 777 -R /tmp/volttron_wheels")
cur.execute("SELECT application_id FROM "+db_table_application_registered)
if cur.rowcount != 0:
    # print 'cur.fetchall()' + str(max(cur.fetchall())[0])
    app_no = max(cur.fetchall())[0] + 1
else: #default no_app
    app_no = 1
registered_time = str(datetime.datetime.now())
last_updated_time = str(datetime.datetime.now())
cur.execute("INSERT INTO application_registered(application_id, app_name, executable, auth_token, app_user, "
            "description,registered_time,last_updated_time) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",
            (app_no, app_name, exec_store, auth_token, str(app_user), app_description, registered_time, last_updated_time))
con.commit()
os.system("sudo killall volttron-lite")