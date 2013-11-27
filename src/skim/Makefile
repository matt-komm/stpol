
include ../analysis/Makefile.options

DIR=skim_output
WEIGHTSDIR=../mva/weights/
ENVSCRIPT=../../setenv.sh
skim:
	test ! -d $(DIR) || ( echo "Output diretory $(DIR) already exists" && exit 1 )
	source $(ENVSCRIPT) && julia sub.jl $(DIR) input/oct18.txt
	until julia summary.jl $(DIR); do echo "."; done; echo "skim is done"

add_mva:
	$(ROOTWRAP) && ( find $(DIR) -name "*.root" | sort | ~/parallel $(PAROPTS) python ../mva/adder.py bdt_sig_bg  $(WEIGHTSDIR)/stpol_bdt_sig_bg_lepton_flavour.weights.xml {} )
	$(ROOTWRAP) && ( find $(DIR) -name "*.root" | sort | ~/parallel $(PAROPTS) python ../mva/adder.py bdt_sig_bg1 $(WEIGHTSDIR)/stpol_bdt_sig_wjets_lepton_flavour.weights.xml {} )
	$(ROOTWRAP) && ( find $(DIR) -name "*.root" | sort | ~/parallel $(PAROPTS) python ../mva/adder.py bdt_sig_bg2 $(WEIGHTSDIR)/stpol_bdt_sig_ttjets_lepton_flavour.weights.xml {} )
	$(ROOTWRAP) && ( find $(DIR) -name "*.root" | sort | ~/parallel $(PAROPTS) python ../mva/adder.py bdt_bg1_bg2 $(WEIGHTSDIR)/stpol_bdt_wjets_ttjets_lepton_flavour.weights.xml {} )

hadd:
	find $(DIR) -name "*.root" > files.txt
	./hadd.jl files.txt $(DIR)

parhadd:
	find $(DIR) -name "*.root" > files.txt
	split -a5 -l10 files.txt files.split.
	find . -name "files.split.*" | $(PARCMD) ./hadd.jl {} $(DIR).{#}

gjets:
	mkdir -p output/gjets
	~/.julia/ROOT/julia skim.jl output/gjets/gjets `cat input/gjets.txt`
	find output/gjets -name "*.root" > output/gjets/files.txt
	~/.julia/ROOT/julia hadd.jl output/gjets/files.txt output/gjets/gjets.jld 
