#!/bin/sh

LEP_CH="mu"
INDIR=$STPOL_DIR"/step3_aug22/"$LEP_CH

cd $INDIR
ls *.root>$STPOL_DIR/iso_sys_weights/infiles.txt
cd -

while read -r line
do
  echo "running on file: "$line
  sh run_iso_weights.sh $line $LEP_CH
done < infiles.txt