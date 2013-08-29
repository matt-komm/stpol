#!/bin/bash

STEP3_PATH=/hdfs/local/stpol/step3/37acf5_343e0a9_Aug22/

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
        com="python prepare_unfolding.py --path=$STEP3_PATH --channel=mu --cut=$j --extra=no_metphi"
        echo "$com" >> $fn
        chmod 755 $fn
        sbatch -p prio $fn
        echo "$fn"
        sleep 1
done

sleep 100

#channel="mu"
for i in {-50..70} 
do
        j=$(echo "scale=2; $i /100" | bc)
        fn="/tmp/$USER/unfoldhistos_mva_mu_comphep_$j.sh"
        echo "#!/bin/bash" > $fn
        #echo "unset DISPLAY" >> $fn
        #echo "Hostname: `echo $HOSTNAME`" >> $fn
        echo "mkdir -p /tmp/$USER" >> $fn
        echo "source $STPOL_DIR/setenv.sh" >> $fn
        com="python prepare_unfolding.py --path=$STEP3_PATH --channel=mu --cut=$j --extra=no_metphi --coupling=comphep"
        echo "$com" >> $fn
        chmod 755 $fn
        sbatch -p prio $fn
        echo "$fn"
        sleep 1
done

sleep 100

#channel="ele"
for i in {-50..70} 
do
        j=$(echo "scale=2; $i /100" | bc)
        fn="/tmp/$USER/unfoldhistos_mva_ele_$j.sh"
        echo "#!/bin/bash" > $fn
        #echo "unset DISPLAY" >> $fn
        #echo "Hostname: `echo $HOSTNAME`" >> $fn
        echo "mkdir -p /tmp/$USER" >> $fn
        echo "source $STPOL_DIR/setenv.sh" >> $fn
        com="python prepare_unfolding.py --path=$STEP3_PATH --channel=ele --cut=$j --extra=no_metphi"
        echo "$com" >> $fn
        chmod 755 $fn
        sbatch -p prio $fn
        echo "$fn"
        sleep 1
done

sleep 100

#channel="ele"
for i in {-50..70} 
do
        j=$(echo "scale=2; $i /100" | bc)
        fn="/tmp/$USER/unfoldhistos_mva_ele_comphep_$j.sh"
        echo "#!/bin/bash" > $fn
        #echo "unset DISPLAY" >> $fn
        #echo "Hostname: `echo $HOSTNAME`" >> $fn
        echo "mkdir -p /tmp/$USER" >> $fn
        echo "source $STPOL_DIR/setenv.sh" >> $fn
        com="python prepare_unfolding.py --path=$STEP3_PATH --channel=ele --cut=$j --extra=no_metphi --coupling=comphep"
        echo "$com" >> $fn
        chmod 755 $fn
        sbatch -p prio $fn
        echo "$fn"
        sleep 1
done
