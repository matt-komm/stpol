#!/bin/bash
for i in `cat filelist`; 
do 
   sed "s+FILE+$i+g" template > tmp.sh
   chmod 755 tmp.sh
   sbatch -p prio --comment "`basename $i`" tmp.sh
done
