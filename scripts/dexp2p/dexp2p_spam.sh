#!/bin/bash

end=$((SECONDS+180))

while [ $SECONDS -lt $end ]; do
  TEST=$(( ( RANDOM % 1000000 )  + 1 ))
  curl --user test:test --data-binary '{"jsonrpc": "1.0", "id":"curltest", "method": "DEX_broadcast", "params": ["'"$TEST"'", "0", "'"$1"'", "", "", "0.1", "100"] }' -H 'content-type: text/plain;' http://127.0.0.1:$1/ >> spam_p2p/packages/node$1_packages.txt
done

# getting orderbooks
i=0
j=$(($NODESAMOUNT-1))
while [ $i -le $j ]
do
  TAG=$(( 7000 + $i ))
  curl --user test:test --data-binary '{"jsonrpc": "1.0", "id":"curltest", "method": "DEX_list", "params": [ "0", "0", "'"$TAG"'"] }' -H 'content-type: text/plain;' http://127.0.0.1:$1/ >> spam_p2p/orderbooks/node$1_tag_$TAG.txt
  ((i++))
done
