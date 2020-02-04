#!/bin/bash

while true; do
  ./komodo-cli -ac_name=DEXSTATS -conf=/root/node_0/DEXTEST.conf -rpcport=7000 -datadir=/root/node_0 DEX_streamsub pony_8x01.mkv 0 01d259a49bb668ecdb709ee988a8e71cb106564eef0f26b581ec2e2f5c0cfcd57f
done
