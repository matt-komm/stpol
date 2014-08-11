copies:
	./copy_cfgs.sh fitconfigs/bdt/mu/nominal.cfg
	rm -Rf fitconfigs/bdt/ele	
	cp -R fitconfigs/bdt/mu fitconfigs/bdt/ele
	sed -i '' 's/mu/ele/g' fitconfigs/bdt/ele/*.cfg
	./copy_cfgs.sh fitconfigs/bdt/combined/nominal.cfg

fit_all:
	find fitconfigs/bdt -name "*.cfg" -exec ./runtheta.sh bgfit.py {} \;
