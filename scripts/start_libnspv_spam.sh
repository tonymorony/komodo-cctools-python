#!/bin/bash

i=7000

while [ $i -le 7100 ]
do
  ./libnspv_calls.sh $i &
  ((i++))
done
