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
import sys
import os
#sys.path.insert(0,os.path.expanduser('~/BEMOSS'))
import re
from cassandra.cluster import Cluster
from cassandra.io.asyncorereactor import AsyncoreConnection
from cassandra.auth import PlainTextAuthProvider
from bemoss_lib.utils.find_own_ip import getIPs
import settings

def addSeed(newseed):
    '''
    Add a seed IP to the cassandra settings file, and update cassandra yaml file accordingly
    Will be called by udpclient in a node after a core is discovered
    :param newseed: Ip address string to add to seed list
    :return:
    '''
    try:
        casSettingsFile = open(settings.PROJECT_DIR+"/cassandra_settings.txt",'r+')
    except IOError as er:
        print 'cassandra settings file missing. Settings file must be present at this point'
    settingsContent = casSettingsFile.read()
    seeds = re.search('seeds:(.*)\n',settingsContent).group(1)
    if newseed not in seeds:
        oldseeds = seeds.replace('"','').strip()
        seeds = '"%s, %s"'% (newseed,oldseeds)
        settingsContent = re.sub('seeds:(.*)\n','seeds: %s\n'%seeds,settingsContent)
        casSettingsFile.seek(0)
        casSettingsFile.write(settingsContent)
        casSettingsFile.truncate()
        casYamlFile = open(os.path.expanduser("~")+"/workspace/cassandra/conf/cassandra.yaml",'r+')
        yamlContent = casYamlFile.read()
        yamlContent = re.sub('seeds:(.*)\n','seeds: %s\n' % seeds,yamlContent)
        casYamlFile.seek(0)
        casYamlFile.write(yamlContent)
        casYamlFile.truncate()
        casYamlFile.close()

    casSettingsFile.close()

def findKeyAndRep():
    try:
        casSettingsFile = open(settings.PROJECT_DIR+"/cassandra_settings.txt",'r')
        settingsContent = casSettingsFile.read()
        casSettingsFile.close()
        keyspace = re.search('keyspace_name: *(.*)\n',settingsContent).group(1)
        replication_factor = re.search('replication_factor: *(.*)\n',settingsContent).group(1)
    except IOError as er:
        print "No cassandra_settings file or bad settings file. Using default bemossspace and factor 1"
        keyspace = 'bemossspace'
        replication_factor = '1'

    return keyspace, replication_factor



def findIP():
    """
    Reads the listen address from cassandra settings file
    :return:
    """
    try:
        casSettingsFile = open(settings.PROJECT_DIR+"/cassandra_settings.txt",'r')
        settingsContent = casSettingsFile.read()
        casSettingsFile.close()
        ip_address = re.search('rpc_address: *([0-9\.]*)\n',settingsContent).group(1)
    except IOError as er:
        print "No cassandra_settings file. Using current IP"
        ip_address = getIPs()[-1]

    return ip_address

def findUserPass():
    try:
        casSettingsFile = open(settings.PROJECT_DIR+"/cassandra_settings.txt",'r')
        settingsContent = casSettingsFile.read()
        casSettingsFile.close()
        username = re.search('db_username: *(.*)\n',settingsContent).group(1)
        password = re.search('db_password: *(.*)\n',settingsContent).group(1)
    except IOError as er:
        print "No cassandra_settings file. Using the default cassandra cassandra userpass"
        username='cassandra'
        password='cassandra'

    userpass = [username,password]
    return userpass


def makeConnection():
    ip_address = findIP()
    notResolved = True
    while notResolved:
        notResolved=False
        try:
            userpass = findUserPass()
            ap = PlainTextAuthProvider(username=userpass[0], password=userpass[1])
            bCluster=Cluster([ip_address],connection_class=AsyncoreConnection,auth_provider=ap)
            bSpace = bCluster.connect()
        except Exception as er:
            redFlag = ['AuthenticationFailed','username','password','incorrect']
            test = filter(lambda x: x.lower() in str(er).lower(), redFlag)
            if len(test)==len(redFlag): #all redFlags words exists on message
                print 'provided username doesnt work. trying default:'
                ap = PlainTextAuthProvider(username='cassandra', password='cassandra')
                try:
                    bCluster=Cluster([ip_address],connection_class=AsyncoreConnection,auth_provider=ap)
                    bSpace=bCluster.connect()
                    bSpace.execute("ALTER USER cassandra with password 'merogharanuwakotmaparchhatimrokahaparchha'")
                except Exception as er:
                    print er
                    ap = PlainTextAuthProvider(username='cassandra', password='merogharanuwakotmaparchhatimrokahaparchha')
                    bCluster=Cluster([ip_address],connection_class=AsyncoreConnection,auth_provider=ap)
                    bSpace=bCluster.connect()

                bSpace.execute("CREATE USER %s with password '%s' SUPERUSER" % (userpass[0],userpass[1]))
                print ('The username and password created. Now trying login again')
                bCluster.shutdown()
                notResolved=True
            else:
                raise

    return bCluster, bSpace




if __name__ == '__main__':
    findIP()
