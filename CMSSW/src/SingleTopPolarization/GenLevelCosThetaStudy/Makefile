RESDIR=$(STPOL_DIR)/results/gen_level_cos_theta

hists: hmass hnomass hmadgraph

hmass:
	./hists.py hmass.root WD_mass/out*.root

hnomass:
	./hists.py hnomass.root WD_nomass/out*.root
	
hmadgraph:
	./hists.py hmadgraph.root WD_madgraph/out*.root

copyres: hmass.root hnomass.root
	mkdir -p $(RESDIR)
	cp hmass.root $(RESDIR)/
	cp hnomass.root $(RESDIR)/
	cp hmadgraph.root $(RESDIR)/
