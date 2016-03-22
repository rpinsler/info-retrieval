#!/bin/bash
for N in {1..10}
do
   cp qrels qrels_$N
   sed -i -- "s/TOPIC_NUM/$N/" qrels_$N
done
