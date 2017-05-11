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

__author__ =  "BEMOSS Team"

import json
import os
from django_web_server import settings
import sys
import datetime

def reset_device_status_topic(agent_id, device_type):
    print os.path.basename(__file__)+'i am printing from json based file access method'
    print "inside reset device update status"
    file_path = settings.PROJECT_DIR
    print file_path
    file_path = file_path.replace('bemoss_os', 'bemoss_web_ui')
    print file_path
    json_file = open(file_path + '/resources/page_load/page_load.json', "r+")
    _json_data = json.load(json_file)
    agent_id = str(agent_id).encode('ascii', 'ignore')
    device_type = str(device_type).encode('ascii', 'ignore')
    if agent_id in _json_data[device_type]:
        _json_data[device_type][agent_id]['page_load'] = "{empty_string}"

    json_file.seek(0) #set the file current position to an offset
    json_file.write(json.dumps(_json_data, indent=4, sort_keys=True))
    json_file.truncate()
    json_file.close()
    print "done"


def page_load(agent_id, device_type, message):
    print os.path.basename(__file__)+'i am printing from json based file access method'
    reset_device_status_topic(agent_id, device_type)
    #json_file = open(os.path.join(settings.PROJECT_DIR, 'resources/page_load/page_load.json'), "r+")
    #json_file = open('resources/page_load/page_load.json', "r+")
    file_path = settings.PROJECT_DIR
    file_path = file_path.replace('bemoss_os', 'bemoss_web_ui')
    json_file = open(file_path + '/resources/page_load/page_load.json', "r+")
    _json_data = json.load(json_file)
    #Data comes in as string, and it is converted to json and pushed to the topic_values.json file.
    print type(message)
    message = message.encode('ascii', 'ignore')
    message = json.loads(message, object_hook=_decode_dict)
    agent_id = str(agent_id).encode('ascii', 'ignore')
    device_type = str(device_type).encode('ascii', 'ignore')
    print type(agent_id)
    print type(device_type)

    if agent_id not in _json_data[device_type]:
        _json_data[device_type][agent_id] = {"page_load": "{empty_string}"}
    _json_data[device_type][agent_id]['page_load'] = message

    json_file.seek(0)
    json_file.write(json.dumps(_json_data, indent=4, sort_keys=True))
    json_file.truncate()
    json_file.close()


def _decode_list(data):
    rv = []
    for item in data:
        if isinstance(item, unicode):
            item = item.encode('utf-8')
        elif isinstance(item, list):
            item = _decode_list(item)
        elif isinstance(item, dict):
            item = _decode_dict(item)
        rv.append(item)
    return rv


def _decode_dict(data):
    rv = {}
    for key, value in data.iteritems():
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        elif isinstance(value, list):
            value = _decode_list(value)
        elif isinstance(value, dict):
            value = _decode_dict(value)
        rv[key] = value
    return rv