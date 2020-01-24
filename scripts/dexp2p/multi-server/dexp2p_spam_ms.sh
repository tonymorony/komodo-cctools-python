#!/bin/bash

end=$((SECONDS+$3))
i=0

while [ $SECONDS -lt $end ]; do
  let "c = $i % 10"
  if (( $c == 0 ))
  then
  curl --user test:test --data-binary '{"jsonrpc": "1.0", "id":"curltest", "method": "DEX_broadcast", "params": ["ffff", "0", "'"$1"'", "", "", "0.1", "100"] }' -H 'content-type: text/plain;' http://127.0.0.1:$1/ >> spam_p2p/packages/$2_$1_packages.txt
  sleep 1
  i=$((i+1))
  else
  curl --user test:test --data-binary '{"jsonrpc": "1.0", "id":"curltest", "method": "DEX_broadcast", "params": ["ffff", "0", "'"$1"'", "", "", "0.1", "100"] }' -H 'content-type: text/plain;' http://127.0.0.1:$1/ >> spam_p2p/packages/$2_$1_packages.txt
  i=$((i+1))
  fi
done
