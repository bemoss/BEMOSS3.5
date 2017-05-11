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
import os
import re
import sys
import settings
sys.path.insert(0,settings.PROJECT_DIR)
from bemoss_lib.utils.find_own_ip import getIPs


def init():
    try:
        casSettingsFile = open(settings.PROJECT_DIR+"/cassandra_settings.txt",'r')
    except IOError as er:
        print "creating a new cassandra_settings file"
        cluster_name = raw_input("Enter a unique name for cassandra cluster-name: ")
        if cluster_name=='':
            cluster_name = 'bemosscluster'
            print 'Using default clustername: '+cluster_name
        db_username = raw_input("Enter database username: ")
        if db_username=='':
            db_username='bemoss'
            print 'Using default username: '+db_username
        db_password = raw_input("Enter database password: ")
        if db_password=='':
            db_password='bemoss'
            print 'Using default password: '+db_password
        else:
            password2 = raw_input("Enter password again: ")
            while password2 != db_password:
                password2 = raw_input("Password doesn't match. Input again: ")
                #TODO have some exit condition
        ip_address = getIPs()[-1]
        casSettingsFile = open(settings.PROJECT_DIR+"/cassandra_settings.txt",'w')
        contents="""cluster_name: '%s'
keyspace_name: bemossspace
replication_factor: 2
listen_address: %s
rpc_address: %s
seeds: "%s"
authenticator: PasswordAuthenticator
db_username: %s
db_password: %s
MAX_HEAP_SIZE="400M"
HEAP_NEWSIZE="100M"
    """ % (cluster_name,ip_address,ip_address,ip_address,db_username,db_password)
        casSettingsFile.write(contents)
        casSettingsFile.close()
        casSettingsFile = open(settings.PROJECT_DIR+"/cassandra_settings.txt",'r')

    settingsContent = casSettingsFile.read()
    casSettingsFile.close()
    try:
        casYamlFile = open(settings.PROJECT_DIR+"/cassandra/conf/cassandra.yaml",'r')
        yamlContent = casYamlFile.read()
        casYamlFile.close()
    except IOError as er:
        print "Not found:" + settings.PROJECT_DIR+"/cassandra/conf/cassandra.yaml"
        raise

    try:
        casEnvFile = open(settings.PROJECT_DIR+"/cassandra/conf/cassandra-env.sh",'r')
        envContent = casEnvFile.read()
        casEnvFile.close()
    except IOError as er:
        print "Not found:" + settings.PROJECT_DIR+"/cassandra/conf/cassandra.yaml"
        raise

    cluster_name = re.search('cluster_name:(.*)\n',settingsContent).group(1)
    listen_address = re.search('listen_address:(.*)\n',settingsContent).group(1)
    rpc_address = re.search('rpc_address: *([0-9\.]*)\n',settingsContent).group(1)
    db_username = re.search('db_username: *(.*)\n',settingsContent).group(1)
    db_password = re.search('db_password: *(.*)\n',settingsContent).group(1)
    keyspace = re.search('keyspace_name: *(.*)\n',settingsContent).group(1)
    replication_factor = re.search('replication_factor: *(.*)\n',settingsContent).group(1)
    myips = getIPs()

    seeds = re.search('seeds:(.*)\n',settingsContent).group(1)
    authenticator = re.search('authenticator:(.*)\n',settingsContent).group(1)
    MAX_HEAP_SIZE = re.search('MAX_HEAP_SIZE=("[a-zA-Z0-9]*")\n',settingsContent).group(1)
    HEAP_NEWSIZE = re.search('HEAP_NEWSIZE=("[a-zA-Z0-9]*")\n',settingsContent).group(1)

    #check if any of the seeds IP is current machine IP. At least one seed needs to be self IP
    bad_seed = True
    for ip in myips:
        if ip in seeds:
            bad_seed = False

    if bad_seed:
        oldseeds = seeds.replace('"','').strip()
        seeds = '"%s, %s"'% (myips[-1],oldseeds)

    if listen_address.strip() not in myips or rpc_address.strip() not in myips:

        listen_address = myips[-1]
        rpc_address = myips[-1]



    casSettingsFile = open(settings.PROJECT_DIR+"/cassandra_settings.txt",'w')
    contents="""cluster_name: %s
keyspace_name: %s
replication_factor: %s
listen_address: %s
rpc_address: %s
seeds: %s
authenticator: %s
db_username: %s
db_password: %s
MAX_HEAP_SIZE=%s
HEAP_NEWSIZE=%s
""" % (cluster_name.strip(),keyspace.strip(),replication_factor.strip(),myips[-1],myips[-1],seeds.strip(),authenticator.strip(),db_username.strip(),db_password.strip(),MAX_HEAP_SIZE.strip(),HEAP_NEWSIZE.strip())
    casSettingsFile.write(contents)
    casSettingsFile.close()

    yamlContent = re.sub('cluster_name:(.*)\n','cluster_name: %s\n' % cluster_name,yamlContent)
    yamlContent = re.sub('listen_address:(.*)\n','listen_address: %s\n' % listen_address,yamlContent)
    yamlContent = re.sub('rpc_address:(.*)\n','rpc_address: %s\n' % rpc_address,yamlContent)
    yamlContent = re.sub('authenticator:(.*)\n','authenticator: %s\n' % authenticator,yamlContent)
    yamlContent = re.sub('seeds:(.*)\n','seeds: %s\n' % seeds,yamlContent)
    envContent = re.sub('#?MAX_HEAP_SIZE=("[a-zA-Z0-9]*")\n','MAX_HEAP_SIZE=%s\n' % MAX_HEAP_SIZE,envContent)
    envContent = re.sub('#?HEAP_NEWSIZE=("[a-zA-Z0-9]*")\n','HEAP_NEWSIZE=%s\n'%HEAP_NEWSIZE,envContent)

    try:
        casYamlFile = open(settings.PROJECT_DIR+"/cassandra/conf/cassandra.yaml",'w')
        casYamlFile.write(yamlContent)
        casYamlFile.close()
    except IOError as er:
        print "Error writing:" + settings.PROJECT_DIR+"/cassandra/conf/cassandra.yaml"
        raise

    try:
        casEnvFile = open(settings.PROJECT_DIR+"/cassandra/conf/cassandra-env.sh",'w')
        casEnvFile.write(envContent)
        casEnvFile.close()
    except IOError as er:
        print "Error writing:" + settings.PROJECT_DIR+"/cassandra/conf/cassandra.yaml"
        raise

if __name__ == '__main__':
    init()
