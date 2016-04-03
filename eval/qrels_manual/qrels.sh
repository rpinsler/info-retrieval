#!/bin/bash
for N in {1..10}
do
   cp qrels.txt qrels_$N.txt
   sed -i -- "s/TOPIC_NUM/$N/" qrels_$N.txt
done
