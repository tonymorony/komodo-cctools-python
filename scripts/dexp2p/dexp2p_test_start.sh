#!/bin/bash

export NODESAMOUNT=$1

python3 dexp2p_clients_spawn.py
./dexp2p_start_spam.sh
python3 dexp2p_clients_spawn.py

rm -rf node_*
rm -rf spam_p2p/orderbooks/*
rm -rf spam_p2p/packages/*
