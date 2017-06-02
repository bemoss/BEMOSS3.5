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
#__created__ = "2016-09-21"
#__lastUpdated__ = "2016-09-21"
'''


class BEMOSS_ONTOLOGY:
    class COOL_SETPOINT:
        NAME = 'cool_setpoint'
        TYPE = 'double'
        UNIT = 'F'
        ALTERNATE_NAMES = ['t_cool','coolTo']
        SPOKEN_NAMES = ['cooling set point','cool setpoint']

    class HEAT_SETPOINT:
        NAME = 'heat_setpoint'
        TYPE = 'double'
        UNIT = 'F'
        ALTERNATE_NAMES = ['t_heat','heatTo']
        SPOKEN_NAMES = ['heat set point', 'heating set point','heat setpoint']

    class SETPOINT:
        NAME = 'setpoint'
        TYPE = 'double'
        UNIT = 'F'
        ALTERNATE_NAMES = []
        SPOKEN_NAMES = ['set point']

    class TEMPERATURE:
        NAME = 'temperature'
        TYPE = 'double'
        UNIT = 'F'
        ALTERNATE_NAMES = ['temp']


    class MAX_TEMPERATURE:
        NAME = 'max_temperature'
        TYPE = 'double'
        UNIT = 'F'
        ALTERNATE_NAMES = ['max_temp']
        SPOKEN_NAMES = ['max temperature','maximum temperature']

    class MIN_TEMPERATURE:
        NAME = 'min_temperature'
        TYPE = 'double'
        UNIT = 'F'
        ALTERNATE_NAMES = ['min_temp']
        SPOKEN_NAMES = ['min temperature', 'minimum temperature']

    class THERMOSTAT_MODE:
        NAME = 'thermostat_mode'
        TYPE = 'text'
        UNIT = None
        class POSSIBLE_VALUES:
            COOL = 'COOL'
            HEAT = 'HEAT'
            AUTO = 'AUTO'
            OFF = 'OFF'
        ALTERNATE_NAMES = ['tmode']
        SPOKEN_NAMES = ['thermostat mode','mode']


    class BEMOSS_MODE:
        NAME = 'bemoss_mode'
        TYPE = 'text'
        UNIT = None
        class POSSIBLE_VALUES:
            COOL = 'COOL'
            HEAT = 'HEAT'
            AUTO = 'AUTO'
            OFF = 'OFF'
        ALTERNATE_NAMES = []
        SPOKEN_NAMES = ['bemoss mode']

    class FAN_MODE:
        NAME = 'fan_mode'
        TYPE = 'text'
        UNIT = None
        class POSSIBLE_VALUES:
            AUTO = 'AUTO'
            CIRCULATE = 'CIRCULATE'
            ON = 'ON'
        ALTERNATE_NAMES = ['fmode']
        SPOKEN_NAMES = ['fan mode']

    class THERMOSTAT_STATE:
        NAME = 'thermostat_state'
        TYPE = 'text'
        UNIT = None
        class POSSIBLE_VALUES:
            COOL = 'COOL'
            HEAT = 'HEAT'
            OFF = 'OFF'
        ALTERNATE_NAMES = ['tstate']
        SPOKEN_NAMES = ['thermostat state']

    class THERMOSTAT_HEATSTATUS:
        # variable used by Honeywell thermostat, similar with HOLD
        NAME = 'status_heat'
        TYPE = 'text'
        UNIT = None
        class POSSIBLE_VALUES:
            NONE = 'NONE'
            TEMPORARY = 'TEMPORARY'
            PERMANENT = 'PERMANENT'

    class THERMOSTAT_COOLSTATUS:
        # variable used by Honeywell thermostat, similar with HOLD
        NAME = 'status_cool'
        TYPE = 'text'
        UNIT = None
        class POSSIBLE_VALUES:
            NONE = 'NONE'
            TEMPORARY = 'TEMPORARY'
            PERMANENT = 'PERMANENT'

    class FAN_STATE:
        NAME = 'fan_state'
        TYPE = 'text'
        UNIT = None
        class POSSIBLE_VALUES:
            ON = 'ON'
            OFF = 'OFF'
        ALTERNATE_NAMES = ['fstate']
        SPOKEN_NAMES = ['fan state']

    class HOLD:
        NAME = 'hold'
        TYPE = 'text'
        UNIT = None
        class POSSIBLE_VALUES:
            NONE = 'NONE'
            TEMPORARY = 'TEMPORARY'
            PERMANENT = 'PERMANENT'
        ALTERNATE_NAMES = ['t_hold']

    class BATTERY:
        NAME = 'soc'
        TYPE = 'double'
        UNIT = '%'
        class POSSIBLE_VALUES:
            MIN = 0
            MAX = 100
        ALTERNATE_NAMES = ['soc']
        SPOKEN_NAMES = ['state of charge']

    class SKY_CONDITION:
        NAME = "sky_condition"
        TYPE = "text"

    class STATUS:
        NAME = 'status'
        TYPE = 'text'
        UNIT = None
        class POSSIBLE_VALUES:
            ON = 'ON'
            OFF = 'OFF'

        ALTERNATE_NAMES = []
        POSSIBLE_SPOKEN_VALUES = {POSSIBLE_VALUES.ON: ['on','1',1,'active','open'],
                               POSSIBLE_VALUES.OFF: ['off','0',0,'inactive','close'] }

    class BRIGHTNESS:
        NAME = 'brightness'
        TYPE = 'double'
        UNIT = '%'
        class POSSIBLE_VALUES:
            MIN = 0
            MAX = 100
        ALTERNATE_NAMES = []
        POSSIBLE_SPOKEN_VALUES = {POSSIBLE_VALUES.MIN: ['minimum','zero',0,'off','zero percent'],
                                  POSSIBLE_VALUES.MAX: ['full', 'maximum', 100, 'hundred', 'hundred percent']}

    class HEXCOLOR:
        NAME = 'hexcolor'
        TYPE = 'text'
        UNIT = None
        ALTERNATE_NAMES = []

    class COLOR:
        NAME = 'color'
        TYPE = 'text'
        UNIT = None
        ALTERNATE_NAMES = []

    class POWER:
        NAME = 'power'
        TYPE = 'double'
        UNIT = 'W'
        ALTERNATE_NAMES = []

    class ENERGY:
        NAME = 'energy'
        TYPE = 'double'
        UNIT = 'kWh'
        ALTERNATE_NAMES = []

    class DAMPER:
        NAME = 'bypass_damper_position'
        TYPE ='int'
        UNIT =None
        ALTERNATE_NAMES = []

    class COOLING:
        NAME = 'cooling_mode'
        TYPE ="text"
        UNIT =None
        ALTERNATE_NAMES = []

    class SUPPLY_TEMPERATURE:
        NAME = 'supply_temperature'
        TYPE ='float'
        UNIT ='F'
        ALTERNATE_NAMES = []

    class HEATING:
        NAME = 'heating_level'
        TYPE ='float'
        UNIT = '%'
        ALTERNATE_NAMES = []

    class RETURN_TEMPERATURE:
        NAME = 'return_temperature'
        TYPE ='float'
        UNIT ='F'
        ALTERNATE_NAMES = []

    class PRESSURE:
        NAME = 'pressure'
        TYPE ='float'
        UNIT =None
        ALTERNATE_NAMES = []

    class COOLING_STATUS:
        NAME = 'cooling_status'
        TYPE = 'text'
        UNIT = None
        ALTERNATE_NAMES = []

    class OUTSIDE_DAMPER:
        NAME = 'outside_damper_position'
        TYPE = 'int'
        UNIT = None
        ALTERNATE_NAMES = []

    class OUTSIDE_TEMPERATURE:
        NAME='outside_temperature'
        TYPE ='float'
        UNIT = 'F'
        ALTERNATE_NAMES = []

    class MAX_OUTSIDE_TEMPERATURE:
        NAME = 'max_outside_temperature'
        TYPE = 'float'
        UNIT = 'F'
        ALTERNATE_NAMES = []
        SPOKEN_NAMES = ['maximum outside temperature']

    class MIN_OUTSIDE_TEMPERATURE:
        NAME = 'min_outside_temperature'
        TYPE = 'float'
        UNIT = 'F'
        ALTERNATE_NAMES = []
        SPOKEN_NAMES = ['minimum outside temperature']

    class CO2:
        NAME = 'co2'
        TYPE = 'float'
        UNIT = 'ppm'
        ALTERNATE_NAMES = ['Carbondioxide']
        SPOKEN_NAMES = ['carbon dioxide','carbon dioxide level']

    class NOISE:
        NAME = 'noise'
        TYPE = 'float'
        UNIT = 'db'
        ALTERNATE_NAMES = ['']
        SPOKEN_NAMES = ['noise level']

    class RELATIVE_HUMIDITY:
        NAME = 'humidity'
        TYPE = 'float'
        UNIT = '%'
        ALTERNATE_NAMES = ['']

    class OUTSIDE_HUMIDITY:
        NAME = 'outside_humidity'
        TYPE = 'float'
        UNIT = '%'
        ALTERNATE_NAMES = ['']

    class ANTI_TAMPERING:
        NAME = 'anti_tampering'
        TYPE = 'text'
        Unit = None
        class POSSIBLE_VALUES:
            ENABLED = 'ENABLED'
            DISABLED = 'DISABLED'

    class FLAP:
        NAME = 'flap_position'
        TYPE = 'int'
        UNIT = None
        ALTERNATE_NAMES = []

    class OVERRIDE:
        NAME = 'override'
        TYPE = 'text'
        UNIT = None
        class POSSIBLE_VALUES:
            ON = 'ON'
            OFF = 'OFF'

    class VOLTAGE:
        NAME = 'voltage'
        TYPE = 'float'
        UNIT = "Volts"
        ALTERNATE_NAMES = []

    class CURRENT:
        NAME = 'current'
        TYPE = 'float'
        UNIT = "Amp"
        ALTERNATE_NAMES = []

    class ILLUMINATION:

        NAME = 'illumination'
        TYPE = 'double'
        UNIT = 'lux'
        ALTERNATE_NAMES = []

    class FREQUENCY:
        NAME = 'frequency'
        TYPE = 'double'
        UNIT = 'Hz'
        ALTERNATE_NAMES = []

    class DOOR:
        NAME = 'door'
        TYPE = 'text'
        UNIT = None
        class POSSIBLE_VALUES:
            OPEN = 'OPEN'
            CLOSE = 'CLOSED'

    class OCCUPIED:
        NAME = 'occupied'
        TYPE = 'text'
        UNIT = None

        class POSSIBLE_VALUES:
            ON = 'OCCUPIED'
            OFF = 'UNOCCUPIED'

        ALTERNATE_NAMES = []

    class POWER_L1:
        NAME = 'power_a'
        TYPE = 'double'
        UNIT = 'W'
        ALTERNATE_NAMES = []
        SPOKEN_NAMES = ['phase A power','Line one power']

    class POWER_L2:
        NAME = 'power_b'
        TYPE = 'double'
        UNIT = 'W'
        ALTERNATE_NAMES = []
        SPOKEN_NAMES = ['phase B power', 'Line two power']

    class POWER_L3:
        NAME = 'power_c'
        TYPE = 'double'
        UNIT = 'W'
        ALTERNATE_NAMES = []
        SPOKEN_NAMES = ['phase C power', 'Line three power']

    class VOLTAGE_L1:
        NAME = 'voltage_a'
        TYPE = 'float'
        UNIT = "Volts"
        ALTERNATE_NAMES = []
        SPOKEN_NAMES = ['phase A voltage', 'Line one voltage']

    class VOLTAGE_L2:
        NAME = 'voltage_b'
        TYPE = 'float'
        UNIT = "Volts"
        ALTERNATE_NAMES = []
        SPOKEN_NAMES = ['phase B voltage', 'Line two voltage']

    class VOLTAGE_L3:
        NAME = 'voltage_c'
        TYPE = 'float'
        UNIT = "Volts"
        ALTERNATE_NAMES = []
        SPOKEN_NAMES = ['phase C voltage', 'Line three voltage']

    class POWERFACTOR_L1:
        NAME = 'powerfactor_a'
        TYPE = 'float'
        UNIT = None
        ALTERNATE_NAMES = []
        SPOKEN_NAMES = ['phase A power factor', 'Line one power factor']

    class POWERFACTOR_L3:
        NAME = 'powerfactor_c'
        TYPE = 'float'
        UNIT = None
        ALTERNATE_NAMES = []
        SPOKEN_NAMES = ['phase B power factor', 'Line two power factor']


    class POWERFACTOR_L2:
        NAME = 'powerfactor_b'
        TYPE = 'float'
        UNIT = None
        ALTERNATE_NAMES = []
        SPOKEN_NAMES = ['phase C power factor', 'Line three power factor']

    class POWERFACTOR:
        NAME = 'powerfactor'
        TYPE = 'float'
        UNIT = None
        ALTERNATE_NAMES = []

    class REACTIVE_POWER:
        NAME = 'reac_power'
        TYPE = 'double'
        UNIT = 'W'
        ALTERNATE_NAMES = []
        SPOKEN_NAMES = ['reactive power']

    class APPARANT_POWER:
        NAME = 'appar_power'
        TYPE = 'double'
        UNIT = 'W'
        ALTERNATE_NAMES = []
        SPOKEN_NAMES = ['apparent power']

    class CURRENT_L1:
        NAME = 'current_a'
        TYPE = 'float'
        UNIT = "Amp"
        ALTERNATE_NAMES = []
        SPOKEN_NAMES = ['phase A current', 'Line one current']

    class CURRENT_L2:
        NAME = 'current_b'
        TYPE = 'float'
        UNIT = "Amp"
        ALTERNATE_NAMES = []
        SPOKEN_NAMES = ['phase B current', 'Line two current']

    class CURRENT_L3:
        NAME = 'current_c'
        TYPE = 'float'
        UNIT = "Amp"
        ALTERNATE_NAMES = []
        SPOKEN_NAMES = ['phase C current', 'Line three current']

    class REACTIVE_POWER_L1:
        NAME = 'reac_power_a'
        TYPE = 'double'
        UNIT = 'W'
        ALTERNATE_NAMES = []

    class REACTIVE_POWER_L2:
        NAME = 'reac_power_b'
        TYPE = 'double'
        UNIT = 'W'
        ALTERNATE_NAMES = []

    class REACTIVE_POWER_L3:
        NAME = 'reac_power_c'
        TYPE = 'double'
        UNIT = 'W'
        ALTERNATE_NAMES = []

    class APPARANT_POWER_L1:
        NAME = 'appar_power_a'
        TYPE = 'double'
        UNIT = 'W'
        ALTERNATE_NAMES = []

    class APPARANT_POWER_L2:
        NAME = 'appar_power_b'
        TYPE = 'double'
        UNIT = 'W'
        ALTERNATE_NAMES = []

    class APPARANT_POWER_L3:
        NAME = 'appar_power_c'
        TYPE = 'double'
        UNIT = 'W'
        ALTERNATE_NAMES = []

    class VOLTAGE_DC:
        NAME = 'vdc'
        TYPE = 'double'
        UNIT = 'V'
        ALTERNATE_NAME = ['Vpv']
        SPOKEN_NAMES = ['dc voltage', 'd.c. voltage']

    class CURRENT_DC:
        NAME = 'idc'
        TYPE = 'double'
        UNIT = 'A'
        ALTERNATE_NAME = ['Ipv']
        SPOKEN_NAMES = ['dc current', 'd.c. current']

    class VOLTAGE_AC:
        NAME = 'vac'
        TYPE = 'double'
        UNIT = 'V'
        ALTERNATE_NAME = ['Vac']
        SPOKEN_NAMES = ['ac voltage', 'a.c. voltage']

    class CURRENT_AC:
        NAME = 'iac'
        TYPE = 'double'
        UNIT = 'A'
        ALTERNATE_NAME = ['Iac']
        SPOKEN_NAMES = ['ac current', 'a.c. current']

    class POWER_DC:
        NAME = 'power_dc'
        TYPE = 'double'
        UNIT = 'W'
        SPOKEN_NAMES = ['dc power', 'd.c. power']

    class POWER_AC:
        NAME = 'power_ac'
        TYPE = 'double'
        UNIT = 'W'
        SPOKEN_NAMES = ['ac power', 'a.c. power']

    class ARRAY_IRRADIANCE:
        NAME = 'irradiance_array'
        TYPE = 'double'
        UNIT = 'W/m2'
        SPOKEN_NAMES = ['array irradiance']


    class HORIZONTAL_IRRADIANCE:
        NAME = 'irradiance_horizontal'
        TYPE = 'double'
        UNIT = 'W/m2'
        SPOKEN_NAMES = ['horizonatal irradiance']

    class MODULE_TEMPERATURE:
        NAME = 'temp_module'
        TYPE = 'double'
        UNIT = 'F'
        SPOKEN_NAMES = ['module temperature']

    class AMBIENT_TEMPERATURE:
        NAME = 'temp_ambient'
        TYPE = 'double'
        UNIT = 'F'
        SPOKEN_NAMES = ['ambient temperature']

    class WIND_VELOCITY:
        NAME = 'v_wind'
        TYPE = 'double'
        UNIT = 'm/s'
        SPOKEN_NAMES = ['wind velocity']

    class ENERGY_TOTAL:
        NAME = 'energy_total'
        TYPE = 'double'
        UNIT = 'MWh'
        SPOKEN_NAMES = ['total energy']

    class ENERGY_DAY:
        NAME = 'energy_day'
        TYPE = 'double'
        UNIT = 'kWh'
        SPOKEN_NAMES = ['daily energy']

    class INCIDENT_POWER:
        NAME = 'power_incident'
        TYPE = 'double'
        UNIT = 'W'
        SPOKEN_NAMES = ['incident power','incident solar power']

    class SOLAR_EFFICIENCY:
        NAME = 'efficiency_solar'
        TYPE = 'double'
        UNIT = '%'
        SPOKEN_NAMES = ['solar efficiency']

    class INVERTER_EFFICIENCY:
        NAME = 'efficiency_inverter'
        TYPE = 'double'
        UNIT = '%'
        SPOKEN_NAMES = ['inverter efficiency']

    class TOTAL_EFFICIENCY:
        NAME = 'efficiency_total'
        TYPE = 'double'
        UNIT = '%'
        SPOKEN_NAMES = ['total efficiency']

    class CO2_SAVED:
        NAME = 'co2_saved'
        TYPE = 'double'
        UNIT = 'lbs'
        SPOKEN_NAMES = ['carbon dioxide saved', 'saved carbon dioxide']



    class VALVE_RELATIVE_POSITION:
        NAME = 'rel_position'
        TYPE = 'int'
        UNIT = '%'
        ALTERNATE_NAMES = []

    class VALVE_ABS_POSITION:
        NAME = 'abs_position'
        TYPE = 'double'
        UNIT = 'degree'
        ALTERNATE_NAMES = []

    class VALVE_SETPOINT:
        NAME = 'val_setpoint'
        TYPE = 'double'
        UNIT = 'F'
        ALTERNATE_NAMES = []

    class DIFF_TEMPERATURE:
        NAME = 'diff_temp'
        TYPE = 'double'
        UNIT = 'F'
        ALTERNATE_NAMES = []

    class VAV_MODE:
        NAME = 'vav_mode'
        TYPE = 'int'
        UNIT = None
        ALTERNATE_NAMES = []

    class VAV_OVERRIDE:
        NAME = 'vav_override'
        TYPE = 'int'
        UNIT = None
        ALTERNATE_NAMES = []

    class ANOTHER_STATUS:
        NAME = 'status2'
        TYPE = 'text'
        UNIT = None
        class POSSIBLE_VALUES:
            ON = 'ON'
            OFF = 'OFF'

        ALTERNATE_NAMES = []
        POSSIBLE_SPOKEN_VALUES = {POSSIBLE_VALUES.ON: ['on','1',1,'active','open'],
                               POSSIBLE_VALUES.OFF: ['off','0',0,'inactive','close'] }


    class CONTRAST:
        NAME = 'contrast'
        TYPE = 'double'
        UNIT = '%'
        class POSSIBLE_VALUES:
            MIN = 0
            MAX = 100
        ALTERNATE_NAMES = []
        POSSIBLE_SPOKEN_VALUES = {POSSIBLE_VALUES.MIN: ['minimum','zero',0,'off','zero percent'],
                                  POSSIBLE_VALUES.MAX: ['full', 'maximum', 100, 'hundred', 'hundred percent']}

    class HUE:
        NAME = 'hue'
        TYPE = 'double'
        UNIT = '%'
        class POSSIBLE_VALUES:
            MIN = 0
            MAX = 100
        ALTERNATE_NAMES = []
        POSSIBLE_SPOKEN_VALUES = {POSSIBLE_VALUES.MIN: ['minimum','zero',0,'off','zero percent'],
                                  POSSIBLE_VALUES.MAX: ['full', 'maximum', 100, 'hundred', 'hundred percent']}

    class SATURATION:
        NAME = 'saturation'
        TYPE = 'double'
        UNIT = '%'
        class POSSIBLE_VALUES:
            MIN = 0
            MAX = 100
        ALTERNATE_NAMES = []
        POSSIBLE_SPOKEN_VALUES = {POSSIBLE_VALUES.MIN: ['minimum','zero',0,'off','zero percent'],
                                  POSSIBLE_VALUES.MAX: ['full', 'maximum', 100, 'hundred', 'hundred percent']}

    class SHARPNESS:
        NAME = 'sharpness'
        TYPE = 'double'
        UNIT = '%'
        class POSSIBLE_VALUES:
            MIN = 0
            MAX = 100
        ALTERNATE_NAMES = []
        POSSIBLE_SPOKEN_VALUES = {POSSIBLE_VALUES.MIN: ['minimum','zero',0,'off','zero percent'],
                                  POSSIBLE_VALUES.MAX: ['full', 'maximum', 100, 'hundred', 'hundred percent']}

    class STREAM:
        NAME = 'stream'
        TYPE = 'text'
        UNIT = None
        ALTERNATE_NAMES = ['']