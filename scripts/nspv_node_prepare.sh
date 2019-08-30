#!/bin/bash
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install zip wget libgomp1 -y
wget http://159.69.45.70/nspv_daemon.zip
unzip nspv_daemon.zip
wget https://raw.githubusercontent.com/tonymorony/komodo-cctools-python/master/scripts/nspv_clients_spawn.py
wget http://159.69.45.70/fetch-params.sh
chmod u+x fetch-params.sh
./fetch-params.sh
python3 nspv_clients_spawn.py
