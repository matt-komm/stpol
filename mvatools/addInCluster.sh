#!/bin/bash
if [ "x$1" == "x" ]; then
	echo "Usage: ./addInCluster.sh step3_directory"
	exit 1
fi
step3=$1
find $step3 -name "*root" > filelist
for i in `cat filelist`; 
do 
   ch='ele'
   if [ `echo $i|grep 'mu'|wc -l` -eq 1 ]; then
	  ch='mu'
   fi
   #fn=`basename $i`.sh
   fn=MVA_ADD.sh
   sed "s+FILE+$i+g;s+CHAN+$ch+g" template > $fn
   chmod 755 $fn
   sbatch -p prio $fn
done
