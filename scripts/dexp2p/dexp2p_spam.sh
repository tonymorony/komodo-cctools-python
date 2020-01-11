#!/bin/bash

end=$((SECONDS+180))

while [ $SECONDS -lt $end ]; do
  TEST=$(( ( RANDOM % 1000000 )  + 1 ))
  curl -s --user test:test --data-binary '{"jsonrpc": "1.0", "id":"curltest", "method": "DEX_broadcast", "params": ["'"$TEST"'", "0", "'"$1"'", "", "", "0.1", "100"] }' -H 'content-type: text/plain;' http://127.0.0.1:$1/ > curl-output.txt
done
