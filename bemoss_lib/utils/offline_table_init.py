__author__ =  "BEMOSS Team"
EVENTS_TABLE_NAME = 'all_events'
EVENTS_TABLE_VARS = {'logged_time': 'TIMESTAMP', 'event_id': 'UUID', 'source': 'text', 'date_id': 'text', 'time': 'TIMESTAMP', 'event': 'text', 'reason': 'text', 'logged_by': 'text', 'node_name': 'text'}
EVENTS_TABLE_PARTITION_KEYS = ['date_id']
EVENTS_TABLE_CLUSTERING_KEYS = ['logged_time', 'event_id']

offline_variables=dict()



