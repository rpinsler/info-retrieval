#!/bin/bash
> qrels_1-10
for N in {1..10}
do
   cat qrels_$N >> qrels_1-10
done
