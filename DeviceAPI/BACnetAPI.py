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
import csv
from collections import Counter, defaultdict
import os
import gevent
from DeviceAPI.BaseAPI import baseAPI
from services.core.MainDriverAgent.main_driver.driver import DriverAgent
from csv import DictWriter
from bacpypes.object import get_datatype
from bacpypes.primitivedata import Enumerated, Unsigned, Boolean, Integer, Real, Double
debug = True
from ast import literal_eval

class BACnetAPI(baseAPI):

    def __init__(self, parent,converter=None,**kwargs):
        baseAPI.__init__(self,**kwargs)
        #DriverAgent.__init__(self,parent=parent,config_name=None)
        self.device_supports_auto = True
        self._debug = True
        self.parent = parent
        self.converter = converter
        self.proxy_address = "platform.bacnet_proxy"
        self.config_file = None
        if 'vip' in self.variables.keys():
            self.vip = self.variables['vip']
    #        self.core = BasicCore(self)
            self.core= self.variables['core']

    def discover(self):

        try:
            deviceinfo = self.broadcast()
            return deviceinfo

        except Exception as e:
            print e
            return None

    def broadcast(self, *args):

      try:
            deviceinfo=list()
            Remote_addresses=set()
            Remote_address=list()
            Identifier=list()
            discovery2=list()
            discovery1=list()
            self.proxy_address ="platform.bacnet_proxy"
            retries=2

            while retries>0:
                try:
                    addresses = self.vip.rpc.call(self.proxy_address, 'broadcast', *args).get(timeout=10.0)
                except gevent.Timeout:
                    print "Discovery call timeout"
                    return None
                for a,b in addresses:
                    discovery1.append(a)
                    discovery2.append(b)
                retries=retries-1
            Remote_addresses=zip(discovery1,discovery2)
            Remote_addresses=list(set(Remote_addresses))
            for Address, property_instance in Remote_addresses:
                Remote_address.append(Address)
                Identifier.append(property_instance)
            for i in range(0, len(Identifier)):
                Address = Remote_address[i]  # destination address
                object_instance = Identifier[i]
                if object_instance!=4194303:
                    if object_instance!=0:
                        model,vendor=self.GetModelVendor(Address,object_instance)
                        deviceinfo.append({'address': Address, 'mac': str(object_instance),
                               'model': model, 'vendor': vendor, })
            config_path = os.path.dirname(os.path.abspath(__file__))
            config_path = config_path + "/Bacnetdata"
            for device in deviceinfo:
                address = device["address"]
                device_id = device["mac"]
                filename = str(device_id) + ".csv"
                success = False
                for files in os.listdir(config_path):
                    if files.endswith(filename):
                        success = True
                if not success:
                        self.configure_data(address, device_id)
            #search for config

            return deviceinfo
      except Exception as e:
          print e
          return deviceinfo


    def GetModelVendor(self,Address,object_instance):

        model= ""
        vendor = ""
        retries = 2
        while retries > 0:
            try:
                    propertylist=["modelName","vendorName"]
                    value= self.vip.rpc.call(self.proxy_address, 'simple_read', Address,object_instance,propertylist).get(timeout=10.0)
                    if len(value)==2:
                        vendor,model=value
                    return model,vendor
            except Exception as e:
                print e
                retries=retries-1
            except gevent.Timeout:
                retries=retries-1
        return model,vendor

    def getDataFromDevice(self):


        bacnetread = self.Bacnet_read()
        print bacnetread
        return bacnetread

    def setDeviceData(self, postmsg):

         try:
            result = self.sendcommand(postmsg)
            return result
         except Exception as e:
            print e
            return False

    def Bacnet_read(self):

        results={}
        needed_points = list()
        needed_objecttype = list()
        needed_index = list()
        data = self.readcsv()
        if data:
            device_count = data["Device number"]
            device_map = self.duplicates_indices(device_count)
            for device, values in device_map.iteritems():
                if self.number == device:
                    for value in values:
                        if data['Reference Point Name'][value] in self.ontology():
                            needed_points.append(data['Reference Point Name'][value])
                            needed_objecttype.append(data['BACnet Object Type'][value])
                            needed_index.append(data['Index'][value])
                    devicepoints = zip(needed_points, needed_objecttype, needed_index)
                    # self.setup_device(needed_points)
                    try:
                        results = self.Bemoss_read(devicepoints)
                        print results
                        # results = self.interface.scrape_all()
                        for key, value in results.iteritems():
                            try:
                                valuetype = literal_eval(str(value))
                                if isinstance(valuetype, int):
                                    if self.converter:
                                        results[key] = self.dict_rev_translate(self.converter, value)
                                elif isinstance(valuetype, float):
                                    results[key] = round(value, 2)

                            except ValueError:
                                if self.converter:
                                    results[key] = self.dict_rev_translate(self.converter, value)
                    except Exception as e:
                        return results

                    return results

    def sendcommand(self, postmsg):

            point_names = list()
            setpoint=list()
            setvalues=list()
            needed_points = list()
            needed_objecttype = list()
            needed_index = list()
            for variable_name,set_value in postmsg.iteritems():
                #if variable_name in self.ontology().keys():
                    for key, value in self.ontology().iteritems():
                        if variable_name == value.NAME:
                            point_names.append(key)
                            setpoint.append(set_value)
                            break
            final_message=dict(zip(point_names, setpoint))
            data = self.readcsv()
            if data:
                device_count = data["Device number"]
                device_map = self.duplicates_indices(device_count)
                for device, values in device_map.iteritems():

                    if self.number == device:
                        for value in values:
                            if data['Reference Point Name'][value] in final_message.keys():

                                needed_points.append(data['Reference Point Name'][value])
                                needed_objecttype.append(data['BACnet Object Type'][value])
                                needed_index.append(data['Index'][value])
                                if self.converter:
                                    setvalues.append((self.converter[final_message[data['Reference Point Name'][value]]]))
                                else:
                                    setvalues.append(final_message[data['Reference Point Name'][value]])
                        devicepoints = zip(needed_points, needed_objecttype, needed_index,setvalues)
                        break
            results = self.writedata(devicepoints)
            return True

    def writedata(self, postmessage,priority=8):

        target_address = self.variables['address']
        writeresults = list()
        for needed_points, needed_objecttype, needed_index,setvalue in postmessage:

            setvalue = setvalue
            object_type=needed_objecttype
            instance_number=needed_index
            property="presentValue"
            try:
                #results=self.interface.set_point(point_name, setvalue, priority=8)
                args = [target_address, setvalue,
                        object_type,
                        int(instance_number),
                        property,
                        priority]
                result = self.vip.rpc.call(self.proxy_address, 'write_property', *args).get(timeout=10.0)


            except gevent.Timeout:
                    print "Write function timeout "
                    return False
            except Exception as e:
                    print e
                    return False
        writeresults=True
        return writeresults

    def readcsv(self):
        config_path = os.path.dirname(os.path.abspath(__file__))
        device_path = config_path + self.config_file

        with open(os.path.join(device_path), 'rU') as infile:
            reader = csv.DictReader(infile)
            data = {}
            for row in reader:
                for header, value in row.items():
                    try:
                        data[header].append(value)
                    except KeyError:
                        data[header] = [value]
        return data

    def duplicates_indices(self,lst):
        dup, ind = self.duplicates(lst), defaultdict(list)
        for i, v in enumerate(lst):
            if v in dup: ind[v].append(i)
        return ind

    def duplicates(self,lst):
        cnt = Counter(lst)
        return [key for key in cnt.keys() if cnt[key] >= 1]


    def Bemoss_read(self,devicepoints):
        point_map = {}
        result={}

        target_address=self.variables['address']
        for point_name,object_type,instance_number in devicepoints:

                point_map[point_name] = [object_type,
                                                  int(instance_number),
                                                  "presentValue"]
        try:
            result = self.vip.rpc.call(self.proxy_address, 'read_properties',
                                       target_address, point_map,
                                           ).get(timeout=10.0)
        except gevent.Timeout:
            print "BEMOSS Read function timeout "


        return result

    def process_device_object_reference(self, address, obj_type, index, property_name, max_range_report, config_writer):

        objectCount = self.vip.rpc.call( address, obj_type, index, property_name, index=0)

        for object_index in xrange(1, objectCount + 1):
            #_log.debug('property_name index = ' + repr(object_index))

            object_reference = self.vip.rpc.call(address,obj_type,index,property_name,index=object_index)

            # Skip references to objects on other devices.
            if object_reference.deviceIdentifier is not None:
                continue

            sub_obj_type, sub_obj_index = object_reference.objectIdentifier

            self.process_object( address, sub_obj_type, sub_obj_index, max_range_report, config_writer)

    def process_object(self, address, obj_type, index, config_writer, max_range_report=None):
       # _log.debug('obj_type = ' + repr(obj_type))
       # _log.debug('bacnet_index = ' + repr(index))

        writable = 'TRUE'

        subondinate_list_property = get_datatype(obj_type, 'subordinateList')
        if subondinate_list_property is not None:
           # _log.debug('Processing StructuredViewObject')
            try:

                self.process_device_object_reference(self, address, obj_type, index, 'subordinateList', max_range_report,
                                            config_writer)
            except Exception as e:
                print e
                pass
            return

        subondinate_list_property = get_datatype(obj_type, 'zoneMembers')
        if subondinate_list_property is not None:

            try:
               # _log.debug('Processing LifeSafetyZoneObject')
                self.process_device_object_reference( address, obj_type, index, 'zoneMembers', max_range_report,
                                            config_writer)
            except Exception as e:
                print e
                pass
            return

        present_value_type = get_datatype(obj_type, 'presentValue')
        if present_value_type is None:
            #_log.debug('This object type has no presentValue. Skipping.')
            return

        if not issubclass(present_value_type, (Enumerated,
                                               Unsigned,
                                               Boolean,
                                               Integer,
                                               Real,
                                               Double)):
           # _log.debug('present Value is an unsupported type: ' + repr(present_value_type))
            return

        try:
            description = self.vip.rpc.call(self.proxy_address, 'simple_read', address, index,
                                            propertylist=["objectName"], obj_type=obj_type).get(timeout=10.0)
            if not description:
                object_name = "NO NAME! PLEASE NAME THIS."
            else:
                description = description[0]
                object_name = description
                #_log.debug('object name = ' + object_name)
        except TypeError:
            object_name = "NO NAME! PLEASE NAME THIS."

        # _log.debug('  object type = ' + obj_type)
        #         _log.debug('  object index = ' + str(index))

        try:
            object_notes = self.vip.rpc.call(self.proxy_address, 'simple_read', address, index,
                                            propertylist=["description"], obj_type=obj_type).get(timeout=10.0)
            if not object_notes:
                object_notes=''
            else:
                object_notes=object_notes[0]

        except TypeError:
            object_notes = ''

        object_units_details = ''

        if issubclass(present_value_type, Enumerated):
            object_units = 'Enum'
            values = present_value_type.enumerations.values()
            min_value = min(values)
            max_value = max(values)

            vendor_range = ''
            if hasattr(present_value_type, 'vendor_range'):
                vendor_min, vendor_max = present_value_type.vendor_range
                vendor_range = ' (vendor {min}-{max})'.format(min=vendor_min, max=vendor_max)

            object_units_details = '{min}-{max}{vendor}'.format(min=min_value, max=max_value, vendor=vendor_range)

            if not obj_type.endswith('Input'):
                try:
                    default_value = self.vip.rpc.call(self.proxy_address, 'simple_read', address, index,
                                            propertylist=["relinquishDefault"], obj_type=obj_type).get(timeout=10.0)
                    if not default_value:
                        pass
                    else:
                        default_value=default_value [0]
                    if type(default_value)==str:
                        object_units_details += ' (default {default})'.format(
                            default=present_value_type.enumerations[default_value])
                    else:
                        object_units_details += ' (default {default})'.format(
                            default=default_value)
                    # writable = 'TRUE'
                except TypeError:
                    pass
                except ValueError:
                    pass

            if not object_notes:
                enum_strings = []
                for name in Enumerated.keylist(present_value_type(0)):
                    value = present_value_type.enumerations[name]
                    enum_strings.append(str(value) + '=' + name)

                object_notes = present_value_type.__name__ + ': ' + ', '.join(enum_strings)


        elif issubclass(present_value_type, Boolean):
            object_units = 'Boolean'

        elif get_datatype(obj_type, 'units') is None:
            if obj_type.startswith('multiState'):
                object_units = 'State'
                try:
                    state_count = self.vip.rpc.call(self.proxy_address, 'simple_read', address, index,
                                            propertylist=["numberOfStates"], obj_type=obj_type).get(timeout=10.0)
                    if not state_count:
                        pass
                    else:
                        state_count=state_count[0]
                    object_units_details = 'State count: {}'.format(state_count)
                except TypeError:
                    pass

                try:
                    enum_strings = []
                    state_list = self.vip.rpc.call(self.proxy_address, 'simple_read', address, index,
                                            propertylist=["stateText"], obj_type=obj_type).get(timeout=10.0)
                    if not state_list:
                        pass
                    else:
                        state_list= state_list[0]

                    for name in state_list[1:]:
                        enum_strings.append(name)

                    object_notes = ', '.join('{}={}'.format(x, y) for x, y in enumerate(enum_strings, start=1))

                except TypeError:
                    pass

                if obj_type != 'multiStateInput':
                    try:
                        default_value = self.vip.rpc.call(self.proxy_address, 'simple_read', address, index,
                                            propertylist=["relinquishDefault"], obj_type=obj_type).get(timeout=10.0)
                        if not default_value:
                            pass
                        else:
                            default_value=default_value[0]
                        object_units_details += ' (default {default})'.format(default=default_value)
                        object_units_details = object_units_details.strip()
                        # writable = 'TRUE'
                    except TypeError:
                        pass
                    except ValueError:
                        pass

            elif obj_type == 'loop':
                object_units = 'Loop'
            else:
                object_units = 'UNKNOWN UNITS'
        else:
            try:
                object_units = self.vip.rpc.call(self.proxy_address, 'simple_read', address, index,
                                            propertylist= ["units"], obj_type=obj_type).get(timeout=10.0)
                if not object_units:
                    object_units = 'UNKNOWN UNITS'
                    pass
                else:
                    object_units=object_units[0]
            except TypeError:
                object_units = 'UNKNOWN UNITS'

            if isinstance(object_units, (int, long)):
                object_units = 'UNKNOWN UNIT ENUM VALUE: ' + str(object_units)

            if obj_type.startswith('analog') or obj_type in (
            'largeAnalogValue', 'integerValue', 'positiveIntegerValue'):
                # Value objects never have a resolution property in practice.
                if not object_notes and not obj_type.endswith('Value'):
                    try:
                        res_value = self.vip.rpc.call(self.proxy_address, 'simple_read', address, index,
                                            propertylist=["resolution"], obj_type=obj_type).get(timeout=10.0)
                        if not res_value:
                            pass
                        else:
                            res_value=res_value[0]
                            object_notes = 'Resolution: {resolution:.6g}'.format(resolution=res_value)
                    except TypeError:
                        pass

                if obj_type not in ('largeAnalogValue', 'integerValue', 'positiveIntegerValue'):
                    try:
                        min_value = self.vip.rpc.call(self.proxy_address, 'simple_read', address, index,
                                            propertylist=["minPresValue"], obj_type=obj_type).get(timeout=10.0)
                        max_value = self.vip.rpc.call(self.proxy_address, 'simple_read', address, index,
                                            propertylist=["maxPresValue"], obj_type=obj_type).get(timeout=10.0)
                        if not min_value:
                            pass
                        else:
                            min_value=int(min_value[0])
                        if not max_value:
                            pass
                        else:
                            max_value=int(max_value[0])
                        has_min = min_value > -max_range_report
                        has_max = max_value < max_range_report

                        if has_min and has_max:
                            object_units_details = '{min:.2f} to {max:.2f}'.format(min=min_value, max=max_value)
                        elif has_min:
                            object_units_details = 'Min: {min:.2f}'.format(min=min_value)
                        elif has_max:
                            object_units_details = 'Max: {max:.2f}'.format(max=max_value)
                        else:
                            object_units_details = 'No limits.'
                            # object_units_details = '{min} to {max}'.format(min=min_value, max=max_value)
                    except Exception as e:

                        #print e
                        pass

                if obj_type != 'analogInput':
                    try:
                        default_value = self.vip.rpc.call(self.proxy_address, 'simple_read', address, index,
                                            propertylist=["relinquishDefault"], obj_type=obj_type).get(timeout=10.0)
                        if not default_value:
                            pass
                        else:
                            default_value=default_value[0]
                            object_units_details += ' (default {default})'.format(default=default_value)
                            object_units_details = object_units_details.strip()
                            # writable = 'TRUE'
                    except Exception:
                        pass

        results = {}
        results['Reference Point Name'] = results['Volttron Point Name'] = object_name
        results['Units'] = object_units
        results['Unit Details'] = object_units_details
        results['BACnet Object Type'] = obj_type
        results['Property'] = 'presentValue'
        results['Writable'] = writable
        results['Index'] = index
        results['Notes'] = object_notes

        # print results
        config_writer.writerow(results)

    def configure_data(self, address, mac):

        try:
            config_path = os.path.dirname(os.path.abspath(__file__))
            config_path = config_path + "/Bacnetdata/"
            device_id=int(mac)
            target_address=address

            filename = str(device_id) + ".csv"
            try:
                Objectlist = ["objectList"]
                result = self.vip.rpc.call(self.proxy_address, 'simple_read', target_address, device_id,
                                           Objectlist).get(timeout=1000.0)
            except TypeError:
                Objectlist = ["structuredObjectList"]
                result = self.vip.rpc.call(self.proxy_address, 'simple_read', target_address, device_id,
                                           Objectlist).get(timeout=10.0)


            print result
            if not result:
                return
            objectlist = result[0]

            with open (config_path+filename, 'wb')as fp:

                config_writer = DictWriter(fp,
                                           ('Reference Point Name',
                                            'Volttron Point Name',
                                            'Units',
                                            'Unit Details',
                                            'BACnet Object Type',
                                            'Property',
                                            'Writable',
                                            'Index',
                                            'Write Priority',
                                            'Notes'))

                config_writer.writeheader()
                for object in objectlist:

                    obj_type= object[0]
                    index=object[1]
                    self.process_object(target_address, obj_type, index, config_writer)
        except Exception as e:
            print e
            return None
        except gevent.Timeout:
            print "objectlist call timeout"
            return None

