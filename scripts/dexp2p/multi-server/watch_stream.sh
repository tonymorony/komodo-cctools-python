#!/bin/bash

while true; do
  ./komodo-cli -ac_name=DEXSTATS -conf=/root/node_0/DEXTEST.conf -rpcport=7000 -datadir=/root/node_0 DEX_streamsub pony_8x01.mkv 0 01d6a288b65dd144f054f1aaf65e4850d56eaefb559c4f2e9317e85fdabc39ac46
done
