#!/bin/bash

i=7000

while [ $i -le 7250 ]
do
  ./nspv_calls.sh $i &
  ((i++))
done
