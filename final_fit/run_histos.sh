python makehistos.py --path=/hdfs/local/stpol/step3/Jul26_MVA_multivar_v1/ --channel=mu --var=mva_BDT_with_top_mass_eta_lj_C_mu_pt_mt_mu_met_mass_bj_pt_bj_mass_lj
python makehistos.py --path=/hdfs/local/stpol/step3/Jul26_MVA_multivar_v1/ --channel=ele --var=mva_BDT_with_top_mass_C_eta_lj_el_pt_mt_el_pt_bj_mass_bj_met_mass_lj

python makehistos.py --path=/hdfs/local/stpol/step3/Jul26_MVA_multivar_v1/ --channel=mu --var=C
python makehistos.py --path=/hdfs/local/stpol/step3/Jul26_MVA_multivar_v1/ --channel=ele --var=C

python makehistos.py --path=/hdfs/local/stpol/step3/Jul26_MVA_multivar_v1/ --channel=mu
python makehistos.py --path=/hdfs/local/stpol/step3/Jul26_MVA_multivar_v1/ --channel=ele

python makehistos.py --path=/hdfs/local/stpol/step3/Jul26_MVA_multivar_v1/ --channel=mu --var=mva_BDT_with_top_mass_eta_lj_C_mu_pt_mt_mu_met_mass_bj_pt_bj_mass_lj --asymmetry=0.3
python makehistos.py --path=/hdfs/local/stpol/step3/Jul26_MVA_multivar_v1/ --channel=mu --var=mva_BDT_with_top_mass_eta_lj_C_mu_pt_mt_mu_met_mass_bj_pt_bj_mass_lj --asymmetry=0.1
python makehistos.py --path=/hdfs/local/stpol/step3/Jul26_MVA_multivar_v1/ --channel=ele --var=mva_BDT_with_top_mass_C_eta_lj_el_pt_mt_el_pt_bj_mass_bj_met_mass_lj --asymmetry=0.3
python makehistos.py --path=/hdfs/local/stpol/step3/Jul26_MVA_multivar_v1/ --channel=ele --var=mva_BDT_with_top_mass_C_eta_lj_el_pt_mt_el_pt_bj_mass_bj_met_mass_lj --asymmetry=0.1

