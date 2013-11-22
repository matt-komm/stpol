
include ../analysis/Makefile.options

DIR=skim_output

skim:
	test ! -d $(DIR) || ( echo "Output diretory $(DIR) already exists" && exit 1 )
	julia sub.jl $(DIR) input/oct18.txt
	until julia summary.jl $(DIR); do echo "."; done; echo "skim is done"

add_mva:
	$(ROOTWRAP) && ( find $(DIR) -name "*.root" | sort | ~/parallel $(PAROPTS) python ../mva/adder.py bdt_sig_bg ../mva/weights/stpol_bdt_sig_bg_lepton_flavour.weights.xml {} )
	$(ROOTWRAP) && ( find $(DIR) -name "*.root" | sort | ~/parallel $(PAROPTS) python ../mva/adder.py bdt_sig_bg1 ../mva/weights/stpol_bdt_sig_wjets_lepton_flavour.weights.xml {} )
	$(ROOTWRAP) && ( find $(DIR) -name "*.root" | sort | ~/parallel $(PAROPTS) python ../mva/adder.py bdt_sig_bg2 ../mva/weights/stpol_bdt_sig_ttjets_lepton_flavour.weights.xml {} )
	$(ROOTWRAP) && ( find $(DIR) -name "*.root" | sort | ~/parallel $(PAROPTS) python ../mva/adder.py bdt_bg1_bg2 ../mva/weights/stpol_bdt_wjets_ttjets_lepton_flavour.weights.xml {} )

hadd:
	find $(DIR) -name "*.root" > files.txt
	./hadd.jl files.txt $(DIR).jld
