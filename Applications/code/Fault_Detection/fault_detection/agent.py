
import sys
import json
import logging
from volttron.platform.vip.agent import Agent, Core
from volttron.platform.agent import utils
from volttron.platform.messaging import headers as headers_mod
import time
import datetime
import settings
from bemoss_lib.utils import db_helper
import psycopg2
import numpy as np
from sklearn.svm import SVR
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

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

        self.data = {'thermostat':'RTH8_1169269','powermeter':'','sensitivity':'low','fault':'No','weather_agent':settings.weather_agent}

        self.dashboard_view = {"top": None, "center": {"type": "image", "value": 'wattstopper_on.png'},
                               "bottom": BEMOSS_ONTOLOGY.STATUS.NAME}
        self.sensitivity_std_factor = {'low':1,'medium':2,'high':3}
        self.trained = False
        self.notification_variables = dict()
        self.last_fault_time = None
        self.anamoly = False
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
        except psycopg2.IntegrityError as er: #Database trouble
            #reconnect first
            self.curcon.database_connect()

    @Core.periodic(60*60*24)
    def daily_training(self):
        self.train_model()

    def current_time(self):
        return datetime.datetime.now()

    def getRate(self,temperature_profile):  # return the avg_outdoor temperature, the liner-fit slop, and std-error of fit
        # for the provided set of timestamp, indoor_temp, outdoor_temp data
        slope, intercept, r_value, p_value, std_err = stats.linregress(list(temperature_profile[:, 0] / (1000 * 60 * 60)),
                                                                       list(temperature_profile[:, 1]))
        prev = temperature_profile[0, :]
        temps = []
        weights = []
        n = temperature_profile.shape[0]
        for i in range(1, n):
            entry = temperature_profile[i]

            if prev[2] is None and entry[2] is None:
                temp =0
                weights.append(0)
            elif prev[2] is None:
                temp = entry[2]
                weights.append(entry[0] - prev[0])
            elif entry[2] is None:
                temp = prev[2]
                weights.append(entry[0] - prev[0])
            else:
                temp = (prev[2] + entry[2]) / 2
                weights.append(entry[0] - prev[0])
            temps.append(temp)
            prev = entry

        if np.sum(weights) == 0:
            return []
        else:
            avg_outdoor = np.sum(np.multiply(weights, temps)) / np.sum(weights)
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
            for i in range(len(ln_residue)):
                if ln_residue[i] > ln_mean + 1.5*ln_std:
                    sh = np.delete(sh,i,axis=0)

            #redo the fit
            error_inverse = np.array(1 / sh[:, 2])[:, 0]
            lnfit = lnmodel.fit(sh[:, 0], sh[:, 1])
            ln_residue = []
            for i in range(len(sh)):
                p = lnfit.predict(sh[i,0])[0][0]
                ln_residue.append((p - sh[i,1]) ** 2)

            ln_std = stats.tstd(ln_residue)
            ln_mean = stats.tmean(ln_residue)

            return {'ln_model':lnfit,'ln_residue':ln_residue,'ln_residue_std':ln_std,'ln_residue_mean':ln_mean,'data_matrix':sh}


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
            if row[3] == 'HEAT':
                heat_setpoint = row[2]
                if heat_setpoint > row[5] + 0.5:  # Heating-On
                    if prev_row is not None and not heating_points and prev_row[2] > row[5]+0.5:
                        heating_points.append([prev_row[0], prev_row[5], prev_row[oindex], prev_row[2]])
                    heating_points.append([row[0], row[5], row[oindex],heat_setpoint])  # time temperature, outdoor_temperature, heat_setpoint
                    heating_done = False

                if heat_setpoint < row[5] - 0.5:
                    if prev_row is not None and not cooloff_points and prev_row[2] < row[5]-0.5:
                        cooloff_points.append([prev_row[0], prev_row[5], prev_row[oindex], prev_row[2]])
                    cooloff_points.append([row[0], row[5], row[oindex], heat_setpoint])
                    cooloff_done = False

            elif row[3] == 'COOL':
                cool_setpoint = row[1]
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

    @Core.periodic(300)
    def periodicProcess(self):
        if not self.trained:
            self.train_model()

        vars= ['time','cool_setpoint','heat_setpoint','thermostat_mode','thermostat_state','temperature']

        curtime = self.current_time()
        look_back_time = curtime - datetime.timedelta(hours=24)

        vars, result = cassandraDB.retrieve(self.data['thermostat'],vars,look_back_time,curtime,weather_agent=self.data['weather_agent'])

        slopes_and_points = self.getSlopesAndPoints(result,vars)

        def checkAnamoly(current_points,model):

            if not (current_points[-1][0] - current_points[0][0]) / (
                        1000 * 60) > 30:  # make sure there is 10 minute worth of data
                raise ValueError('not-enough-data')

            current_slope = self.getRate(np.array(current_points))
            if not current_slope:
                raise ValueError("no-outdoor-temp")
            current_slope = current_slope[0]
            if model in ['cooloff_model','cooling_model'] and current_slope[1] > 0:
                return True
            if model in ['heatoff_model','heating_model'] and current_slope[1] < 0:
                return True
            if model not in self.models:
                return False

            model = self.models[model]
            p = model['ln_model'].predict(current_slope[0])[0][0]
            current_ln_residue = (p - current_slope[1])**2


            mean = model['ln_residue_mean']
            std = model['ln_residue_std']
            try:
                factor = self.sensitivity_std_factor[self.data['sensitivity']]
            except KeyError:
                factor = 3

            if abs(current_ln_residue) > mean + factor*std: #we are just checking if the svr_residue is worse than the mean
                return True
            else:
                return False

        anamoly = False
        current_mode = 'setpoint-following'
        try:
            if slopes_and_points['heating_points']:
                current_mode = 'heating'
                if checkAnamoly(slopes_and_points['heating_points'],'heating_model'):
                    anamoly = True

            elif slopes_and_points['cooling_points']:
                current_mode = 'cooling'
                if checkAnamoly(slopes_and_points['cooling_points'], 'cooling_model'):
                    anamoly = True

            elif slopes_and_points['heatoff_points']:
                current_mode = 'heat-off'
                if checkAnamoly(slopes_and_points['heatoff_points'], 'heatoff_model'):
                    anamoly = True

            elif slopes_and_points['cooloff_points']:
                current_mode = 'cool-off'
                if checkAnamoly(slopes_and_points['cooloff_points'], 'cooloff_model'):
                    anamoly = True

        except ValueError as er:
            if str(er)=='no-outdoor-temp':
                anamoly = True
                current_mode = "Missing outdoor temperature"
            elif str(er) == 'not-enough-data':
                anamoly = False
                current_mode = "Watching " + current_mode
            else:
                raise

        if not anamoly and self.anamoly: #The anamoly just got cleared
            self.add_notification('hvac-fault_cleared','fault cleared')

        self.anamoly=anamoly
        if anamoly:
            fault_type = "Abnormal " + current_mode
            self.add_notification('hvac-fault', fault_type)
            print "Anamoly Detected"
            self.data['fault'] = fault_type + " fault."
        else:
            print "No anamoly"
            self.data['fault'] = "Normal " + current_mode

        self.updateDB()

    def add_notification(self,event, reason):

        if event == 'hvac-fault':
            if self.last_fault_time is not None and datetime.datetime.now() - self.last_fault_time < datetime.timedelta(hours=12):
                return
            self.last_fault_time = datetime.datetime.now()

        temp = uuid.uuid4()
        self.notification_variables['date_id'] = str(datetime.datetime.now().date())
        self.notification_variables['time'] = datetime.datetime.utcnow()
        self.notification_variables['event_id'] = temp
        self.notification_variables['agent_id'] = self.agent_id
        self.notification_variables['event'] = event
        self.notification_variables['reason'] = reason
        self.notification_variables['related_to'] = None
        self.offline_id = temp
        self.notification_variables['logged_time'] = datetime.datetime.utcnow()
        not_vars = {'date_id': 'text', 'logged_time': 'TIMESTAMP', 'agent_id': 'text', 'event_id': 'UUID', 'time': 'TIMESTAMP',
         'event': 'text', 'reason': 'text', 'related_to': 'UUID', 'logged_by': 'text', 'node_name': 'text'}
        cassandraDB.customInsert(all_vars=self.notification_variables, log_vars=not_vars,
                                 tablename="offline_events")

        time = date_converter.UTCToLocal(datetime.datetime.utcnow())
        message = str(self.agent_id) + ': ' + event + '. Reason: '+ reason
        self.curcon.execute("select id from possible_events where event_name=%s", (event,))
        event_id = self.curcon.fetchone()[0]
        self.curcon.execute(
            "insert into notification (dt_triggered, seen, event_type_id, message) VALUES (%s, %s, %s, %s)",
            (time, False, event_id, message))
        self.curcon.commit()

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