#!/bin/bash

STEP3_PATH=/hdfs/local/stpol/step3/Aug4_0eb863_full_with_Jul29_MVA/

#channel="mu"
for i in {-50..70} 
do
        j=$(echo "scale=2; $i /100" | bc)
        fn="/tmp/$USER/unfoldhistos_mva_mu_$j.sh"
        echo "#!/bin/bash" > $fn
        #echo "unset DISPLAY" >> $fn
        #echo "Hostname: `echo $HOSTNAME`" >> $fn
        echo "mkdir -p /tmp/$USER" >> $fn
        echo "source $STPOL_DIR/setenv.sh" >> $fn
        com="python prepare_unfolding.py --path=$STEP3_PATH --channel=mu --cut=$j --extra=new_syst"
        echo "$com" >> $fn
        chmod 755 $fn
        sbatch $fn
        echo "$fn"
done

for i in {-50..70} 
do
        j=$(echo "scale=2; $i /100" | bc)
        fn="/tmp/$USER/unfoldhistos_mva_ele_$j.sh"
        echo "#!/bin/bash" > $fn
        #echo "unset DISPLAY" >> $fn
        #echo "Hostname: `echo $HOSTNAME`" >> $fn
        echo "mkdir -p /tmp/$USER" >> $fn
        echo "source $STPOL_DIR/setenv.sh" >> $fn
        com="python prepare_unfolding.py --path=$STEP3_PATH --channel=ele --cut=$j --extra=new_syst"
        echo "$com" >> $fn
        chmod 755 $fn
        sbatch $fn
        echo "$fn"
done
