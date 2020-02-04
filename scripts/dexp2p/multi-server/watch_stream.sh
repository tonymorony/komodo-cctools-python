#!/bin/bash

while true; do
  ./komodo-cli -ac_name=DEXSTATS -conf=/root/node_0/DEXTEST.conf -rpcport=7000 -datadir=/root/node_0 DEX_streamsub pony_8x01.mkv 0 014351f0bce757ada7e9889dd98d0a5226c7f726f6c45c2ec1b9aa9ab4e311836d
done
