

import re
import os
import socket
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.mei_message import *
from pymodbus.other_message import *
import settings
class Modbuscommon():

    def discovery(self):

        device_list = list()
        valid_iphead = False
        try:
            infile = None
            infile = open(settings.PROJECT_DIR+"/machine_ip.txt", "r")
            for line in infile:
                own_ip = line.rstrip()
                own_ip_parts = own_ip.split('.')
                if len(own_ip_parts) == 4:
                    print "Found own IP: " + own_ip
                    iphead = own_ip_parts[0] + '.' + own_ip_parts[1] + '.' + own_ip_parts[2] + '.'
                    valid_iphead = True
                    break
            infile.close()
        except:
            if infile is not None:
                infile.close()
            valid_iphead = False

        if valid_iphead:
            start_ip = 2
            end_ip = 254
            print "Looking for Modbus Devices in the IP range: " + iphead + str(start_ip) + " to " + iphead + str(end_ip)
            _Timeout = 0.2

            ip_index = start_ip
            iprange = list()
            while ip_index <= end_ip:
                iprange.append(iphead + str(ip_index))
                ip_index = ip_index + 1

            #print iprange
            for ip in iprange:
                try:
                    #print ip
                    _socket = None
                    try:
                        _socket = socket.create_connection((ip, 502), _Timeout)
                    except socket.error:
                        if _socket:
                            _socket.close()
                        _socket = None
                    if _socket is not None:
                        _socket.close()
                        client = connection(ip, port=502)
                        client.connect()
                        result2=None
                        possible_subordinate_ids = self.subordinatelist
                        for subordinate_id in possible_subordinate_ids:
                            subordinate_id=int(subordinate_id)
                            result = client.read_device_info(subordinate_id, object_id=0x00)
                            if result is None:
                                result2 = client.read_input_registers(0, 10, unit=subordinate_id)
                                if result2 is None:
                                    result2 = client.read_holding_registers(999, 1, unit=subordinate_id)
                                    if result2 is None:
                                        result2=client.read_discrete_inputs(0,10, unit=subordinate_id)
                                        if result2 is None:
                                            result2 = client.read_coils(0, 10, unit=subordinate_id)
                            if result or result2 is not None:
                              str_Result = str(result)
                              str_Result2=str(result2)
                              try:
                                    match=re.search('Response', str_Result2)
                                    match2 = re.search('IllegalFunction', str_Result)
                                    if match2 or match:
                                        device_list.append(ip + ':' + str(subordinate_id))
                                        continue
                                    else:##reading registers of Result
                                        try:
                                            Vendor=result.information[0]
                                        except:
                                            Vendor="unknown device"
                                        mac=client.read_device_info(subordinate_id, object_id=0x01)
                                        if mac is not None:
                                            mac=mac.information[0]
                                        else:
                                            mac=subordinate_id
                                        ModelName= client.read_device_info(subordinate_id, object_id=0x05)
                                        if ModelName is not None:
                                            ModelName=ModelName.information[0]
                                        else:
                                            ModelName="unknown device"
                                    device_list.append({'address': ip + ':' + str(subordinate_id), 'mac': mac,
                                                        'model': ModelName, 'vendor': Vendor})
                              except Exception as er:
                                     print ("problem with subordinate id " + str(subordinate_id))
                                     print er
                            else:
                                pass
                        client.close()

                except Exception as e:
                    print e
                    pass
            return device_list
        else:
            print "Modbus discovery failed: Couldn't find IP subnet of network!"
        return device_list

    def getDevicedetails(self, subordinate_id):

            deviceinfo = list()
            if subordinate_id == 7:
                macaddress = '30168D000129'
                model='VC1000'
                vendor='Prolon'
            elif subordinate_id == 1:
                macaddress = '30168D000262'
                model = 'VC1000'
                vendor = 'Prolon'
            elif subordinate_id == 2:
                macaddress = '30168D000263'
                model = 'VC1000'
                vendor = 'Prolon'
            elif subordinate_id == 15:
                macaddress = '30168D000130'
                model='M1000'
                vendor='Prolon'
            elif subordinate_id == 20:
                macaddress = '30168D000264'
                model = 'M1000'
                vendor = 'Prolon'
            else:
                macaddress = None
                model="unknown device"
                vendor="unknown device"
            deviceinfo= [macaddress,model,vendor]
            return deviceinfo

class connection(ModbusTcpClient):

    def read_device_info(self,subordinate,object_id):

        request = ReadDeviceInformationRequest(object_id)
        request.unit_id = subordinate
        return self.execute(request)