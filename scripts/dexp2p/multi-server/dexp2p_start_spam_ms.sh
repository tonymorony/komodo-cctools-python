# server IP as argument

#!/bin/bash

i=7000
j=$(($i+$NODESAMOUNT-1))

while [ $i -le $j ]
do
  ./dexp2p_spam_ms.sh $i $1 $2 &
  ((i++))
done