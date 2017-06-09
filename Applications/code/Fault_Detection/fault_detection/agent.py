
import sys
import json
import logging
from volttron.platform.vip.agent import Agent, Core
from volttron.platform.agent import utils
import datetime
from bemoss_lib.utils import db_helper
import psycopg2
import numpy as np
from sklearn.linear_model import LinearRegression

utils.setup_logging()
_log = logging.getLogger(__name__)
from bemoss_lib.utils.BEMOSSAgent import BEMOSSAgent
from bemoss_lib.utils.BEMOSS_ONTOLOGY import BEMOSS_ONTOLOGY
from bemoss_lib.databases.cassandraAPI import cassandraDB
from bemoss_lib.utils import date_converter
import settings
from scipy import stats
import uuid

class FaultDetectionAgent(BEMOSSAgent):

    #1. agent initialization
    def __init__(self, config_path, **kwargs):
        super(FaultDetectionAgent, self).__init__(**kwargs)
        #1. initialize all agent variables
        config = utils.load_config(config_path)
        self.agent_id = config.get('agent_id','faultdetectionagent')
        self.variables = dict()
        self.enabled = True
        trigger_values = {'temperature_low':60,'temperature_high':85}
        self.data = {'thermostat':'RTH8_1169269','powermeter':'','sensitivity':'low','fault':'No',
                     'weather_agent':settings.weather_agent,'trigger_values':trigger_values, 'temp_low_trigger_enabled':True,
                     'temp_high_trigger_enabled':True,'profile_trigger_enabled':True}

        self.dashboard_view = {"top": None, "center": {"type": "image", "value": 'wattstopper_on.png'},
                               "bottom": BEMOSS_ONTOLOGY.STATUS.NAME}
        self.sensitivity_std_factor = {'low':3,'medium':2,'high':1}
        self.trained = False
        self.notification_variables = dict()
        self.last_fault_time = None
        self.profile_anamoly = False
        self.problems = []
        self.low_temp_anamoly = False
        self.high_temp_anamoly = False
        self.thermostat_nickname = ''
    #2. agent setup method


    @Core.receiver('onsetup')
    def setup(self, sender, **kwargs):
        self.curcon = db_helper.db_connection()
        self.core.periodic(60, self.periodicProcess)
        self.vip.pubsub.subscribe(peer='pubsub', prefix='to/'+self.agent_id+'/update/', callback=self.appUpdate)
        self.updateSettings()

    def updateSettings(self):
        try:
            self.curcon.execute("select app_data from application_running where app_agent_id=%s", (self.agent_id,))
            if self.curcon.rowcount:
                data = self.curcon.fetchone()[0]
                for key, value in data.items():
                    self.data[key] = value
            self.curcon.execute("select nickname from device_info where agent_id=%s",(self.agent_id))
            if self.curcon.rowcount:
                self.thermostat_nickname = self.curcon.fetchone()[0]

        except psycopg2.IntegrityError as er: #Database trouble
            #reconnect first
            self.curcon.database_connect()

    @Core.periodic(60*60*24)
    def daily_training(self):
        self.trained = False
        if self.data['profile_trigger_enabled']:
            self.train_model()

    def current_time(self):
        return datetime.datetime.now()

    def get_time_avg(self,lst_measurement):
        # time, measurement
        prev = lst_measurement[0, :]
        measurements = []
        weights = []
        n = len(lst_measurement)
        for i in range(1, n):
            entry = lst_measurement[i]
            if prev[1] is None and entry[1] is None:
                quantity = 0 #if both of the entry is None, ignore by giving zero value and weight
                weights.append(0)
            elif prev[1] is None:
                quantity = entry[1]
                weights.append(entry[0] - prev[0]) #weight is proportional to time between measurement
            elif entry[1] is None:
                quantity = prev[1]
                weights.append(entry[0] - prev[0]) #weight is proportional to  time between measurement
            else:
                quantity = (prev[1] + entry[1]) / 2
                weights.append(entry[0] - prev[0]) #weight is proportional to time between measurement

            measurements.append(quantity)
            prev = entry

        if np.sum(weights) == 0:
            return None
        else:
            avg_measure = np.sum(np.multiply(weights, measurements)) / np.sum(weights)

        return avg_measure

    def getRate(self,temperature_profile):  # return the avg_outdoor temperature, the liner-fit slop, and std-error of fit
        # for the provided set of timestamp, indoor_temp, outdoor_temp data, setpoint
        slope, intercept, r_value, p_value, std_err = stats.linregress(list(temperature_profile[:, 0] / (1000 * 60 * 60.0)),
                                                                       list(temperature_profile[:, 1]))
        if np.isnan(slope):
            print "Nan"
            return []
        avg_outdoor = self.get_time_avg(temperature_profile[:,[0,2]]) #index 0=>time, index 2=>outdoor_weather
        if avg_outdoor is None:
            return []
        if std_err <= 0.05:
            std_err = 0.05
        return [(avg_outdoor, slope, std_err,temperature_profile[0,0])] #also append the begining time

    def train_model(self):
        end_time = self.current_time()
        start_time = end_time - datetime.timedelta(days=90)

        vars = ['time', 'cool_setpoint', 'heat_setpoint', 'thermostat_mode', 'thermostat_state', 'temperature']
        vars, result = cassandraDB.retrieve(self.data['thermostat'], vars, start_time, end_time,
                                            weather_agent=self.data['weather_agent'])

        if not len(result):
            return

        slope_and_points = self.getSlopesAndPoints(result, vars)

        def train_models(slope_history):
            if len(slope_history) < 3:
                return None
            #slope_histroy = list of tuples: (avg_outdoor, slope, std_err,temperature_profile[0,0])
            sh = np.matrix(slope_history)
            lnmodel = LinearRegression()
            error_inverse = np.array(1/sh[:,2])[:,0]
            lnfit = lnmodel.fit(sh[:,0],sh[:,1])
            #svr_rbf = SVR(kernel='linear', C=10, epsilon=0.5)
            #svrfit = svr_rbf.fit(sh[:, 0], sh[:,1])

            ln_residue = []
            for i in range(len(slope_history)):
                p = lnfit.predict(slope_history[i][0])[0][0]
                ln_residue.append((p - slope_history[i][1])**2)

            ln_std = stats.tstd(ln_residue)

            ln_mean = stats.tmean(ln_residue)
            new_sh = None
            for i in range(len(ln_residue)):
                if ln_residue[i] < ln_mean + 3*ln_std:
                    #sh = np.delete(sh,i,axis=0)
                    if new_sh is None:
                        new_sh = sh[i,:]
                    else:
                        new_sh = np.vstack((new_sh,sh[i,:]))

            sh = new_sh
            #redo the fit
            error_inverse = np.array(1 / sh[:, 2])[:, 0]

            slope_mean = stats.tmean(sh[:,1])
            slope_std = stats.tstd(sh[:,1])

            lnfit = lnmodel.fit(sh[:, 0], sh[:, 1])
            ln_residue = []
            for i in range(len(sh)):
                p = lnfit.predict(sh[i,0])[0][0]
                ln_residue.append((p - sh[i,1]) ** 2)

            ln_std = stats.tstd(ln_residue)
            ln_mean = stats.tmean(ln_residue)

            return {'ln_model':lnfit,'ln_residue':ln_residue,'ln_residue_std':ln_std,'ln_residue_mean':ln_mean,'slope_mean': slope_mean,'slope_std': slope_std,'data_matrix':sh}


        slope_dict = {'heating_model':'heating_slopes','cooling_model':'cooling_slopes','heatoff_model':'heatoff_slopes','cooloff_model':'cooloff_slopes'}

        self.models = dict()
        for key, val in slope_dict.items():
            slope_history = slope_and_points[val]
            if len(slope_history):
                self.models[key] = train_models(slope_history)

        self.trained = True

    def getSlopesAndPoints(self,result,vars):

        modes = ['heating','cooloff','cooling','heatoff']

        heating_points = []  # during forced heating
        cooloff_points = []  # during natural cool down
        cooling_points = []  # during forced cooling
        heatoff_points = []  # during natural heat-up

        heating_slopes = []
        cooling_slopes = []
        heatoff_slopes = []
        cooloff_slopes = []

        oindex = vars.index('weather_temperature')
        prev_row = None
        for row in result:
            heating_done = True
            cooling_done = True
            heatoff_done = True
            cooloff_done = True
            if None in [row[0],row[5],row[oindex]]:
                continue

            if row[3] == 'HEAT':
                heat_setpoint = row[2]
                if heat_setpoint is None:
                    continue

                if heat_setpoint > row[5] + 0.5:  # Heating-On
                    if prev_row is not None and not heating_points and prev_row[2] > row[5]+0.5:
                        heating_points.append([prev_row[0], prev_row[5], prev_row[oindex], prev_row[2]])
                    heating_points.append([row[0], row[5], row[oindex],heat_setpoint])  # time, temperature, outdoor_temperature, heat_setpoint
                    heating_done = False

                if heat_setpoint < row[5] - 0.5:
                    if prev_row is not None and not cooloff_points and prev_row[2] < row[5]-0.5:
                        cooloff_points.append([prev_row[0], prev_row[5], prev_row[oindex], prev_row[2]])
                    cooloff_points.append([row[0], row[5], row[oindex], heat_setpoint])
                    cooloff_done = False

            elif row[3] == 'COOL':
                cool_setpoint = row[1]
                if cool_setpoint is None:
                    continue
                if cool_setpoint < row[5] - 0.5:  # Heating-On
                    if prev_row is not None and not cooling_points and prev_row[2] < row[5]-0.5:
                        cooloff_points.append([prev_row[0], prev_row[5], prev_row[oindex], prev_row[1]])
                    cooling_points.append([row[0], row[5], row[oindex],cool_setpoint])
                    cooling_done = False

                if cool_setpoint > row[5] + 0.5:
                    if prev_row is not None and not heatoff_points and prev_row[2] > row[5]+0.5:
                        heatoff_points.append([prev_row[0], prev_row[5], prev_row[oindex], prev_row[1]])
                    heatoff_points.append([row[0], row[5], row[oindex],cool_setpoint])
                    heatoff_done = False

            if heating_points and heating_done:
                if (heating_points[-1][0] - heating_points[0][0]) / (
                            1000 * 60) > 30:  # make sure there is atleast 10 minute gap
                    heating_slopes += self.getRate(np.array(heating_points))
                heating_points = []

            if cooloff_points and cooloff_done:
                if (cooloff_points[-1][0] - cooloff_points[0][0]) / (1000 * 60) > 30:
                    cooloff_slopes += self.getRate(np.array(cooloff_points))
                cooloff_points = []

            if cooling_points and cooling_done:
                if (cooling_points[-1][0] - cooling_points[0][0]) / (1000 * 60) > 30:
                    cooling_slopes += self.getRate(np.array(cooling_points))
                cooling_points = []

            if heatoff_points and heatoff_done:
                if (heatoff_points[-1][0] - heatoff_points[0][0]) / (1000 * 60) > 30:
                    heatoff_slopes += self.getRate(np.array(heatoff_points))
                heatoff_points = []

            prev_row = row

        return {"heating_points":heating_points,"cooling_points":cooling_points,"heatoff_points":heatoff_points,"cooloff_points":cooloff_points,
                "heating_slopes":heating_slopes,"cooling_slopes":cooling_slopes,"heatoff_slopes":heatoff_slopes,"cooloff_slopes":cooloff_slopes,}



    def check_device_offline(self,device_agent_id):
        self.curcon.execute('select network_status from devicedata where agent_id=%s',(device_agent_id,))
        if self.curcon.rowcount:
            status = self.curcon.fetchone()[0]
            if status == "ONLINE":
                return False
        return True

    @Core.periodic(300)
    def periodicProcess(self):


        current_status = []

        if not self.check_device_offline(self.data['thermostat']):
            if self.data['temp_high_trigger_enabled']:
                if self.check_temp_low():
                    if not self.low_temp_anamoly:
                        self.low_temp_anamoly = True
                        self.add_notification('hvac-fault','Temperature too low.')
                    current_status += ['Temperature too low.']
                else:
                    if self.low_temp_anamoly:
                        self.low_temp_anamoly = False
                        self.add_notification('hvac-fault-cleared','Temperature no longer low.')

            if self.data['temp_high_trigger_enabled']:
                if self.check_temp_high():
                    if not self.high_temp_anamoly:
                        self.high_temp_anamoly = True
                        self.add_notification('hvac-fault','Temperature too high.')
                    current_status += ['Temperature too high.']
                else:
                    if self.high_temp_anamoly:
                        self.high_temp_anamoly = False
                        self.add_notification('hvac-fault-cleared','Temperature no longer high.')


            if self.data['profile_trigger_enabled']:
                anamoly, status = self.check_profile_trigger()
                if anamoly:
                    if not self.profile_anamoly:
                        self.profile_anamoly = True
                        self.add_notification('hvac-fault',  status)
                    current_status += [status]
                else:
                    if self.profile_anamoly:
                        self.profile_anamoly = False
                        self.add_notification('hvac-fault-cleared', 'Fault cleared')
                    current_status +=[status]
        else:
            current_status = ["Thermostat is offline, can't detect fault"]

        self.data['fault'] = ' and '.join(current_status)
        self.updateDB()
        print self.data['fault']

    def check_temp_high(self):
        self.curcon.execute('select data from devicedata where agent_id=%s',(self.data['thermostat'],))
        new_problems = []
        if self.curcon.rowcount:
            data = self.curcon.fetchone()[0]
            upper_limit = self.data['trigger_values']['temperature_high']
            if data[BEMOSS_ONTOLOGY.TEMPERATURE.NAME] > upper_limit:
                return True
        return  False

    def check_temp_low(self):
        self.curcon.execute('select data from devicedata where agent_id=%s',(self.data['thermostat'],))
        new_problems = []
        if self.curcon.rowcount:
            data = self.curcon.fetchone()[0]
            lower_limit = self.data['trigger_values']['temperature_low']
            if data[BEMOSS_ONTOLOGY.TEMPERATURE.NAME] < lower_limit:
                return True
        return False

    def checkAnamoly(self, current_points, model):

        if not (current_points[-1][0] - current_points[0][0]) / (
                    1000 * 60.0) >= 30:  # make sure there is 30 minute worth of data
            raise ValueError('not-enough-data')
        current_slope = self.getRate(np.array(current_points))
        if not current_slope:
            raise ValueError("no-outdoor-temp")
        current_slope = current_slope[0]
        if model in ['cooloff_model', 'cooling_model'] and current_slope[1] > 0:
            return True
        if model in ['heatoff_model', 'heating_model'] and current_slope[1] < 0:
            return True
        if model not in self.models:
            return False

        model = self.models[model]
        if not model:
            raise ValueError('not-enough-historical-data')

        p = model['ln_model'].predict(current_slope[0])[0][0]
        current_ln_residue = (p - current_slope[1]) ** 2

        mean = model['ln_residue_mean']
        std = model['ln_residue_std']
        try:
            factor = self.sensitivity_std_factor[self.data['sensitivity']]
        except KeyError:
            factor = 3


        if abs(
                current_ln_residue) > mean + factor * std:  # we are just checking if the svr_residue is worse than the mean
            if len(model['data_matrix']) >= 5:  # if atleast five (outdoor_temp, slope) has been used to get the model, use model
                return True
            else:
                raise ValueError('not-enough-historical-data')
        else:
            return False

    def checkDeviation(self,temperature_points):
        temperature_points = np.array(temperature_points)
        # temperature_points is a list of list. OuterList[InnerList[time, temperature, outdoor_temperature, setpoint], ...]
        diffs = temperature_points[:,3] - temperature_points[:,1]
        diff_array = np.stack((temperature_points[:, 0], diffs), axis=1)
        avg_diff = self.get_time_avg(diff_array)
        time_diff = (temperature_points[-1,0] - temperature_points[0,0])/(1000*60*60.0) #time difference in hours
        if abs(avg_diff)*time_diff > 9: #Change this 9 degree-hour integrated temperature - setpoint differene if necessary
            return True
        return False

    def check_profile_trigger(self):
        if not self.trained:
            self.train_model()

        vars= ['time','cool_setpoint','heat_setpoint','thermostat_mode','thermostat_state','temperature']

        curtime = self.current_time()
        look_back_time = curtime - datetime.timedelta(hours=24)

        vars, result = cassandraDB.retrieve(self.data['thermostat'],vars,look_back_time,curtime,weather_agent=self.data['weather_agent'])

        slopes_and_points = self.getSlopesAndPoints(result,vars)
        anamoly = False
        current_mode = 'Normal setpoint-following'
        try:
            if slopes_and_points['heating_points']:
                current_mode = 'heating'
                if self.checkAnamoly(slopes_and_points['heating_points'],'heating_model'):
                    anamoly = True
                if self.checkDeviation(slopes_and_points['heating_points']):
                    anamoly = True

            elif slopes_and_points['cooling_points']:
                current_mode = 'cooling'
                if self.checkAnamoly(slopes_and_points['cooling_points'], 'cooling_model'):
                    anamoly = True
                if self.checkDeviation(slopes_and_points['cooling_points']):
                    anamoly = True


            elif slopes_and_points['heatoff_points']:
                current_mode = 'heat-off'
                if self.checkAnamoly(slopes_and_points['heatoff_points'], 'heatoff_model'):
                    anamoly = True

            elif slopes_and_points['cooloff_points']:
                current_mode = 'cool-off'
                if self.checkAnamoly(slopes_and_points['cooloff_points'], 'cooloff_model'):
                    anamoly = True

        except ValueError as er:
            if str(er)=='no-outdoor-temp':
                anamoly = False
                current_mode = "Missing outdoor temperature"
            elif str(er) == 'not-enough-data':
                anamoly = False
                current_mode = "Watching " + current_mode
            elif str(er) == 'not-enough-historical-data':
                anamoly = False
                current_mode = "Watching " + current_mode +". Insufficient historical data"
            else:
                raise

        return  anamoly, current_mode



    def add_notification(self,event, reason):
        self.EventRegister(event,reason=reason,source=self.thermostat_nickname)

    def updateDB(self):

        self.curcon.execute("UPDATE application_running SET app_data=%s, status=%s WHERE app_agent_id=%s",
                            (json.dumps(self.data),"running",self.agent_id))
        self.curcon.commit()


    def appUpdate(self, peer, sender, bus, topic, headers, message):
        old_thermostat = self.data['thermostat']
        self.updateSettings()
        new_thermostat = self.data['thermostat']

        if new_thermostat != old_thermostat:
            self.train_model() #need to retrain model for new thermostat


        topic_list = topic.split('/')
        return_index = topic_list.index('from') + 1
        return_entity = topic_list[return_index]
        if 'thermostat' in message:
            self.variables['data']['thermostat'] = message['thermostat']
        if 'powermeter' in message:
            self.variables['data']['powermeter'] = message['powermeter']
        if 'sensitivity' in message:
            self.variables['data']['sensitivity'] = message['sensitivity']

        self.bemoss_publish('update_response', return_entity, message, headers=headers)


def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    try:
        utils.vip_main(FaultDetectionAgent)
    except Exception as e:
        _log.exception('unhandled exception')

if __name__ == '__main__':
    # Entry point for script
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass