#!/bin/bash
export PYTHONPATH=$1/env
nohup x-terminal-emulator -e $1/env/bin/python $1/Web_Server/run/bemoss_server.py
#---------
