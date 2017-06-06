#!/bin/sh
#Author: BEMOSS Team

sudo killall volttron
sudo killall python
sudo killall pgadmin3
sudo service postgresql restart
pkill -9 python
sudo killall volttron
sudo killall python
fuser -n udp -k 47808
