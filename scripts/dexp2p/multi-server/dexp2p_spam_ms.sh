#!/bin/bash

end=$((SECONDS+180))

while [ $SECONDS -lt $end ]; do
  TEST=$(( ( RANDOM % 1000000 )  + 1 ))
  curl --user test:test --data-binary '{"jsonrpc": "1.0", "id":"curltest", "method": "DEX_broadcast", "params": ["'"$TEST"'", "0", "'"$2_$1"'", "", "", "0.1", "100"] }' -H 'content-type: text/plain;' http://127.0.0.1:$1/ >> spam_p2p/packages/$2_$1_packages.txt
done

# getting orderbooks
servers_ips=("159.69.45.70", "95.217.44.58")

for server_ip in "${servers_ips[@]}"; do
  i=0
  j=$(($NODESAMOUNT*${#servers_ips[@]}-1))
  while [ $i -le $j ]
  do
    TAG="$server_ip"_"$(( 7000 + $i ))"
    curl --user test:test --data-binary '{"jsonrpc": "1.0", "id":"curltest", "method": "DEX_list", "params": [ "0", "0", "'"$TAG"'"] }' -H 'content-type: text/plain;' http://127.0.0.1:$1/ >> spam_p2p/orderbooks/$TAG.txt
    ((i++))
  done
done