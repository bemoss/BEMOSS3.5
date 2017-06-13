#!/bin/sh
#Author: BEMOSS Team

# Get project path
mypath=$(readlink -f "$0")
echo $mypath
guipath=$(dirname "$mypath")
echo $guipath
projectpath=$(dirname "$guipath")
echo $projectpath

sudo apt-get update
# Download and install the Linux dependencies of the BEMOSS platform
sudo apt-get install build-essential openssl git g++ libxml2-dev libxslt1-dev python-dev libevent-dev libssl-dev python-tk python-pip libffi-dev libpq-dev python-psycopg2 python-zmq gnome-terminal --assume-yes

#Remove the existing volttron folder if exists
sudo rm -rf ~/.volttron/
#Go to the bemoss folder and run the bootstrap command 
cd $projectpath
python2.7 bootstrap.py

# Check if the bootstrap is successfully done
volttronpath="$projectpath/env"
if [ ! -d "$volttronpath" ]; then
    echo "volttron is not properly installed, please try install again"
    exit 1
fi
echo "volttron successfully installed"

cd $projectpath
. env/bin/activate

# Install Python dependencies in the BEMOSS virtualenv
pip install -r BEMOSS_requirements.txt
pip install pyzmq==14.7 --upgrade --install-option="--zmq=bundled"

# Download and install the dependencies of the postgresql database
sudo apt-get install postgresql postgresql-contrib python-yaml --assume-yes
# Create the bemossdb database
sudo -u postgres psql -c "CREATE USER admin WITH PASSWORD 'admin';"
sudo -u postgres psql -c "DROP DATABASE IF EXISTS bemossdb;"
sudo -u postgres createdb bemossdb -O admin
sudo -u postgres psql -d bemossdb -c "create extension hstore;"
# Install Dependencies for Cassandra
sudo apt-get install openjdk-8-jre libjna-java --assume-yes
# Install Cassandra
cd $projectpath
wget http://downloads.datastax.com/community/dsc-cassandra-3.0.9-bin.tar.gz
tar -xzf dsc-cassandra-3.0.9-bin.tar.gz
sudo rm dsc-cassandra-3.0.9-bin.tar.gz 
sudo rm -rf cassandra/
sudo mv dsc-cassandra-3.0.9 cassandra
# Install Cassandra Driver
# (For better performance of Cassandra, the install-option can be removed but might cause installation failure in some boards.)
CASS_DRIVER_NO_CYTHON=1 pip install cassandra-driver
# Go to the bemoss_web_ui and run the syncdb command for the database tables (ref: model.py)
cd $projectpath
python Web_Server/manage.py makemigrations
python Web_Server/manage.py migrate
# create web ui super user first
python Web_Server/manage.py createsuperuser   
python Web_Server/run/defaultDB.py
#Initialize the tables
mkdir -p ~/.volttron/agents
mkdir -p .temp
python bemoss_lib/utils/platform_initiator.py
# Prompt user for Cassandra Authorization Info
python bemoss_lib/databases/cassandraAPI/initialize.py
# Fix miscellaneaus issues
sudo bemoss_lib/utils/increase_open_file_limit.sh
rm bemoss_lib/utils/increase_open_file_limit.sh
deactivate
python Agents/MultiNodeAgent/generate_certificates.py 2
# Direct user to post installation configuration
echo "******************************************************************************"
echo "*                                                                            *"
echo "* Congratulations! BEMOSS Installation is complete!                          *"
echo "* Before running BEMOSS for the first time, please refer the following link  *"
echo "* for post installtion configuration:                                        *"
echo "* https://github.com/bemoss/BEMOSS3.5/wiki/Post-Installation-Instruction     *"
echo "*                                                                            *"
echo "******************************************************************************"
