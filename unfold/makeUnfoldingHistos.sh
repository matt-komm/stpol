#!/bin/bash

#com="python prepare_unfolding.py --path /hdfs/local/stpol/step3/Jul26_MVA_multivar_v1/ --channel=ele --mva_cut=$j --mva --mva_var=mva_BDT_with_top_mass_C_eta_lj_el_pt_mt_el_pt_bj_mass_bj_met_mass_lj"

STEP3_PATH=/hdfs/local/stpol/step3/Jul26_MVA_multivar_v1/

channel="mu"
for i in {1..2} 
do
        j=$(echo "scale=2; $i /100" | bc)
        fn=/tmp/unfoldhistos_mva_mu_$j.sh
        echo "#!/bin/bash" > $fn
        echo "source $STPOL_DIR/setenv.sh" >> $fn
        com="python prepare_unfolding.py --path=$STEP3_PATH --channel=mu --mva_cut=$j --mva --mva_var=mva_BDT_with_top_mass_eta_lj_C_mu_pt_mt_mu_met_mass_bj_pt_bj_mass_lj"
        echo "$com" >> $fn
        chmod 755 $fn
        sbatch $fn
        echo "$fn"
done
