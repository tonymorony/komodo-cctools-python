#!/bin/bash

end=$((SECONDS+180))

while [ $SECONDS -lt $end ]; do
  TEST="$2"_$(( ( RANDOM % 1000000 )  + 1 ))
  curl --user test:test --data-binary '{"jsonrpc": "1.0", "id":"curltest", "method": "DEX_broadcast", "params": ["'"$TEST"'", "0", "'"$1"'", "", "", "0.1", "100"] }' -H 'content-type: text/plain;' http://127.0.0.1:$1/ >> spam_p2p/packages/$2_$1_packages.txt
done
