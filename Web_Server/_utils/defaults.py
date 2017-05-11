# -*- coding: utf-8 -*-
# Authors: BEMOSS Team
# Version: 2.0
# Email: aribemoss@gmail.com
# Created: "2014-10-13 18:45:40"
# Updated: "2015-02-13 15:06:41"


# Copyright © 2014 by Virginia Polytechnic Institute and State University
# All rights reserved
#
# Virginia Polytechnic Institute and State University (Virginia Tech) owns the copyright for the BEMOSS software and
# and its associated documentation ("Software") and retains rights to grant research rights under patents related to
# the BEMOSS software to other academic institutions or non-profit research institutions.
# You should carefully read the following terms and conditions before using this software.
# Your use of this Software indicates your acceptance of this license agreement and all terms and conditions.
#
# You are hereby licensed to use the Software for Non-Commercial Purpose only.  Non-Commercial Purpose means the
# use of the Software solely for research.  Non-Commercial Purpose excludes, without limitation, any use of
# the Software, as part of, or in any way in connection with a product or service which is sold, offered for sale,
# licensed, leased, loaned, or rented.  Permission to use, copy, modify, and distribute this compilation
# for Non-Commercial Purpose to other academic institutions or non-profit research institutions is hereby granted
# without fee, subject to the following terms of this license.
#
# Commercial Use: If you desire to use the software for profit-making or commercial purposes,
# you agree to negotiate in good faith a license with Virginia Tech prior to such profit-making or commercial use.
# Virginia Tech shall have no obligation to grant such license to you, and may grant exclusive or non-exclusive
# licenses to others. You may contact the following by email to discuss commercial use:: vtippatents@vtip.org
#
# Limitation of Liability: IN NO EVENT WILL VIRGINIA TECH, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR REDISTRIBUTE
# THE PROGRAM AS PERMITTED ABOVE, BE LIABLE TO YOU FOR DAMAGES, INCLUDING ANY GENERAL, SPECIAL, INCIDENTAL OR
# CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE OR INABILITY TO USE THE PROGRAM (INCLUDING BUT NOT LIMITED TO
# LOSS OF DATA OR DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD PARTIES OR A FAILURE
# OF THE PROGRAM TO OPERATE WITH ANY OTHER PROGRAMS), EVEN IF VIRGINIA TECH OR OTHER PARTY HAS BEEN ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGES.
#
# For full terms and conditions, please visit https://bitbucket.org/bemoss/bemoss_os.
#
# Address all correspondence regarding this license to Virginia Tech's electronic mail address: vtippatents@vtip.org


__author__ =  "BEMOSS Team"


import getpass
import os
from django_web_server import settings_tornado


current_path = settings_tornado.PROJECT_DIR
current_path = current_path.replace("/workspace/bemoss_web_ui","")
print current_path

PUSH_SOCKET = "ipc://" + current_path + "/.volttron/run/publish"
SUB_SOCKET = "ipc://" + current_path + "/.volttron/run/subscribe"


DISABLED_VALUES_THERMOSTAT = {"everyday": {
            'monday_heat': [],
            'monday_cool': [],
            'tuesday_heat': [],
            'tuesday_cool': [],
            'wednesday_heat': [],
            'wednesday_cool': [],
            'thursday_heat': [],
            'thursday_cool': [],
            'friday_heat': [],
            'friday_cool': [],
            'saturday_heat': [],
            'saturday_cool': [],
            'sunday_heat': [],
            'sunday_cool': []},
        "weekdayweekend": {
            'weekday_heat': [],
            'weekday_cool': [],
            'weekend_heat': [],
            'weekend_cool': []},
        "holiday": {
            'holiday_heat': [],
            'holiday_cool': [],
        }}

DISABLED_VALUES_THERMOSTAT_NEW = {"everyday": {
            'monday': [],
            'tuesday': [],
            'wednesday': [],
            'thursday': [],
            'friday': [],
            'saturday': [],
            'sunday': []},
        "weekdayweekend": {
            'weekday': [],
            'weekend': []},
        "holiday": {
            'holiday': []}}

DISABLED_VALUES_LIGHTING = {"everyday": {
            'monday': [],
            'tuesday': [],
            'wednesday': [],
            'thursday': [],
            'friday': [],
            'saturday': [],
            'sunday': []},
        "weekdayweekend": {
            'weekday': [],
            'weekend': []},
        "holiday": {
            'holiday': []}}

DISABLED_VALUES_PLUGLOAD = {"everyday": {
            'monday': [],
            'tuesday': [],
            'wednesday': [],
            'thursday': [],
            'friday': [],
            'saturday': [],
            'sunday': []},
        "weekdayweekend": {
            'weekday': [],
            'weekend': []},
        "holiday": {
            'holiday': []}}

THERMOSTAT_DEFAULT_SCHEDULE_NEW = {
                "everyday": {
                    "friday": [

                    ],
                    "monday": [

                    ],
                    "saturday": [

                    ],
                    "sunday": [

                    ],
                    "thursday": [

                    ],
                    "tuesday": [

                    ],
                    "wednesday": [

                    ],
                },
                "holiday": [

                    ]
            }



THERMOSTAT_DEFAULT_SCHEDULE = {
                "everyday": {
                    "friday": {
                        "cool": [

                        ],
                        "heat": [

                        ]
                    },
                    "monday": {
                        "cool": [


                        ],
                        "heat": [

                        ]
                    },
                    "saturday": {
                        "cool": [

                        ],
                        "heat": [

                        ]
                    },
                    "sunday": {
                        "cool": [

                        ],
                        "heat": [

                        ]
                    },
                    "thursday": {
                        "cool": [

                        ],
                        "heat": [

                        ]
                    },
                    "tuesday": {
                        "cool": [

                        ],
                        "heat": [

                        ]
                    },
                    "wednesday": {
                        "cool": [

                        ],
                        "heat": [

                        ]
                    }
                },
                "holiday": {
                    "cool": [

                    ],
                    "heat": [

                    ]
                }
            }

LIGHTING_DEFAULT_SCHEDULE = {
                "everyday": {
                    "friday": [

                    ],
                    "monday": [

                    ],
                    "saturday": [

                    ],
                    "sunday": [

                    ],
                    "thursday": [

                    ],
                    "tuesday": [

                    ],
                    "wednesday": [

                    ]
                },
                "holiday": {
                    "holiday": [

                    ]
                }
            }

PLUGLOAD_DEFAULT_SCHEDULE = {
                "everyday": {
                    "friday": [

                    ],
                    "monday": [

                    ],
                    "saturday": [

                    ],
                    "sunday": [

                    ],
                    "thursday": [

                    ],
                    "tuesday": [

                    ],
                    "wednesday": [

                    ]
                },
                "holiday": {
                    "holiday": [

                    ]
                }
            }