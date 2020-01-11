#!/bin/bash

i=7000

while [ $i -le 7100 ]
do
  ./dexp2p_spam.sh $i &
  ((i++))
done
