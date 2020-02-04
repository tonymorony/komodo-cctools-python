#!/bin/bash

while true; do
  ./komodo-cli -ac_name=DEXSTATS -conf=/root/node_0/DEXTEST.conf -rpcport=7000 -datadir=/root/node_0 DEX_streamsub pony_8x01.mkv 0 019a988dd4a6502ee816e589e296ad3c850e49ff889517995e2769973c4ca18a2d
done
