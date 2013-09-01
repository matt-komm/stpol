RESDIR=$(STPOL_DIR)/results/gen_level_cos_theta

hists: WD_mass WD_nomass
	./hists.py hmass.root WD_mass/out*.root
	./hists.py hnomass.root WD_nomass/out*.root

copyres: hmass.root hnomass.root
	mkdir -p $(RESDIR)
	cp hmass.root $(RESDIR)/
	cp hnomass.root $(RESDIR)/
