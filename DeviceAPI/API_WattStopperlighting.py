# -*- coding: utf-8 -*-
from __future__ import division
'''
Copyright (c) 2014 by Virginia Polytechnic Institute and State University
All rights reserved

Virginia Polytechnic Institute and State University (Virginia Tech) owns the copyright for the BEMOSS software and its
associated documentation (“Software”) and retains rights to grant research rights under patents related to
the BEMOSS software to other academic institutions or non-profit research institutions.
You should carefully read the following terms and conditions before using this software.
Your use of this Software indicates your acceptance of this license agreement and all terms and conditions.

You are hereby licensed to use the Software for Non-Commercial Purpose only.  Non-Commercial Purpose means the
use of the Software solely for research.  Non-Commercial Purpose excludes, without limitation, any use of
the Software, as part of, or in any way in connection with a product or service which is sold, offered for sale,
licensed, leased, loaned, or rented.  Permission to use, copy, modify, and distribute this compilation
for Non-Commercial Purpose to other academic institutions or non-profit research institutions is hereby granted
without fee, subject to the following terms of this license.

Commercial Use If you desire to use the software for profit-making or commercial purposes,
you agree to negotiate in good faith a license with Virginia Tech prior to such profit-making or commercial use.
Virginia Tech shall have no obligation to grant such license to you, and may grant exclusive or non-exclusive
licenses to others. You may contact the following by email to discuss commercial use: vtippatents@vtip.org

Limitation of Liability IN NO EVENT WILL VIRGINIA TECH, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR REDISTRIBUTE
THE PROGRAM AS PERMITTED ABOVE, BE LIABLE TO YOU FOR DAMAGES, INCLUDING ANY GENERAL, SPECIAL, INCIDENTAL OR
CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE OR INABILITY TO USE THE PROGRAM (INCLUDING BUT NOT LIMITED TO
LOSS OF DATA OR DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD PARTIES OR A FAILURE
OF THE PROGRAM TO OPERATE WITH ANY OTHER PROGRAMS), EVEN IF VIRGINIA TECH OR OTHER PARTY HAS BEEN ADVISED
OF THE POSSIBILITY OF SUCH DAMAGES.

For full terms and conditions, please visit https://bitbucket.org/bemoss/bemoss_os.

Address all correspondence regarding this license to Virginia Tech’s electronic mail address: vtippatents@vtip.org

__author__ =  "BEMOSS Team"
__credits__ = ""
__version__ = "3.5"
__maintainer__ = "BEMOSS Team""
__email__ = "aribemoss@gmail.com"
__website__ = ""
__status__ = "Prototype"
__created__ = "2016-10-24 16:12:00"
__lastUpdated__ = "2016-10-25 13:25:00"
'''

from bemoss_lib.utils.BEMOSS_ONTOLOGY import BEMOSS_ONTOLOGY
from DeviceAPI.BaseAPI_WattStopper import baseAPI_Wattstopper
debug = True


class API(baseAPI_Wattstopper):


    def API_info(self):
        return [{'device_model': 'LMRC-212', 'vendor_name': 'WattStopper', 'communication': 'BACnet',
                 'device_type_id': 2, 'api_name': 'API_WattStopperlighting','html_template': 'lighting/lighting.html',
                 'agent_type': 'BasicAgent', 'identifiable': True,'authorizable': False, 'is_cloud_device': False,
                 'schedule_weekday_period': 4, 'schedule_weekend_period': 4, 'allow_schedule_period_delete': True,
                 'chart_template': 'charts/charts_lighting.html'},
                ]

    def dashboard_view(self):
        if self.get_variable(BEMOSS_ONTOLOGY.STATUS.NAME) == BEMOSS_ONTOLOGY.STATUS.POSSIBLE_VALUES.ON:
            return {"top": None, "center": {"type": "image", "value": 'wattstopper_on.png'},
                    "bottom": BEMOSS_ONTOLOGY.STATUS.NAME}
        else:
            return {"top": None, "center": {"type": "image", "value": 'wattstopper_off.png'},
                    "bottom": BEMOSS_ONTOLOGY.STATUS.NAME}

    def ontology(self):
        return {"VOLTAGE":BEMOSS_ONTOLOGY.VOLTAGE, "DIMMER": BEMOSS_ONTOLOGY.BRIGHTNESS,
                "Status":BEMOSS_ONTOLOGY.STATUS}

    def getDataFromDevice(self):

        try:

            results = self.Bacnet_read()

            if "DIMMER" in results.keys():
                if results["DIMMER"] > 0:
                    results["Status"] = BEMOSS_ONTOLOGY.STATUS.POSSIBLE_VALUES.ON
                else:
                    results["Status"] = BEMOSS_ONTOLOGY.STATUS.POSSIBLE_VALUES.OFF
            print results
            return results
        except Exception as e:
            print e
            return {}


    def setDeviceData(self, postmsg):

            try:
                devicemess = dict()
                if BEMOSS_ONTOLOGY.STATUS.NAME in postmsg:
                    if postmsg[BEMOSS_ONTOLOGY.STATUS.NAME] == BEMOSS_ONTOLOGY.STATUS.POSSIBLE_VALUES.OFF:
                        postmsg[BEMOSS_ONTOLOGY.BRIGHTNESS.NAME] = BEMOSS_ONTOLOGY.BRIGHTNESS.POSSIBLE_VALUES.MIN
                        del postmsg[BEMOSS_ONTOLOGY.STATUS.NAME]
                    else:
                        del postmsg[BEMOSS_ONTOLOGY.STATUS.NAME]
                        if BEMOSS_ONTOLOGY.BRIGHTNESS.NAME not in postmsg:
                            postmsg[BEMOSS_ONTOLOGY.BRIGHTNESS.NAME] = BEMOSS_ONTOLOGY.BRIGHTNESS.POSSIBLE_VALUES.MAX

                for key, value in postmsg.iteritems():
                    for value2 in self.ontology().values():
                        value2 = value2.NAME
                        if key == value2:
                            devicemess[key] = value

                result = self.sendcommand(devicemess)
                return True
            except Exception as e:
                print e
                return False

    def identifyDevice(self):
        identifyDeviceResult = False
        try:
            postmsg = dict()
            ret1 = False
            bacnetread = self.Bacnet_read()
            if bacnetread:
                prev_dim_level = bacnetread.get("DIMMER")
            else:
                return identifyDeviceResult
            if prev_dim_level == 0:
                postmsg[BEMOSS_ONTOLOGY.BRIGHTNESS.NAME] = BEMOSS_ONTOLOGY.BRIGHTNESS.POSSIBLE_VALUES.MAX
                ret1 = self.sendcommand(postmsg)
            else:
                postmsg[BEMOSS_ONTOLOGY.BRIGHTNESS.NAME] = BEMOSS_ONTOLOGY.BRIGHTNESS.POSSIBLE_VALUES.MIN
                ret1 = self.sendcommand(postmsg)
            if ret1:
                self.timeDelay(5)
                postmsg = {BEMOSS_ONTOLOGY.BRIGHTNESS.NAME: prev_dim_level}
                ret2 = self.sendcommand(postmsg)
                if ret2:
                    identifyDeviceResult = True
        except Exception as e:

            print "ERROR: Reading/Writing BACnet property at identifyDevice"
            return identifyDeviceResult



