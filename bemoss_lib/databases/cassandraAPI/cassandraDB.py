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
import pandas
from cassandra import *
import numpy
import datetime
import re
from bemoss_lib.databases.cassandraAPI import cassandraHelper
from bemoss_lib.utils.catcherror import catcherror
import json
from bemoss_lib.utils import date_converter
connection_established = False
from uuid import UUID
#Global variables
bCluster, bSpace, keyspace_name, replication_factor = None, None, None, None



@catcherror('Could not get replication')
def get_replication(keyspace):

    global connection_established
    if not connection_established:
        makeConnection()
    x = bSpace.execute("SELECT replication from system_schema.keyspaces where keyspace_name=%s",(keyspace,))
    y =  int(x[0][0]['replication_factor'])
    return y


@catcherror('Could not set replication')
def set_replication(keyspace,replication):

    global connection_established
    if not connection_established:
        makeConnection()
    bSpace.execute("ALTER KEYSPACE %s WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : %d };" % (keyspace,replication))



def makeConnection():
    try:
        global bCluster, bSpace, keyspace_name, replication_factor, connection_established
        bCluster, bSpace = cassandraHelper.makeConnection()
        keyspace_name,replication_factor = cassandraHelper.findKeyAndRep()
        bSpace.set_keyspace(keyspace_name)
        if bSpace is not None:
            connection_established = True #if some error occurs this would be skipped
            return True
    except InvalidRequest as er:
        try:
            bSpace.execute("create keyspace %s with replication={'class':'SimpleStrategy','replication_factor':%s}" % (keyspace_name, replication_factor))
            bSpace.set_keyspace(keyspace_name)
            return True
        except Exception as er:
            print 'bemossspace couldnt be created/switched to'
            print er
            raise er

    except Exception as er:
        print 'Cannot establish connection'
        raise er

try:
    makeConnection()
except Exception as er:
    print 'Connection cannot be established'
    print er

def descTables(keyspace):

    if not connection_established:
        makeConnection()
    tables=bSpace.execute('select table_name from system_schema.tables where keyspace_name=%s',(keyspace,))
    return tables

def createCustomTable(columns,partition_keys,clustering_keys,tablename):
    global connection_established
    if not connection_established:
        makeConnection()

    varStr = ''
    for vars,types in columns.items():
        varStr += vars+" "+types+", "
    varStr = varStr[:-2]

    primaryStr = ', '.join(partition_keys)
    clusteringStr = ', '.join(clustering_keys)

    create_query = "create table {0} ({1}, PRIMARY KEY (({2}), {3}))".format(tablename,varStr,primaryStr,clusteringStr)
    try:
        bSpace.execute(create_query)
    except AlreadyExists as e:
        print 'table %s already present' % tablename
        raise
    except Exception:
        connection_established = False #Try to establish connection again next time
        raise

    return 0


def customInsert(all_vars, log_vars, tablename):
    """
    :param all_vars: dictionary (usually APIobject.variables). It contains all the variables and their values.
    :param log_vars: dictionary (usually APIobject.log_variables). It contains variables to be logged and their datatypes
    :return: 0, if successful

    """
    global connection_established

    if not connection_established:
        makeConnection()

    all_vars = dict(all_vars)
    log_vars = dict(log_vars)

    varStr = ""
    placeHolderStr = ""

    values = []
    noVarStr =""
    for var in log_vars:
        reading = all_vars.get(var)
        if not reading == None:
            varStr += var+", "
            placeHolderStr += "%s"+", "
            values.append(reading)
        else:
            noVarStr+=var+', '

    varStr=varStr[:-2]
    placeHolderStr = placeHolderStr[:-2]
    noVarStr=noVarStr[:-2]

    insert_query = "insert into {0} ({1}) VALUES ({2})".format(tablename,varStr,placeHolderStr)
    retry = True
    while retry:
        try:
            bSpace.execute(insert_query,values)
            retry = False
        except InvalidRequest as e:
            connection_established = False
            if e.message.find('unconfigured')!=-1:
                print 'Table not exits. Creating one:'
                createTable(log_vars,tablename=tablename)
                print "Table Created. Now Trying to insert Again:"
                bSpace.execute(insert_query,values)
                retry = False
            elif e.message.lower().find('unknown identifier')!=-1:
                k = str(e.message)
                newColumn = re.search('[Uu]nknown identifier ([a-zA-Z_]*)',k).groups()[0]
                alter_query = "ALTER TABLE {0} ADD {1} {2}".format(tablename,newColumn,log_vars[newColumn])
                bSpace.execute(alter_query)
                retry = True
            else:
                #TO DO: Don't do this. if the table already exists and can't insert data, simply raise exception
                #drop_query = "drop table {0}".format(tableName)
                #bSpace.execute(drop_query)
                #print "Table Dropped. Now Trying to create again"
                #createTable(agentID,log_vars)
                #print "Created. Now inserting"
                #bSpace.execute(insert_query,values)
                retry = False
                print e
                raise
        except:
            connection_established = False #Try to connect again next-time
            raise

    return 0

def customQuery(querryString,parameters=None):
    if parameters==None:
        x = bSpace.execute(querryString)
    else:
        x = bSpace.execute(querryString,parameters)
    if x is not None:
        return list(x)
    else:
        return []

def createTable(variables, tablename):
    """
    Function to create table for a AgentID

    :param agentID: string. Table with b<agent_id> will be created
    :param variables: dictionary (usually APIobject.log_variables). It contains variables to be logged and their datatypes
    :return: 0, if successful

    """
    variables = dict(variables)

    variables['agent_id']='text'
    variables['date_id']='text'
    variables['time'] = 'TIMESTAMP'
    primary_keys = ['agent_id','date_id']
    clustering_keys = ['time']

    return createCustomTable(variables,primary_keys,clustering_keys,tablename)


def insert(agentID, all_vars, log_vars, cur_timeLocal=None, tablename=None):
    """
    :param agentID: string. Data will be inserted to table named B<agent_id>
    :param all_vars: dictionary (usually APIobject.variables). It contains all the variables and their values.
    :param log_vars: dictionary (usually APIobject.log_variables). It contains variables to be logged and their datatypes
    :return: 0, if successful

    timestamp is generated based on current utc time. UTC time is put in cassandra database. If the table by the agent
    name doesn't exist, table is created. **If error occurs because the name of variables/data_type has changed, the old
    table will be deleted, and a new one with currect variable names/datatype will be created**.

    **Need to avoid doing this in final version.Feature made to help during development
    """
    #make copies to not mess up original variables
    all_vars = dict(all_vars)
    log_vars = dict(log_vars)

    global connection_established

    if not connection_established:
        makeConnection()

    if cur_timeLocal == None:
        cur_timeUTC = datetime.datetime.utcnow()
    else:
        cur_timeUTC = date_converter.localToUTC(cur_timeLocal)

    date_only = str(cur_timeUTC.date())

    if tablename==None:
        tablename = "B"+agentID

    #Add default columns to log_vars
    log_vars['agent_id']='text'
    log_vars['date_id']='text'
    log_vars['time']='TIMESTAMP'

    #assign values to deafault columns
    all_vars['agent_id']=agentID
    all_vars['date_id']=date_only
    all_vars['time']=cur_timeUTC

    return customInsert(all_vars=all_vars,log_vars=log_vars,tablename=tablename)


def delete(agentID,startDate=None, endDate=None, tablename=None):
    """
    Performs deletion of data. if statDate and endDate is omitted, whole table is delted.
    :param agentID: The B<agentID> table in which the operation is to be performed
    :param startDate: dateTime.date object (local timezone). The begining date from which to delete. Must be supplied
    unless trying to delete the whole table
    :param endDate: datetime.date object (local timezone). The endDate upto which to delete. The default is to upto today.
    must be supplied unless trying to delte the whole table
    :return: 0, if successfull

    Delete can be performed with a resolution of a day so, data cannot be partially deleted for a day. If new data needs
    to be written to existing place, simply inserting it again with same primary key will override it.

    """
    global connection_established
    if not connection_established:
        makeConnection()

    if tablename==None:
        tablename = "B"+agentID

    if endDate==None and startDate==None:
        try:
            delete_query='drop table {0}'.format(tablename)
            bSpace.execute(delete_query)
        except InvalidRequest as e:
            if e.message.find('unconfigured')!=-1:
                print "Already delted. Don't worry about it"
                return  0
            else:
                raise
        except Exception:
            connection_established = False #Try to establish connection again next time
            raise

    elif startDate==None:
        print "startTime compulsory when endTime is given"
        return -1
    elif endDate==None:
        endDate=datetime.datetime.now()

    daterange = pandas.date_range(startDate,endDate)
    date_local=""
    try:
        for day in daterange:
            date_local = str(day.date())
            delete_query = 'DELETE from {0} WHERE agent_id=%s AND date_id=%s'.format(tablename)
            bSpace.execute(delete_query,(agentID,date_local))

    except Exception as e:
        print "sorry, not deleted all. deleted upto:%s" % date_local
        connection_established = False
        return  -1

    return 0





def retrieve(agentID, vars=None, startTime=None, endTime=None,export=False,tablename=None):
    """Function to retrieve Data from the active cassandra cluster. \n
    :param agentID: must supply, since each agentID is associated with a table in database.
    :param vars: supplied as a list of strings. It represents the variables to be retrieved from the table.
          eg. ['time','temperature','heat_setpoint']. If any of the variables don't match the column name, the result
          will contain -1. If not supplied, the default is to return the complete row \n\n
    :param startTime: the time in localtime zone (the timezone of the node), in datetime.datetime format. It marks the
            beginning for the range. If not supplied, will be taken 24-hours before endTime
    :param endTime: the time in localtime zone (the timezone of the node), in datetime.datetime format.It marks the end of the
            range. If not supplied, will be taken as the currentTime.
    :return: A numpy 2-dimensional array. Columns corresponds to variables querried, and rows corresponds to
            various table entries.The time is reported in local time (cassandra returns UTC time, conversion is done in
            this function). If the query fails, -1 is returned (and no exception raised)

    """

    global connection_established
    if not connection_established:
        makeConnection()

    x = datetime.datetime.utcnow()-datetime.datetime.now()
    sec_offset = int(round(x.seconds+x.microseconds/1000000.0))
    timeDel = datetime.timedelta(seconds=sec_offset)

    if startTime==None:
        startTimeUTC=datetime.datetime.utcnow()-datetime.timedelta(hours=24)
    else:
        startTimeUTC = date_converter.localToUTC(startTime) #convert to UTC

    if endTime==None:
        endTimeUTC = datetime.datetime.utcnow()
    else:
        endTimeUTC = date_converter.localToUTC(endTime) #convert to UTC

    if tablename==None:
        tablename = str("B"+agentID).lower()


    if vars is None:
        try:
            result=bSpace.execute("select column_name from system_schema.columns WHERE keyspace_name=%s and table_name=%s",[keyspace_name,tablename])
        except:
            connection_established = False #Try to establish connection again next time
            raise
        vars = [var[0] for var in result]

    varStr = ', '.join(vars) #to get rid of the last ', '
    daterange = pandas.date_range(startTimeUTC,endTimeUTC)
    total_result = []
    try:
        for day in daterange:

            date_local = str(day.date())
            result = bSpace.execute('select {0} from {1} WHERE agent_id=%s AND date_id=%s AND time >= %s AND time <= %s'.format(varStr, tablename),[agentID,date_local,startTimeUTC,endTimeUTC])
            total_result += result

        total_result = numpy.array(total_result)

        # If there is no data, return an empty list []
        if len(total_result) == 0:
            return vars, total_result

        if vars is not None:
            #convert the UTC time to local time if time is present
            #more robust method would be look at data types of the result and convert them if it has datetime data type


            if 'cooling_mode' in vars:
                total_result[:, vars.index('cooling_mode')] = map(lambda x: x.encode('utf8'), total_result[:, vars.index('cooling_mode')])
            if export:
                if 'time' in vars:
                    time_array = total_result[:, vars.index('time')]
                    time_array = [date_converter.UTCToLocal(t) for t in time_array]  # convert to local time for exporting
                    total_result[:, vars.index('time')] = map(lambda x: "{}".format(x.strftime('%y-%m-%d %H:%M:%S')),time_array)
            else:
                if 'time' in vars:
                    time_array = total_result[:, vars.index('time')]
                    total_result[:, vars.index('time')] = map(lambda x: int((x-datetime.datetime(1970,1,1)).total_seconds()*1000),time_array) #epoch times for chart
                if 'status' in vars:
                    total_result[:, vars.index('status')] = map(lambda x: 1 if str(x).lower() == 'on' else 0 if str(x).lower() == 'off' else x, total_result[:, vars.index('status')])
                if 'motion' in vars:
                    total_result[:, vars.index('motion')] = map(lambda x: 1 if x == True else 0 if x == False else x, total_result[:, vars.index('motion')])

            return vars, total_result

    except InvalidRequest as e:
        if e.message.find('unconfigured columnfamily')!=-1:
            total_result = -1
            print ('table not exist')
        else:
            total_result = -1
            print e
    except:
        connection_established = False #Try to establish connection again next time
        raise


def retrieve_for_export(agentID, vars=None, startTime=None, endTime=None, tablename=None):
    a,b = retrieve(agentID=agentID,vars=vars,startTime=startTime,endTime=endTime,export=True,tablename=tablename)
    return a,b

if __name__ == '__main__':
    x = get_replication('system_auth')
    set_replication('system_auth',2)
    print x
