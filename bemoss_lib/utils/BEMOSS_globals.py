import os
from collections import OrderedDict
import settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings_tornado'

APPROVAL_SHORT_CODE = {'Approved':'APR','Pending':'PND','Non-BEMOSS Device':'NBD'}

class ZONE_ASSIGNMENT_TYPES():
    PERMANENT = 1
    TEMPORARY = 0

class APPROVAL_STATUS():
    APR='APR'
    PND='PND'
    NBD='NBD'
    full_names = OrderedDict([('PND','Pending'),('APR','Approved'), ('NBD', 'Non-BEMOSS')])

class STATUS_CHANGE():
    AGENT_ID, AGENT_STATUS, NODE, NODE_ASSIGNMENT_TYPE = 'agent_id', 'agent_status', 'node', 'node_assignment_type'

PUB_ADDRESS = "ipc://" + settings.PROJECT_DIR + '/pub.socket'
SUB_ADDRESS = "ipc://" + settings.PROJECT_DIR + '/sub.socket'
ZMQ_SEPARATOR = "*^*"