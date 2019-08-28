#!/bin/bash

while :
do
  curl -s --user test:test --data-binary '{"jsonrpc": "2.0", "id":"curltest", "method": "getinfo", "params": [] }' -H 'content-type: text/plain;' http://127.0.0.1:$1/ &> curl-output.txt
  curl -s --user test:test --data-binary '{"jsonrpc": "2.0", "id":"curltest", "method": "listunspent", "params": ["RQ1mvCUcziWzRwE8Ugtex29VjoFjRzxQJT"] }' -H 'content-type: text/plain;' http://127.0.0.1:$1 &> curl-output.txt
  curl -s --user test:test --data-binary '{"jsonrpc": "2.0", "id":"curltest", "method": "notarizations", "params": ["2000"] }' -H 'content-type: text/plain;' http://127.0.0.1:$1 &> curl-output.txt
  curl -s --user test:test --data-binary '{"jsonrpc": "2.0", "id":"curltest", "method": "spentinfo", "params": ["67ffe0eaecd6081de04675c492a59090b573ee78955c4e8a85b8ac0be0e8e418", "1"] }' -H 'content-type: text/plain;' http://127.0.0.1:$1 &> curl-output.txt
  curl -s --user test:test --data-binary '{"jsonrpc": "2.0", "id":"curltest", "method": "txproof", "params": ["67ffe0eaecd6081de04675c492a59090b573ee78955c4e8a85b8ac0be0e8e418", "2673"] }' -H 'content-type: text/plain;' http://127.0.0.1:$1 &> curl-output.txt
done
