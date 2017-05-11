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
#__version__ = "3.5"
#__maintainer__ = "BEMOSS Team"
#__email__ = "aribemoss@gmail.com"
#__website__ = "www.bemoss.org"
#__created__ = "2016-10-16 12:04:50"
#__lastUpdated__ = "2016-10-18 11:23:33"
'''
from gevent.event import AsyncResult

from bemoss_lib.utils.find_own_ip import getIPs
from bacpypes.primitivedata import Null, Atomic, Enumerated, Integer, Unsigned, Real
from bacpypes.constructeddata import Array,  Any, Choice
from bacpypes.debugging import bacpypes_debugging, ModuleLogger
from bacpypes.core import run, stop
from bacpypes.pdu import GlobalBroadcast
from bacpypes.app import LocalDeviceObject, BIPSimpleApplication
from bacpypes.errors import DecodingError
import threading, time, sys
from bacpypes.apdu import WhoIsRequest, IAmRequest, ReadPropertyRequest, ReadPropertyACK,WritePropertyRequest,SimpleAckPDU
from bacpypes.object import get_datatype
from bacpypes.pdu import Address
# some debugging
_debug = True

_log = ModuleLogger(globals())

# globals
this_device = None
this_application = None
#
#   WhoIsIAmApplication
#


try:
    objectlist = ["objectList"]
    result = self.vip.rpc.call(self.proxy_address, 'simple_read', Address, object_instance,
                               objectlist).get(timeout=20.0)
except TypeError:
    objectlist = ["structuredObjectList"]
    result = self.vip.rpc.call(self.proxy_address, 'simple_read', Address, object_instance,
                               objectlist).get(timeout=20.0)
print result
ObjectList = result[0]
type_list = list()
Property_number = list()
for a, b in ObjectList:
    type_list.append(a)
    Property_number.append(b)
print type_list
print Property_number
'''
pointnames = list()
propertylist = ["objectName"]
for i in range(0, len(type_list), 1):
    description = self.vip.rpc.call(self.proxy_address, 'simple_read', Address, Property_number[i],
                                  propertylist, obj_type=type_list[i]).get(timeout=20.0)
    description=description[0]
    pointnames.append(description)
'''


def discover(self):
    device_list = list()
    app, Remote_address, Identifier = self.getinstance()
    print Remote_address, Identifier
    for i in range(0, len(Identifier)):
        Address = Remote_address[i]  # destination address
        object_instance = Identifier[i]
        myproperty = "modelName"
        model = getproperty(app, Address, object_instance, myproperty)
        myproperty = "vendorName"
        vendor = getproperty(app, Address, object_instance, myproperty)
        configurer(app, Identifier[i], Remote_address[i])

        device_list.append({'address': Address, 'mac': object_instance, 'model': model, 'vendor': vendor})
    print device_list
    return device_list


def getinstance(self):
    app, j, q = broadcast()
    return app, j, q

def ImportantPoints(self, Pointlist, modellist, ObjectList):
    indexlist = list()
    neededpoints = list()
    required_objectlist_alldevices = list()
    for i in range(0, len(modellist), 1):  # i specifies which bacnet device
        if modellist[i] == "LMBC-300":
            neededpoints = ['DIMMER-1', 'DIMMER-2', 'WATTAGE-1', 'WATTAGE-2', 'VOLTAGE-1', 'VOLTAGE-2', 'CURRENT-1',
                            'CURRENT-2']
            for element in neededpoints:
                indexlist.append(Pointlist[i].index(element))
            print indexlist
            print ObjectList[i]
            required_objectlist = [ObjectList[i][j] for j in indexlist]
            print required_objectlist
            required_objectlist_alldevices.append(required_objectlist)
        else:
            required_objectlist_alldevices.append(None)
            continue
    return required_objectlist_alldevices


def broadcast():

    try:
        device_list=list()
        localaddress=list()
        ips=getIPs()
        print "found local ip as ", ips
        for ip in ips:
            str(ip)
            localaddress=ip+"/24"

        # make a device object
        this_device = LocalDeviceObject(
            objectName="BEMOSS",
            objectIdentifier=599,   #change if there exists a bacnet device with same identifier
            maxApduLengthAccepted=1024,
            segmentationSupported="segmentedBoth",
            vendorIdentifier=99,
        )

        # Device application
        this_application = Application(this_device, localaddress)

        request = WhoIsRequest()
        request.pduDestination = GlobalBroadcast()

        def time_out():
            time.sleep(5)
            stop()

        thread = threading.Thread(target=time_out)
        thread.start()

        this_application.request(request)
        this_application.found_address=list()
        this_application.found_deviceidentifier=list()
        run()
        #time.sleep(10)
        this_application.release=True
        this_application.update=False
        address,deviceidentifier=this_application.updator()

        todelete=list()
        for i in range(0,len(deviceidentifier)):
            if deviceidentifier[i]==0:
                todelete.append(i)
        for i in todelete:
            del address[i],deviceidentifier[i]   #Deleting identified bacnet router
        Remote_address=list(set(address))      #Removing repeatition
        Identifier=list(set(deviceidentifier))  #Removing repeatition

        print "destination address list is " , Remote_address
        print "object instance of that address" , Identifier

        return this_application,Remote_address,Identifier
    except Exception, e:
        _log.exception("an error has occurred: %s", e)
        return None


def getproperty(this_application,Remote_address, Identifier, property,type="device"):

                    try:
                           ''' def read_prop(app, address, obj_type, obj_inst, prop_id, index=None):'''

                           value = read_prop(this_application, Remote_address, type, Identifier, "units")
                           return value

                    except Exception as e:
                            print e
#j=write_property("2001:127", 1, "binaryOutput", 1, "presentValue")

@bacpypes_debugging
class Application(BIPSimpleApplication):

    def __init__(self, *args):
        if _debug: Application._debug("__init__ %r", args)
        BIPSimpleApplication.__init__(self, *args)
        # keep track of requests to line up responses
        self._request = None
        self.expect_confirmation = True

    def confirmation(self, apdu):
        self.apdu = apdu
        stop()

    def make_request(self, request, expected_device_id=None):
        self.expected_device_id = expected_device_id
        self._request = request
        self.request(request)
        run()
        return self.apdu

    def request(self, apdu):
        if _debug: Application._debug("request %r", apdu)

        # save a copy of the request
        self._request = apdu

        # forward it along
        BIPSimpleApplication.request(self, apdu)


    def indication(self,apdu):

        self.apdu = apdu
        if (isinstance(self._request, WhoIsRequest)) and (isinstance(apdu, IAmRequest)):
            device_type, device_instance = apdu.iAmDeviceIdentifier
            self.device_instance = device_instance
            if device_type != 'device':
                raise DecodingError("invalid object type")
        self.release=False
        self.update=True
        self.updator()


    def updator(self):

        apdu=self.apdu
        Remotestation=apdu.pduSource
        StationIdentifier=self.device_instance

        self.found_address.append(Remotestation)
        self.found_deviceidentifier.append(StationIdentifier)

        if self.release==True:
            return (self.found_address,self.found_deviceidentifier)



def read_prop(app, address, obj_type, obj_inst, prop_id, index=None):
    request = ReadPropertyRequest(
        objectIdentifier=(obj_type, obj_inst),
        propertyIdentifier=prop_id,
        propertyArrayIndex=index)
    request.pduDestination = address

    result = app.make_request(request)
    if not isinstance(result, ReadPropertyACK):
        result.debug_contents(file=sys.stderr)
        raise TypeError("Error reading property")

    # find the datatype
    datatype = get_datatype(obj_type, prop_id)
    if issubclass(datatype, Array) and (result.propertyArrayIndex is not None):
        if result.propertyArrayIndex == 0:
            value = result.propertyValue.cast_out(Unsigned)
        else:
            value = result.propertyValue.cast_out(datatype.subtype)
    else:
        value = result.propertyValue.cast_out(datatype)

    return value

class IOCB:
    def __init__(self, request, asynccall):
        # requests and responses
        self.ioRequest = request
        self.ioResult = AsyncResult()
        self.ioCall = asynccall

    def set(self, value):
        self.ioCall.send(None, self.ioResult.set, value)

    def set_exception(self, exception):
        self.ioCall.send(None, self.ioResult.set_exception, exception)



def write_property(self,target_address, value, object_type, instance_number, property_name, priority=None, index=None):
    """Write to a property."""


    request = WritePropertyRequest(
        objectIdentifier=(object_type, instance_number),
        propertyIdentifier=property_name)

    datatype = get_datatype(object_type, property_name)
    if (value is None or value == 'null'):
        bac_value = Null()
    elif issubclass(datatype, Atomic):
        if datatype is Integer:
            value = int(value)
        elif datatype is Real:
            value = float(value)
        elif datatype is Unsigned:
            value = int(value)
        bac_value = datatype(value)
    elif issubclass(datatype, Array) and (index is not None):
        if index == 0:
            bac_value = Integer(value)
        elif issubclass(datatype.subtype, Atomic):
            bac_value = datatype.subtype(value)
        elif not isinstance(value, datatype.subtype):
            raise TypeError("invalid result datatype, expecting %s" % (datatype.subtype.__name__,))
    elif not isinstance(value, datatype):
        raise TypeError("invalid result datatype, expecting %s" % (datatype.__name__,))

    request.propertyValue = Any()
    request.propertyValue.cast_in(bac_value)

    request.pduDestination = Address(target_address)

    # Optional index
    if index is not None:
        request.propertyArrayIndex = index

    # Optional priority
    if priority is not None:
        request.priority = priority

    iocb = IOCB(request, AsyncCall())
    self.this_application.submit_request(iocb)
    result = iocb.ioResult.wait()
    if isinstance(result, SimpleAckPDU):
        return value
    raise RuntimeError("Failed to set value: " + str(result))


#k= write_property("2001:127", 1, "binaryOutput", 1, "presentValue", priority=None, index=None)