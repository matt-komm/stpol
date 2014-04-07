include ../analysis/Makefile.options

#INF=input/mar17.txt.rand
INF=input/tchpt.txt.rand
WEIGHTSDIR=../mva/weights/

.PHONY: comphep

skim:
	rm ~/singletop/output/skims/output/*
	test ! -d $(DIR) || ( echo "Output diretory $(DIR) already exists" && exit 1 )
	julia sub.jl $(DIR) $(INF)
	until julia summary.jl ~/singletop/output/skims/output/*; do echo "."; done; echo "skim is done"
	echo "skim is done" | sendmail $(EMAIL)

skimsummary:
	julia summary.jl $(DIR) --list

comphep:
	test ! -d comphep || ( echo "Output diretory comphep already exists" && exit 1 )
	source $(ENVSCRIPT) && julia sub.jl comphep input/comphep.txt
	until julia summary.jl comphep; do echo "."; done; echo "skim is done"
	mkdir -p comphep/merged
	$(ROOTWRAP) && python ../mva/adder.py bdt_sig_bg $(WEIGHTSDIR)/stpol_bdt_sig_bg_lepton_flavour.weights.xml comphep/*.root 
	find comphep -name "*.root" > comphep/merged/files.txt
	julia metahadd.jl comphep/merged/files.txt comphep/merged/md.txt $(INF)

conv2root:
	find $(DIR) -name "*.jld" | sort | ~/parallel $(PAROPTS) -j60 -n1 ~/.julia/ROOT/julia conv2root.jl {} {.}.root

add-mva:
	find $(DIR) -name "*.root" | xargs -n5 | julia createscript.jl "$(ROOTWRAP) && ( python ../mva/adder.py bdt_sig_bg $(WEIGHTSDIR)/stpol_bdt_sig_bg_lepton_flavour.weights.xml {} )" mva.sig_bg
	find $(DIR) -name "*.root" | xargs -n5 | julia createscript.jl "$(ROOTWRAP) && ( python ../mva/qcd_mva_adder.py {} )" mva.qcd
	find $(DIR) -name "*.root" | xargs -n5 | julia createscript.jl "$(ROOTWRAP) && ( python ../mva/qcd_mva_adder2.py {} )" mva.qcd2
	find $(DIR) -name "*.root" | xargs -n5 | julia createscript.jl "$(ROOTWRAP) && ( python ../mva/top_13_001_mva_adder.py {} )" mva.top_13_001

add-mva2:
	cat input/combined | julia createscript.jl "$(ROOTWRAP) && ( python ../mva/adder.py bdt_sig_bg $(WEIGHTSDIR)/stpol_bdt_sig_bg_lepton_flavour.weights.xml {} )" mva.sig_bg
	cat input/combined | julia createscript.jl "$(ROOTWRAP) && ( python ../mva/qcd_mva_adder.py {} )" mva.qcd
	cat input/combined | julia createscript.jl "$(ROOTWRAP) && ( python ../mva/qcd_mva_adder2.py {} )" mva.qcd2
	cat input/combined | julia createscript.jl "$(ROOTWRAP) && ( python ../mva/top_13_001_mva_adder.py {} )" mva.top_13_001

metahadd-csvt:
	find /hdfs/local/joosep/stpol/skims/Apr04/step3/csvt/ -name "*.root" > csvt.txt
	julia metahadd.jl csvt.txt md.csvt.json input/mar17.txt &> md.csvt.out

metahadd-tchpt:
	find /hdfs/local/joosep/stpol/skims/Apr04/step3/tchpt/ -name "*.root" > tchpt.txt
	julia metahadd.jl tchpt.txt md.tchpt.json input/tchpt.txt &> md.tchpt.out

metahadd:
	mkdir -p $(DIR)/merged
	find $(DIR) -name "*.root" > ~/singletop/output/files.txt
	julia metahadd.jl ~/singletop/output/files.txt $(DIR)/merged/md.txt $(INF) > $(DIR)/merged/metahadd.out

parhadd:
	mkdir -p $(DIR)/merged
	find $(DIR) -name "*.root" > $(DIR)/merged/files.txt
	julia metahadd.jl $(DIR)/merged/files.txt $(DIR)/merged/md.txt > $(DIR)/merged/metahadd.out
	split -a5 -l3 $(DIR)/merged/files.txt $(DIR)/merged/files.split.
	#echo "hadding in parallel"
	#find $(DIR)/merged/ -name "files.split.*" | $(PARCMD) -j32 ./hadd.jl {} $(DIR)/merged/md.txt $(DIR)/merged/$(DIR).{#} > $(DIR)/merged/hadd.out	
	echo "hadding on cluster"
	find $(DIR) -name "files.split*" | julia createscript.jl "./hadd.jl {} $(DIR)/merged/md.txt skim_jan14/merged/data.{#}" hadd
	sh hadd.submit.sh

hadd:
	$(ROOTWRAP) && hadd data.nominal.tagged.root $(DIR)/merged/data.*.root.nominal.1T $(DIR)/merged/data.*.root.unknown.1T $(DIR)/merged/data.*.root.nominal.2T $(DIR)/merged/data.*.root.unknown.2T
	$(ROOTWRAP) && hadd data.nominal.untagged.root $(DIR)/merged/data.*.root.nominal.0T $(DIR)/merged/data.*.root.unknown.0T
	rm -Rf $(DIR)/chunked
	mkdir $(DIR)/chunked
	$(ROOTWRAP) && ( find $(DIR)/merged -name "*.root.*" | $(PARCMD) -n100 -j32 hadd $(DIR)/chunked/data.{#}.root {} )
	~/.julia/ROOT/julia conv.jl data.nominal.tagged.root data.nominal.tagged.jld
	~/.julia/ROOT/julia conv.jl data.nominal.untagged.root data.nominal.untagged.jld

gjets_tchpt:
	mkdir -p output/gjets_tchpt
	~/.julia/ROOT/julia skim.jl output/gjets_tchpt/gjets `cat input/gjets_tchpt.txt`
	find output/gjets_tchpt -name "*.root" > output/gjets_tchpt/files.txt
	julia metahadd.jl output/gjets_tchpt/files.txt output/gjets_tchpt/gjets.md.txt
	~/.julia/ROOT/julia hadd.jl output/gjets_tchpt/files.txt output/gjets_tchpt/gjets.md.txt output/gjets_tchpt/gjets 

gjets:
	rm -Rf output/gjets; mkdir -p output/gjets
	~/.julia/ROOT/julia skim.jl output/gjets/gjets `cat input/gjets1.txt` > output/gjets/skim.txt
	find output/gjets -name "*.root" > output/gjets/files.txt
	julia metahadd.jl output/gjets/files.txt output/gjets/gjets.md.txt
	~/.julia/ROOT/julia hadd.jl output/gjets/files.txt output/gjets/gjets.md.txt output/gjets/gjets > output/gjets/hadd.txt 

gjets_strange:
	rm -Rf output/gjets_strange; mkdir -p output/gjets_strange
	~/.julia/ROOT/julia skim.jl output/gjets_strange/gjets `cat input/gjets.txt.strange` > output/gjets_strange/skim.txt
	find output/gjets_strange -name "*.root" > output/gjets_strange/files.txt
	julia metahadd.jl output/gjets_strange/files.txt output/gjets_strange/gjets.md.txt
	~/.julia/ROOT/julia hadd.jl output/gjets_strange/files.txt output/gjets_strange/gjets.md.txt output/gjets_strange/gjets > output/gjets_strange/hadd.txt 

skim_strange:
	rm -Rf output/skim_strange; mkdir -p output/strange
	~/.julia/ROOT/julia skim.jl output/strange/out.1 `cat files.txt.sorted.1` &> output/strange/skim.txt
	~/.julia/ROOT/julia skim.jl output/strange/out.2 `cat files.txt.sorted.2` &> output/strange/skim.txt
	~/.julia/ROOT/julia skim.jl output/strange/out.3 `cat files.txt.sorted.3` &> output/strange/skim.txt
	find output/strange -name "*.root" > output/strange/files.txt
	julia metahadd.jl output/strange/files.txt output/strange/md.txt
	~/.julia/ROOT/julia hadd.jl output/strange/files.txt output/strange/md.txt output/strange/output &> output/strange/hadd.txt 

combine_inputs:
	find ~/singletop/stpol/filelists/Nov29_tW_etabl_CSVT_genwhgt_2fdd84/ -name "*.txt" -exec cat {} > input/comb.txt \;
	find ~/singletop/stpol/filelists/Dec6_anom_42ccfd/ -name "*.txt" -exec cat {} >> input/comb.txt \;



