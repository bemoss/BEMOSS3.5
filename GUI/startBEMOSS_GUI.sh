#!/bin/sh

#Get project path
mypath=$(readlink -f "$0")
echo $mypath
guipath=$(dirname "$mypath")
echo $guipath
projectpath=$(dirname "$guipath")

NET_Installed=$(dpkg-query -W --showformat='${Status}\n' python-netifaces|grep "install ok installed")
echo $NET_Installed

if [ "$NET_Installed" = "install ok installed" ]; then
	echo "Package Installed"
else
	echo "Installing Package..."
	sudo apt-get install python-netifaces --assume-yes
fi
TK_Installed=$(dpkg-query -W --showformat='${Status}\n' python-imaging-tk|grep "install ok installed")
echo $TK_Installed

if [ "$TK_Installed" = "install ok installed" ]; then
	echo "Package Installed"
else
	echo "Installing Package..."
	sudo apt-get install python-imaging-tk --assume-yes
	# Tested on Odroid, this board looks like need the package below.
	sudo apt-get install python-imaging --assume-yes
fi

#run GUI in virtual environment
cd $guipath
python GUI.py
