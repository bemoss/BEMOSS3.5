#!/bin/bash
#Copyright (c) 2016, Virginia Tech
#All rights reserved.
#
#Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
#disclaimer.
#2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
#disclaimer in the documentation and/or other materials provided with the distribution.
#
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
#INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
#WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

#The views and conclusions contained in the software and documentation are those of the authors and should not be
#interpreted as representing official policies, either expressed or implied, of the FreeBSD Project.
#
#This material was prepared as an account of work sponsored by an agency of the United States Government. Neither the
#United States Government nor the United States Department of Energy, nor Virginia Tech, nor any of their employees,
#nor any jurisdiction or organization that has cooperated in the development of these materials, makes any warranty,
#express or implied, or assumes any legal liability or responsibility for the accuracy, completeness, or usefulness or
#any information, apparatus, product, software, or process disclosed, or represents that its use would not infringe
#privately owned rights.
#
#Reference herein to any specific commercial product, process, or service by trade name, trademark, manufacturer, or
#otherwise does not necessarily constitute or imply its endorsement, recommendation, favoring by the United States
#Government or any agency thereof, or Virginia Tech - Advanced Research Institute. The views and opinions of authors
#expressed herein do not necessarily state or reflect those of the United States Government or any agency thereof.
#
#VIRGINIA TECH – ADVANCED RESEARCH INSTITUTE
#under Contract DE-EE0006352
#
#__author__ =  "BEMOSS Team"
#__credits__ = ""
#__version__ = "3.5"
#__maintainer__ = "BEMOSS Team"
#__email__ = "aribemoss@gmail.com"
#__website__ = "www.bemoss.org"
#__created__ = "2014-09-12 12:04:50"
#__lastUpdated__ = "2016-08-17 11:23:33"

. env/bin/activate
echo Got this for address:
echo $1
volttron -vv 2>&1>$1/log/volttron.log & # | tee $1/log/volttron.log &

rm -rf ~/.volttron/packaged/*
rm -rf ~/.volttron/agents/*
cd $1
python $1/bemoss_lib/utils/AddBemossUser.py
volttron-pkg package $1/Agents/BasicAgent


#Install discovery Agent #Discovery agent will be started by multinodeagent on the core
./scripts/core/pack_install.sh $1/Agents/DeviceDiscoveryAgent $1/Agents/DeviceDiscoveryAgent/devicediscoveryagent.launch.json devicediscoveryagent

#Install Platform agent
./scripts/core/pack_install.sh $1/Agents/PlatformMonitorAgent $1/Agents/PlatformMonitorAgent/platformmonitoragent.launch.json platformmonitoragent

#Install ApprovalHelper Agent
./scripts/core/pack_install.sh $1/Agents/ApprovalHelperAgent $1/Agents/ApprovalHelperAgent/approvalhelperagent.launch.json approvalhelperagent

#Install OpenADR Agent
./scripts/core/pack_install.sh $1/Agents/OpenADRAgent $1/Agents/OpenADRAgent/openadragent.launch.json openadragent

#Install TestDR Agent
./scripts/core/pack_install.sh $1/Agents/TestDRAgent $1/Agents/TestDRAgent/testdragent.launch.json testdragent

#Install Network Agent
./scripts/core/pack_install.sh $1/Agents/NetworkAgent $1/Agents/NetworkAgent/networkagent.launch.json networkagent

#Install Multinode Agent
./scripts/core/pack_install.sh $1/Agents/MultiNodeAgent $1/Agents/MultiNodeAgent/multinodeagent.launch.json multinodeagent

#Install Bacnet Agent
./scripts/core/pack_install.sh $1/services/core/BACnetProxy $1/services/core/BACnetProxy/bacnet-proxy.agent bacnetagent

#Install VIP Agent
./scripts/core/pack_install.sh $1/Agents/VIPAgent/ $1/Agents/VIPAgent/vipagent.launch.json vipagent

#Install TSD
./scripts/core/pack_install.sh $1/Agents/TSDAgent/ $1/Agents/TSDAgent/tsdagent.launch.json tsdagent

#sudo chmod 777 -R ~/.volttron/packaged/

### 
### Applications fail to install because bemossdb.executable table does not exists...
###

#Install Apps
# cd $1/Applications/code/Thermostat_Scheduler
# sudo python installapp.py
# cd $1/Applications/code/Lighting_Scheduler
# python installapp.py
# cd $1/Applications/code/Plugload_Scheduler
# python installapp.py
# cd $1/Applications/code/IlluminanceBasedLightingControl
# python installapp.py
# cd $1/Applications/code/Fault_Detection
# python installapp.py
# sudo chmod 777 -R ~/workspace
echo "BEMOSS App installation complete!"
