__author__ =  "BEMOSS Team"
import settings
import db_helper
#Offline variables initialized
offline_table = 'offline_events'
offline_log_variables = {'date_id':'text','logged_time':'TIMESTAMP','agent_id':'text','event_id':'UUID','time':'TIMESTAMP','event':'text','reason':'text','related_to':'UUID','logged_by':'text','node_name':'text'}
offline_log_partition_keys = ['agent_id','date_id']
offline_log_clustering_keys = ['event_id']
offline_variables=dict()
multinode_data = db_helper.get_multinode_data()
node_name = multinode_data['this_node']
offline_variables['node_name']=node_name


