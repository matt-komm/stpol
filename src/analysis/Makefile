include ../analysis/Makefile.options

INDIR=/hdfs/local/joosep/stpol/skims/chunked
OFDIR=/home/joosep/singletop/output/batch

.PHONY: hists

hists:
	rm -Rf $(OFDIR)/hists
	mkdir -p $(OFDIR)/hists
	find $(INDIR) -name "*.root" | $(PARCMD) -j32 ./evloop.jl {} $(OFDIR)/hists/hist.{#}.jld > $(OFDIR)/log.txt

hists-jobfiles:
	mkdir -p $(OFDIR)/hists
	find $(INDIR) -name "*.root" | ../skim/createscript.jl "./evloop.jl {} $(OFDIR)/hists/hist.{#}.jld" hists-evloop
	sh hists-evloop.submit.sh

merge-data:
	find $(DIR) -name "*.root" | $(PARCMD) -n10 -j32 $(JULIA_ROOT_DIR)/julia mergedf.jl $(DIR)/merged/md.txt {}

merge-mva:
	$(JULIA_ROOT_DIR)/julia -F mvamerge.jl /scratch/joosep/mva.root /scratch/joosep/skim_jan31_2/output*.jld

submit-scan:
	find input/hists -name "*.json" | ~/parallel --delay 0.1 sbatch --exclude=../skim/exclude.txt parrun.sh {}

project-nominal:
	#find $(DIR) -name "output*.root" | ~/parallel -j100 srun -p prio --exclude=../skim/exclude.txt $(JULIA_ROOT_DIR)/julia project_nominal.jl {} {}.nominal
	find $(DIR) -name "output*.root" | ~/parallel -j32 $(JULIA_ROOT_DIR)/julia project_nominal.jl {} {}.nominal

project-tchan:
	find $(DIR) -name "output*.root" | ~/parallel -j100 srun -p prio --exclude=../skim/exclude.txt $(JULIA_ROOT_DIR)/julia project_tchan.jl {} {}.tchan

test-merge:
	$(JULIA_ROOT_DIR)/julia mergedf.jl test $(DIR)/merged/md.txt $(DIR)/output_1.jld  $(DIR)/output_2.jld

test-evloop:
	julia evloop.jl input/bdt_scan/test.json

recursive-hadd:
	rm -Rf hadd/*
	mkdir -p hadd/step1
	#$(ROOTWRAP) && ( cat files.txt | $(PARCMD) -n10 hadd hadd/step1/merged_{#}.root {} )
	$(ENVSCRIPT) &
	mkdir -p hadd/step2
	$(ENVSCRIPT) && ( find hadd/step1 -name "merged_*.root" | $(PARCMD) -n5 hadd hadd/step2/merged_{#}.root {} )
	$(ENVSCRIPT) && hadd hadd/merged.root hadd/step2/merged_*.root
	rm -Rf hadd/step1
	rm -Rf hadd/step2

convert-hists:
	rm -Rf output/bdt_scan
	$(ROOTWRAP) && python histmerge.py hadd/merged.root

conv2root:
	find ~/singletop/output/skims/skim_merged -name "*.jld" | ~/parallel $(JULIA_ROOT_DIR)/julia ../skim/conv2root.jl {} ~/singletop/output/skims/skim_root/{/.}.root


merge:
	rm -Rf output

	mkdir -p results/csvt/qcd__metmtw_nominal
	python histmerge.py ../../results/hists/apr03/hists/csvt/qcd__metmtw_nominal/merged.root
	mv output/bdt_scan/* results/csvt/qcd__metmtw_nominal

	mkdir -p results/csvt/qcd__mva_nominal
	python histmerge.py ../../results/hists/apr03/hists/csvt/qcd__mva_nominal/merged.root
	mv output/bdt_scan/* results/csvt/qcd__mva_nominal

	mkdir -p results/tchpt/qcd__metmtw_nominal
	python histmerge.py ../../results/hists/apr03/hists/tchpt/qcd__metmtw_nominal/merged.root
	mv output/bdt_scan/* results/tchpt/qcd__metmtw_nominal

	mkdir -p results/tchpt/qcd__mva_nominal
	python histmerge.py ../../results/hists/apr03/hists/tchpt/qcd__mva_nominal/merged.root
	mv output/bdt_scan/* results/tchpt/qcd__mva_nominal

recursive-hadd: recursive-hadd-1 recursive-hadd-2 recursive-hadd-3 recursive-hadd-4
recursive-hadd-1:
	./recursive-hadd.sh /hdfs/local/joosep/stpol/hists/Apr02_B/qcd__metmtw_nominal/skims_step3/apr1/csvt/ /scratch/joosep/hists/csvt/qcd__metmtw_nominal

recursive-hadd-2:
	./recursive-hadd.sh /hdfs/local/joosep/stpol/hists/Apr02_B/qcd__mva_nominal/skims_step3/apr1/csvt/ /scratch/joosep/hists/csvt/qcd__mva_nominal

recursive-hadd-3:
	./recursive-hadd.sh /hdfs/local/joosep/stpol/hists/Apr02_B/qcd__metmtw_nominal/skims_step3/apr1/tchpt/ /scratch/joosep/hists/tchpt/qcd__metmtw_nominal

recursive-hadd-4:
	./recursive-hadd.sh /hdfs/local/joosep/stpol/hists/Apr02_B/qcd__mva_nominal/skims_step3/apr1/tchpt/ /scratch/joosep/hists/tchpt/qcd__mva_nominal
