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
from bemoss_lib.protocols.Modbus import Modbuscommon
from DeviceAPI.BaseAPI import baseAPI
import csv
import os
debug = True


class ModbusAPI(baseAPI):

    def __init__(self,**kwargs):
        super(ModbusAPI, self).__init__(**kwargs)
        self.set_variable('connection_renew_interval',6000)
        self.device_supports_auto = True
        if 'address' in self.variables.keys():
            address_parts = self.get_variable("address").split(':')
            self.address = address_parts[0]
            self.subordinate_id =int(address_parts[1])
        self._debug = True

    def discover(self):

        discovered_list=list()
        client=Modbuscommon()
        config_path = os.path.dirname(os.path.abspath(__file__))
        config_path = config_path + "/Device_details/modbus_devices.csv"
        with open(os.path.join(config_path), 'rU') as infile:
            reader = csv.DictReader(infile)
            data = {}
            for row in reader:
                for header, value in row.items():
                    try:
                        data[header].append(value)
                    except KeyError:
                        data[header] = [value]
        client.subordinatelist=data["Subordinate_id"]
        device_list=client.discovery()
        for address in device_list:
             if isinstance(address, dict):
                 break
             else:
                subordinate_id=address.split(':')[1]
                for idx, val in enumerate(data["Subordinate_id"]):
                    if subordinate_id==val:
                        macaddress = data["MacAddress"][idx]
                        model = data["ModelName"][idx]
                        vendor = data["VendorName"][idx]
                        discovered_list.append({'address': address, 'mac': macaddress,
                                            'model': model, 'vendor': vendor})
                        break
        print discovered_list
        return discovered_list