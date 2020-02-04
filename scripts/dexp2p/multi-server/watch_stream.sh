#!/bin/bash

while true; do
  ./komodo-cli -ac_name=DEXSTATS -conf=/root/node_0/DEXTEST.conf -rpcport=7000 -datadir=/root/node_0 DEX_streamsub pony_8x01.mkv 0 0165986632addeab67c50eceada9625e31e29bbb402249b120cd0115cdd2853752
done
