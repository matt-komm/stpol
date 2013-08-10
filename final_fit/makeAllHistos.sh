#!/bin/bash
#fn=/tmp/`basename $i`.sh
fn=/tmp/testhistos2.sh
com="python $STPOL_DIR/final_fit/makehistos.py --path=/hdfs/local/stpol/step3/Jul26_MVA_multivar_v1/ --channel=ele --var=mva_BDT_with_top_mass_C_eta_lj_el_pt_mt_el_pt_bj_mass_bj_met_mass_lj --asymmetry=0.3"

#TODO implement various different settings

echo "#!/bin/bash" > $fn
#echo "env" >> $fn
echo "source $STPOL_DIR/setenv.sh" >> $fn
echo "$com" >> $fn
chmod 755 $fn
sbatch $fn
echo "$fn"

