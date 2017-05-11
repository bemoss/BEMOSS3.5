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

'''BEMOSS UI topic templates.'''
#TODO Clean file

import os
import settings
import json


def set_wifi_3m50_update_recv_status(update_number, message):
    print os.path.basename(__file__)+'i am printing from json based file access method'
    reset_update_topic('wifi_3m50_update_recv_status')
    file_path = settings.PROJECT_DIR
    file_path = file_path.replace('bemoss_os', 'bemoss_web_ui')
    json_file = open(file_path + '/resources/identify/identify.json', "r+")
    #json_file = open(os.path.join(settings.PROJECT_DIR, 'ZMQHelper/topic_values.json'),"r+")
    _json_data = json.load(json_file)
    _json_data['wifi_3m50_update_recv_status'] = update_number+'/'+str(message).strip('[]').strip('\'\'')
    
    json_file.seek(0)
    json_file.write(json.dumps(_json_data, indent=4, sort_keys=True))
    json_file.truncate()
    json_file.close()
    return 


def set_plugload_update_recv_status(update_number, message):
    print os.path.basename(__file__)+'i am printing from json based file access method'
    reset_update_topic('plugload_update_recv_status')
    file_path = settings.PROJECT_DIR
    file_path = file_path.replace('bemoss_os', 'bemoss_web_ui')
    json_file = open(file_path + '/resources/identify/identify.json', "r+")
    #json_file = open(os.path.join(settings.PROJECT_DIR, 'ZMQHelper/topic_values.json'),"r+")
    _json_data = json.load(json_file)
    _json_data['plugload_update_recv_status'] = update_number+'/'+str(message).strip('[]').strip('\'\'')
    
    json_file.seek(0)
    json_file.write(json.dumps(_json_data, indent=4, sort_keys=True))
    json_file.truncate()
    json_file.close()
    return 


def reset_update_topic(topic):
    print os.path.basename(__file__)+'i am printing from json based file access method'
    file_path = settings.PROJECT_DIR
    file_path = file_path.replace('bemoss_os', 'bemoss_web_ui')
    json_file = open(file_path + '/resources/identify/identify.json', "r+")
    #json_file = open(os.path.join(settings.PROJECT_DIR, 'ZMQHelper/topic_values.json'),"r+")
    _json_data = json.load(json_file)
    _json_data[topic] = '{update_number}/{status}'
    
    json_file.seek(0)
    json_file.write(json.dumps(_json_data, indent=4, sort_keys=True))
    json_file.truncate()
    json_file.close()
    return


def reset_device_status_topic(update_variable):
    print os.path.basename(__file__)+'i am printing from json based file access method'
    print "inside reset device update status"
    file_path = settings.PROJECT_DIR
    file_path = file_path.replace('bemoss_os', 'bemoss_web_ui')
    json_file = open(file_path + '/resources/identify/identify.json', "r+")
    #json_file = open(os.path.join(settings.PROJECT_DIR, 'ZMQHelper/topic_values.json'),"r+")
    _json_data = json.load(json_file)
    _json_data[update_variable] = '{empty_string}'
    
    json_file.seek(0) #set the file current position to an offset
    json_file.write(json.dumps(_json_data, indent=4, sort_keys=True))
    json_file.truncate()
    json_file.close()
    print "done"
    return


def set_wifi_3m50_device_update_status(message):
    print os.path.basename(__file__)+'i am printing from json based file access method'
    topic = 'wifi_3m50_device_initial_update'
    reset_device_status_topic(topic)
    file_path = settings.PROJECT_DIR
    file_path = file_path.replace('bemoss_os', 'bemoss_web_ui')
    json_file = open(file_path + '/resources/identify/identify.json', "r+")
    #json_file = open(os.path.join(settings.PROJECT_DIR, 'ZMQHelper/topic_values.json'), "r+")
    _json_data = json.load(json_file)
    #Data comes in as string, and it is converted to json and pushed to the topic_values.json file.
    print message.strip('\'\'')
    print type(message)
    print type(json.loads(message.strip('\'\'')))
    _json_data[topic] = json.loads(message.strip('\'\''))
    
    json_file.seek(0)
    json_file.write(json.dumps(_json_data, indent=4, sort_keys=True))
    json_file.truncate()
    json_file.close()
    return 

def set_plugload_device_update_status(message):
    print os.path.basename(__file__)+'i am printing from json based file access method'
    topic = 'plugload_device_initial_update'
    reset_device_status_topic(topic)
    file_path = settings.PROJECT_DIR
    file_path = file_path.replace('bemoss_os', 'bemoss_web_ui')
    json_file = open(file_path + '/resources/identify/identify.json', "r+")
    #json_file = open(os.path.join(settings.PROJECT_DIR, 'ZMQHelper/topic_values.json'),"r+")
    _json_data = json.load(json_file)
    #Data comes in as string, and it is converted to json and pushed to the topic_values.json file.
    print message.strip('\'\'')
    print type(message)
    print type(json.loads(message.strip('\'\'')))
    _json_data[topic] = json.loads(message.strip('\'\''))
    
    json_file.seek(0)
    json_file.write(json.dumps(_json_data, indent=4, sort_keys=True))
    json_file.truncate()
    json_file.close()
    return 



def set_thermostat_schedule(message):
    print os.path.basename(__file__)+'i am printing from json based file access method'
    topic = 'thermostat_schedule'
    reset_device_status_topic(topic)
    file_path = settings.PROJECT_DIR
    file_path = file_path.replace('bemoss_os', 'bemoss_web_ui')
    json_file = open(file_path + '/resources/identify/identify.json', "r+")
    #json_file = open(os.path.join(settings.PROJECT_DIR, 'ZMQHelper/topic_values.json'),"r+")
    _json_data = json.load(json_file)
    message = str(message[0]).strip('[]')
    print type(message)
    _json_data[topic] = message
    
    json_file.seek(0)
    json_file.write(json.dumps(_json_data, indent=4, sort_keys=True))
    json_file.truncate()
    json_file.close()
    return 


def set_wifi_3m50_schedule_status(update_number, message):
    print os.path.basename(__file__)+'i am printing from json based file access method'
    topic = 'wifi_3m50_update_schedule_status'
    message = update_number+'/'+str(message).strip('[]').strip('\'\'')
    reset_device_status_topic(topic)
    file_path = settings.PROJECT_DIR
    file_path = file_path.replace('bemoss_os', 'bemoss_web_ui')
    json_file = open(file_path + '/resources/identify/identify.json', "r+")
    #json_file = open(os.path.join(settings.PROJECT_DIR, 'ZMQHelper/topic_values.json'),"r+")
    _json_data = json.load(json_file)
    _json_data[topic] = message
    
    json_file.seek(0)
    json_file.write(json.dumps(_json_data, indent=4, sort_keys=True))
    json_file.truncate()
    json_file.close()
    return 


def set_hue_page_load_data(message):
    print os.path.basename(__file__)+'i am printing from json based file access method'
    topic = 'hue_device_initial_update'
    reset_device_status_topic(topic)
    file_path = settings.PROJECT_DIR
    file_path = file_path.replace('bemoss_os', 'bemoss_web_ui')
    json_file = open(file_path + '/resources/identify/identify.json', "r+")
    #json_file = open(os.path.join(settings.PROJECT_DIR, 'ZMQHelper/topic_values.json'),"r+")
    _json_data = json.load(json_file)
    #_json_data[topic] = '\''+str(message) + '\''
    _json_data[topic] = json.loads(message.strip('\'\''))
    
    json_file.seek(0)
    json_file.write(json.dumps(_json_data, indent=4, sort_keys=True))
    json_file.truncate()
    json_file.close()
    return 

def set_hue_device_update_status(message):
    print os.path.basename(__file__)+'i am printing from json based file access method: set_hue_device_update_status'
    topic = 'hue_update_recv_status'
    message = str(message).strip('[]')
    reset_device_status_topic(topic)
    print message
    file_path = settings.PROJECT_DIR
    file_path = file_path.replace('bemoss_os', 'bemoss_web_ui')
    json_file = open(file_path + '/resources/identify/identify.json', "r+")
    #json_file = open(os.path.join(settings.PROJECT_DIR, 'ZMQHelper/topic_values.json'),"r+")
    _json_data = json.load(json_file)
    _json_data[topic] = message
    
    json_file.seek(0)
    json_file.write(json.dumps(_json_data, indent=4, sort_keys=True))
    json_file.truncate()
    json_file.close()
    return


def set_lighting_page_load_data(message):
    print os.path.basename(__file__)+'i am printing from json based file access method'
    topic = 'lighting_initial_update'
    reset_device_status_topic(topic)
    file_path = settings.PROJECT_DIR
    file_path = file_path.replace('bemoss_os', 'bemoss_web_ui')
    json_file = open(file_path + '/resources/identify/identify.json', "r+")
    #json_file = open(os.path.join(settings.PROJECT_DIR, 'ZMQHelper/topic_values.json'),"r+")
    _json_data = json.load(json_file)
    #_json_data[topic] = '\''+str(message) + '\''
    _json_data[topic] = json.loads(message.strip('\'\''))

    json_file.seek(0)
    json_file.write(json.dumps(_json_data, indent=4, sort_keys=True))
    json_file.truncate()
    json_file.close()
    return


def set_lighting_device_update_status(message):
    print os.path.basename(__file__)+'i am printing from json based file access method: set_hue_device_update_status'
    topic = 'lighting_update_recv_status'
    message = str(message).strip('[]')
    reset_device_status_topic(topic)
    print message
    file_path = settings.PROJECT_DIR
    file_path = file_path.replace('bemoss_os', 'bemoss_web_ui')
    json_file = open(file_path + '/resources/identify/identify.json', "r+")
    #json_file = open(os.path.join(settings.PROJECT_DIR, 'ZMQHelper/topic_values.json'),"r+")
    _json_data = json.load(json_file)
    _json_data[topic] = message

    json_file.seek(0)
    json_file.write(json.dumps(_json_data, indent=4, sort_keys=True))
    json_file.truncate()
    json_file.close()
    return


def identify_device_update(agent_id, message, topic):
    #print os.path.basename(__file__)+'i am printing from json based file access method: identify_device_update'
    #topic = 'identify_device_status'
    message = str(message).strip('[]')
    reset_device_status_topic(topic)
    print message
    file_path = settings.PROJECT_DIR
    file_path = file_path.replace('bemoss_os', 'bemoss_web_ui')
    json_file = open(file_path + '/resources/identify/identify.json', "r+")
    #json_file = open(os.path.join(settings.PROJECT_DIR, 'ZMQHelper/topic_values.json'), "r+")
    _json_data = json.load(json_file)
    _json_data[topic] = agent_id + '/' + message

    json_file.seek(0)
    json_file.write(json.dumps(_json_data, indent=4, sort_keys=True))
    json_file.truncate()
    json_file.close()
    return


def set_plugload_schedule(message):
    print os.path.basename(__file__)+'i am printing from json based file access method'
    print message
    print type(message)
    topic = 'plugload_schedule'
    reset_device_status_topic(topic)
    file_path = settings.PROJECT_DIR
    file_path = file_path.replace('bemoss_os', 'bemoss_web_ui')
    json_file = open(file_path + '/resources/identify/identify.json', "r+")
    #json_file = open(os.path.join(settings.PROJECT_DIR, 'ZMQHelper/topic_values.json'),"r+")
    _json_data = json.load(json_file)
    message = str(message[0]).strip('[]')
    print type(message)
    _json_data[topic] = json.loads(message)

    json_file.seek(0)
    json_file.write(json.dumps(_json_data, indent=4, sort_keys=True))
    json_file.truncate()
    json_file.close()
    return


def set_lighting_schedule(message):
    print os.path.basename(__file__)+'i am printing from json based file access method'
    print message
    print type(message)
    topic = 'lighting_schedule'
    reset_device_status_topic(topic)
    file_path = settings.PROJECT_DIR
    file_path = file_path.replace('bemoss_os', 'bemoss_web_ui')
    json_file = open(file_path + '/resources/identify/identify.json', "r+")
    #json_file = open(os.path.join(settings.PROJECT_DIR, 'ZMQHelper/topic_values.json'), "r+")
    _json_data = json.load(json_file)
    message = str(message[0]).strip('[]')
    print type(message)
    _json_data[topic] = json.loads(message)

    json_file.seek(0)
    json_file.write(json.dumps(_json_data, indent=4, sort_keys=True))
    json_file.truncate()
    json_file.close()
    return


def set_schedule_update_status(agent_id, message):
    print os.path.basename(__file__)+'i am printing from json based file access method'
    topic = 'schedule_update_status'
    reset_device_status_topic(topic)
    file_path = settings.PROJECT_DIR
    file_path = file_path.replace('bemoss_os', 'bemoss_web_ui')
    json_file = open(file_path + '/resources/identify/identify.json', "r+")
    #json_file = open(os.path.join(settings.PROJECT_DIR, 'ZMQHelper/topic_values.json'),"r+")
    _json_data = json.load(json_file)
    message = str(message[0]).strip('[]')
    print type(message)
    _json_data[topic] = agent_id + '/' + message

    json_file.seek(0)
    json_file.write(json.dumps(_json_data, indent=4, sort_keys=True))
    json_file.truncate()
    json_file.close()
    return