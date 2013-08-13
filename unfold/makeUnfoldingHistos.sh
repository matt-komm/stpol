#!/bin/bash

STEP3_PATH=/hdfs/local/stpol/step3/Jul26_MVA_multivar_v1/

#channel="mu"
for i in {-25..40} 
do
        j=$(echo "scale=2; $i /50" | bc)
        fn="/tmp/$USER/unfoldhistos_mva_mu_$j.sh"
        echo "#!/bin/bash" > $fn
        #echo "unset DISPLAY" >> $fn
        #echo "Hostname: `echo $HOSTNAME`" >> $fn
        echo "mkdir -p /tmp/$USER" >> $fn
        echo "source $STPOL_DIR/setenv.sh" >> $fn
        com="python prepare_unfolding.py --path=$STEP3_PATH --channel=mu --cut=$j"
        echo "$com" >> $fn
        chmod 755 $fn
        sbatch $fn
        echo "$fn"
done

#channel="ele"
for i in {-25..40}
do
        j=$(echo "scale=2; $i /50" | bc)
        fn="/tmp/$USER/unfoldhistos_mva_ele_$j.sh"
        echo "#!/bin/bash" > $fn
        #echo "unset DISPLAY" >> $fn
        #echo "Hostname: `echo $HOSTNAME`" >> $fn
        echo "mkdir -p /tmp/$USER" >> $fn
        echo "source $STPOL_DIR/setenv.sh" >> $fn
        com="python prepare_unfolding.py --path=$STEP3_PATH --channel=ele --cut=$j"
        echo "$com" >> $fn
        chmod 755 $fn
        sbatch $fn
        echo "$fn"
done
