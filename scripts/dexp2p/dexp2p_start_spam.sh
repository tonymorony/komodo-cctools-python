#!/bin/bash

i=7000
j=$(($i+$NODESAMOUNT-1))

while [ $i -le $j ]
do
  ./dexp2p_spam.sh $i &
  ((i++))
done