
include ../analysis/Makefile.options

DIR=nov8

do_skim:
	julia sub.jl skim_output input/oct18.txt

add_mva:
	find $(DIR) -name "*.root" | sort | ~/parallel $(PAROPTS) python ../mva/adder.py bdt_sig_bg ../mva/weights/stpol_bdt_sig_bg_lepton_flavour.weights.xml {}
	find $(DIR) -name "*.root" | sort | ~/parallel $(PAROPTS) python ../mva/adder.py bdt_sig_bg1 ../mva/weights/stpol_bdt_sig_wjets_lepton_flavour.weights.xml {}
	find $(DIR) -name "*.root" | sort | ~/parallel $(PAROPTS) python ../mva/adder.py bdt_sig_bg2 ../mva/weights/stpol_bdt_sig_ttjets_lepton_flavour.weights.xml {}
	find $(DIR) -name "*.root" | sort | ~/parallel $(PAROPTS) python ../mva/adder.py bdt_bg1_bg2 ../mva/weights/stpol_bdt_wjets_ttjets_lepton_flavour.weights.xml {}

hadd:
	find $(DIR) -name "*.root" > files.txt
	./hadd.jl files.txt $(DIR).csv 
