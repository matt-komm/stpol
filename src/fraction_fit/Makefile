copies:
	./copy_cfgs.sh fitconfigs/bdt/mu/nominal.cfg
	rm -Rf fitconfigs/bdt/ele	
	cp -R fitconfigs/bdt/mu fitconfigs/bdt/ele
	sed -i '' 's/mu__mva_BDT_with_top_mass_eta_lj_C_mu_pt_mt_mu_met_mass_bj_pt_bj_mass_lj__final/ele__mva_BDT_with_top_mass_C_eta_lj_el_pt_mt_el_pt_bj_mass_bj_met_mass_lj__final/g' fitconfigs/bdt/ele/*.cfg
	sed -i '' 's/mu/ele/g' fitconfigs/bdt/ele/*.cfg
	./copy_cfgs.sh fitconfigs/bdt/combined/nominal.cfg
	
	./copy_cfgs.sh fitconfigs/abs_ljet_eta/mu/nominal.cfg
	rm -Rf fitconfigs/abs_ljet_eta/ele	
	cp -R fitconfigs/abs_ljet_eta/mu fitconfigs/abs_ljet_eta/ele
	sed -i '' 's/mu/ele/g' fitconfigs/abs_ljet_eta/ele/*.cfg
	./copy_cfgs.sh fitconfigs/abs_ljet_eta/combined/nominal.cfg

fit_all:
	find fitconfigs/bdt -name "*.cfg" -exec ./runtheta.sh bgfit.py {} \;
