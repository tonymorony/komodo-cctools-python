#!/bin/bash

while true; do
  ./komodo-cli -ac_name=DEXSTATS -conf=/root/node_0/DEXTEST.conf -rpcport=7000 -datadir=/root/node_0 DEX_streamsub pony_8x01.mkv 0 $1
done
