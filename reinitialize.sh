#!/bin/sh
#Author: BEMOSS Team

./killold.sh
sudo -u postgres psql -c "CREATE USER admin WITH PASSWORD 'admin';"
sudo -u postgres psql -c "DROP DATABASE IF EXISTS bemossdb;"
sudo -u postgres createdb bemossdb -O admin
sudo -u postgres psql -d bemossdb -c "create extension hstore;"
. env/bin/activate
python Web_Server/manage.py makemigrations
python Web_Server/manage.py migrate
python Web_Server/manage.py createsuperuser   
python Web_Server/run/defaultDB.py
echo "******************************************************************************"
echo "*                                                                            *"
echo "* Congratulations! BEMOSS reInitialization is complete!                      *"
echo "* Before running BEMOSS for the first time, please refer the following link  *"
echo "* for post installtion configuration:                                        *"
echo "* https://github.com/bemoss/BEMOSS3.5/wiki/Post-Installation-Instruction     *"
echo "*                                                                            *"
echo "******************************************************************************"
