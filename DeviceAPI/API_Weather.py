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
#__created__ = "2014-09-12 12:04:50"
#__lastUpdated__ = "2016-03-14 11:23:33"
'''

'''This API class is for an agent that want to communicate/monitor/control
devices that compatible with Radio Thermostat Wi-Fi USNAP Module API Version 1.3 March 22, 2012
http://www.radiothermostat.com/documents/rtcoawifiapiv1_3.pdf'''

import urllib2
import json
import datetime
from urlparse import urlparse
from DeviceAPI.BaseAPI import baseAPI
from bemoss_lib.protocols.discovery.SSDP import SSDP,parseJSONresponse
from bemoss_lib.utils.BEMOSS_ONTOLOGY import BEMOSS_ONTOLOGY
import pytz
import settings
#from bemoss_lib.databases.cassandraAPI import cassandraDB
import time
class API(baseAPI):
    def __init__(self,**kwargs):
        super(API, self).__init__(**kwargs)
        self.set_variable('connection_renew_interval',6000)
        self.device_supports_auto = False
        self.zipcode = str(settings.zip_code)
        self.key = settings.WUNDERGROUND_KEY
        self._debug = False

    def API_info(self):
        return [{'device_model' : 'BEMOSSWeather', 'vendor_name' : 'BEMOSS', 'communication' : 'cloud',
                'device_type_id' : 4,'api_name': 'API_Weather','html_template':'sensors/bemoss_weather_sensor.html',
                'agent_type':'BasicAgent','identifiable' : False, 'authorizable': False, 'is_cloud_device' : False,
                'schedule_weekday_period' : 4,'schedule_weekend_period' : 4, 'allow_schedule_period_delete' : False,
                'chart_template': 'charts/charts_bemoss_weather_sensor.html','default_monitor_interval':300}]

    def dashboard_view(self):
        return {"top": BEMOSS_ONTOLOGY.RELATIVE_HUMIDITY.NAME, "center": {"type": "number", "value": BEMOSS_ONTOLOGY.TEMPERATURE.NAME},
        "bottom": BEMOSS_ONTOLOGY.SKY_CONDITION.NAME}

    def ontology(self):
        return {"wind_mph": BEMOSS_ONTOLOGY.WIND_VELOCITY, "relative_humidity":BEMOSS_ONTOLOGY.RELATIVE_HUMIDITY,
                "temp_f":BEMOSS_ONTOLOGY.TEMPERATURE,"weather":BEMOSS_ONTOLOGY.SKY_CONDITION,"pressure_in":BEMOSS_ONTOLOGY.PRESSURE}

    def discover(self):

        datestr = datetime.datetime.now().strftime('%Y%m%d')
        self.mac = "WUG"+self.zipcode
        try:
            weather = urllib2.urlopen('http://api.wunderground.com/api/' + self.key + '/history_' + datestr + '/q/CA/' + self.zipcode + '.json')
            weather_data = json.loads(weather.read())
            if not 'error' in weather_data:
                return [{'address': 'http://api.wunderground.com/api/' + self.key + '/history_%s/q/CA/' + self.zipcode + '.json', 'mac': "WUG"+self.zipcode, 'model': "BEMOSSWeather",'vendor': "BEMOSS"}]
            else:
                return {}
        except:
            return {}

    def getModelVendor(self,address):

        return {'model': "BEMOSSWeather",'vendor': "BEMOSS"}

    def getMACAddress(self,address):
        return self.mac

    # GET Open the URL and read the data
    def getDataFromDevice(self):

        _url = "http://api.wunderground.com/api/"+self.key+'/conditions/q/CA/'+self.zipcode+'.json'
        try:
            rs = urllib2.urlopen(_url)
            weather_data = json.loads(rs.read())
            if not 'error' in weather_data and 'current_observation' in weather_data:
                return_data =  weather_data['current_observation']
                return_data['relative_humidity']= return_data['relative_humidity'].replace('%', '')
                return return_data

        except Exception as er:
            print er
            return None


    def getHistoricalData(self,userdatetime):

        datestr = userdatetime.strftime('%Y%m%d')
        _url = 'http://api.wunderground.com/api/' + self.key + '/history_' + datestr + '/q/CA/' + self.zipcode + '.json'
        try:
            rs = urllib2.urlopen(_url)
            weather_data = json.loads(rs.read())
            result = []

            for idx in range(len(weather_data['history']['observations'])):
                utcdate_dict = weather_data['history']['observations'][idx]['utcdate']
                year = int(utcdate_dict['year'])
                month = int(utcdate_dict['mon'])
                day = int(utcdate_dict['mday'])
                hour = int(utcdate_dict['hour'])
                mins = int(utcdate_dict['min'])
                utcdate = datetime.datetime(year,month,day,hour,mins,tzinfo=pytz.UTC)
                temp_f = float(weather_data['history']['observations'][idx]['tempi'])
                try:
                    relative_humidity = float(weather_data['history']['observations'][idx]['hum'])
                except ValueError:
                    relative_humidity = None
                weather = weather_data['history']['observations'][idx]['conds']
                try:
                    pressure_in = float(weather_data['history']['observations'][idx]['pressurei'])
                except ValueError:
                    pressure_in = None
                try:
                    wind_mph = float(weather_data['history']['observations'][idx]['wspdi'])
                except ValueError:
                    wind_mph = None

                dttime = weather_data['history']['observations'][idx]['utcdate']
                result.append({"utcdate":utcdate,"sky_condition":weather,"pressure":pressure_in,"v_wind":wind_mph,
                               "temperature":temp_f,"humidity":relative_humidity})

            return result
        except Exception as er:
            print er
            return None

    def fillHistoricalData(self,startDate,endDate,cassandraDB,log_variables,agent_id):
        d = startDate
        while d < endDate:
            old_data = self.getHistoricalData(d)
            for entry in old_data:

                cassandraDB.insert(agent_id, entry, log_variables, entry['utcdate'])
            time.sleep(10)
            print d
            d = d + datetime.timedelta(days=1)


# This main method will not be executed when this class is used as a module
def main():
    WeatherAPI = API(agent_id='weatheragent22101',address='http://api.wunderground.com/')
    log_variables = {"sky_condition": 'text', "pressure": 'float', "v_wind": 'float', "temperature": 'float',
                     "humidity": 'float'}
    #w = WeatherAPI.getDeviceStatus()
    #WeatherAPI.fillHistoricalData(datetime.datetime(2017,5,11),datetime.datetime(2017,5,23),cassandraDB,log_variables,agent_id=settings.weather_agent)

    #CT50Thermostat.identifyDevice()
    # scheduleData = {'Enabled': True, 'monday':[['Morning', 50, 83, 80],['Day',480, 72, 82],['Evening',960, 71, 84],['Night',1000, 69, 72]], 'tuesday':[['Morning', 360 , 70, 80],['Day',480, 72, 82],['Evening',960, 71, 84],['Night',1000, 69, 72]],'wednesday':[['Morning', 300 , 70, 80],['Day',480, 72, 82],['Evening',960, 71, 84],['Night',1000, 69, 72]],'thursday':[['Morning', 360 , 70, 80],['Day',480, 72, 82],['Evening',960, 71, 84],['Night',1000, 69, 72]],'friday':[['Morning', 360 , 70, 80],['Day',480, 72, 82],['Evening',960, 71, 84],['Night',1000, 69, 72]],'saturday':[['Morning', 360 , 70, 80],['Day',480, 72, 82],['Evening',960, 71, 84],['Night',1000, 69, 72]],'sunday':[['Morning', 360 , 70, 80],['Day',480, 72, 82],['Evening',960, 71, 84],['Night',1000, 69, 72]],}
    # CT50Thermostat.setDeviceSchedule(scheduleData)
    # CT50Thermostat.discover()

if __name__ == "__main__": main()
