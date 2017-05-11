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
#__version__ = "2.0"
#__maintainer__ = "BEMOSS Team"
#__email__ = "aribemoss@gmail.com"
#__website__ = "www.bemoss.org"
#__created__ = "2014-09-12 12:04:50"
#__lastUpdated__ = "2016-03-14 11:23:33"

cd $1/
. env/bin/activate
volttron -vv 2>&1 | tee $1/log/volttron.log &

sudo chmod 777 -R /tmp/volttron_wheels/
sudo rm -rf /tmp/volttron_wheels/*
sudo rm -rf ~/.volttron/agents/*
cd $1/

volttron-pkg package $1/Agents/ThermostatAgent
volttron-pkg package $1/Agents/PlugloadAgent
volttron-pkg package $1/Agents/LightingAgent
volttron-pkg package $1/Agents/AmbientLightSensorAgent
volttron-pkg package $1/Agents/NetworkAgent
volttron-pkg package $1/Agents/PowerMeterAgent
volttron-pkg package $1/Agents/RTUAgent
volttron-pkg package $1/Agents/VAVAgent
volttron-pkg package $1/Agents/WeatherSensorAgent
volttron-pkg package $1/Agents/PowerMeter3phAgent
volttron-pkg package $1/Agents/MotionSensorAgent
volttron-pkg package $1/Agents/TempSensorAgent
#volttron-pkg package $1/Agents/DeviceDiscoveryAgent
#volttron-pkg configure /tmp/volttron_wheels/devicediscoveryagent-0.1-py2-none-any.whl $1/Agents/DeviceDiscoveryAgent/devicediscoveryagent.launch.json
#volttron-ctl install devicediscoveryagent=/tmp/volttron_wheels/devicediscoveryagent-0.1-py2-none-any.whl
volttron-pkg package $1/Agents/AppLauncherAgent
volttron-pkg configure /tmp/volttron_wheels/applauncheragent-0.1-py2-none-any.whl $1/Agents/AppLauncherAgent/applauncheragent.launch.json
volttron-ctl install applauncheragent=/tmp/volttron_wheels/applauncheragent-0.1-py2-none-any.whl
volttron-pkg package $1/Applications/code/Thermostat_Scheduler
volttron-pkg package $1/Applications/code/Lighting_Scheduler
volttron-pkg package $1/Applications/code/Plugload_Scheduler

#Install Platform agent
volttron-pkg package $1/Agents/PlatformMonitorAgent
volttron-pkg configure /tmp/volttron_wheels/platformmonitoragent-0.1-py2-none-any.whl $1/Agents/PlatformMonitorAgent/platformmonitoragent.launch.json
volttron-ctl install platformmonitoragent=/tmp/volttron_wheels/platformmonitoragent-0.1-py2-none-any.whl

#volttron-pkg package $1/Agents/ApprovalHelperAgent/
#volttron-pkg configure /tmp/volttron_wheels/approvalhelperagent-0.1-py2-none-any.whl $1/Agents/ApprovalHelperAgent/approvalhelperagent.launch.json
#volttron-ctl install approvalhelperagent=/tmp/volttron_wheels/approvalhelperagent-0.1-py2-none-any.whl

# Run multibuilding agent
volttron-pkg package $1/Agents/MultiBuilding/
volttron-pkg configure /tmp/volttron_wheels/multibuildingagent-0.1-py2-none-any.whl $1/Agents/MultiBuilding/multibuildingagent.launch.json
volttron-ctl install multibuildingagent=/tmp/volttron_wheels/multibuildingagent-0.1-py2-none-any.whl
# Run network agent
volttron-pkg package $1/Agents/NetworkAgent/
volttron-pkg configure /tmp/volttron_wheels/networkagent-0.1-py2-none-any.whl $1/Agents/NetworkAgent/networkagent.launch.json
volttron-ctl install networkagent=/tmp/volttron_wheels/networkagent-0.1-py2-none-any.whl
#Run Twistd Launcher Agent - Now run using linux command not this agent
#volttron-pkg package $1/Agents/TwistdLauncher/
#volttron-pkg configure /tmp/volttron_wheels/launcheragent-0.1-py2-none-any.whl $1/Agents/TwistdLauncher/twistd.launcher
#volttron-ctl install launcheragent=/tmp/volttron_wheels/launcheragent-0.1-py2-none-any.whl

sudo chmod 777 -R /tmp/volttron_wheels/

#Install Apps
#cd $1/Applications/code/AppLauncherAgent
#sudo python installapp.py
cd $1/Applications/code/Thermostat_Scheduler
sudo python installapp.py
cd $1/Applications/code/Lighting_Scheduler
sudo python installapp.py
cd $1/Applications/code/Plugload_Scheduler
sudo python installapp.py
sudo chmod 777 -R ~/workspace
echo "BEMOSS App installation complete!"
