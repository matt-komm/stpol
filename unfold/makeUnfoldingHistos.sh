#!/bin/bash

STEP3_PATH=/hdfs/local/stpol/step3/Jul26_MVA_multivar_v1/

channel="mu"
for i in {0..80} 
do
        j=$(echo "scale=2; $i /100" | bc)
        fn=/tmp/$USER/unfoldhistos_mva_$channel_$j.sh
        echo "#!/bin/bash" > $fn
        #echo "unset DISPLAY" >> $fn
        #echo "Hostname: `echo $HOSTNAME`" >> $fn
        echo "mkdir -p /tmp/$USER" >> $fn
        echo "source $STPOL_DIR/setenv.sh" >> $fn
        com="python prepare_unfolding.py --path=$STEP3_PATH --channel=mu --mva_cut=$j --mva --mva_var=mva_BDT_with_top_mass_eta_lj_C_mu_pt_mt_mu_met_mass_bj_pt_bj_mass_lj"
        echo "$com" >> $fn
        chmod 755 $fn
        sbatch $fn
        echo "$fn"
done

channel="ele"
for i in {0..80}
do
        j=$(echo "scale=2; $i /100" | bc)
        fn=/tmp/$USER/unfoldhistos_mva_$channel_$j.sh
        echo "#!/bin/bash" > $fn
        #echo "unset DISPLAY" >> $fn
        #echo "Hostname: `echo $HOSTNAME`" >> $fn
        echo "mkdir -p /tmp/$USER" >> $fn
        echo "source $STPOL_DIR/setenv.sh" >> $fn
        com="python prepare_unfolding.py --path=$STEP3_PATH --channel=mu --mva_cut=$j --mva --mva_var=mva_BDT_with_top_mass_C_eta_lj_el_pt_mt_el_pt_bj_mass_bj_met_mass_lj"
        echo "$com" >> $fn
        chmod 755 $fn
        sbatch $fn
        echo "$fn"
done
