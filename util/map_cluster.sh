#!/bin/bash

while read line
do
    sbatch -p prio $1 $line
done
