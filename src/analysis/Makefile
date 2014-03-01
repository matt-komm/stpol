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

merge:
	rm -Rf $(OFDIR)/merged
	mkdir -p $(OFDIR)/merged
	find $(OFDIR)/hists -name "*hist.*.jld.*" | $(PARCMD) -n10 -j32 ./merge.jl $(OFDIR)/merged/hist.{#}.jld {} > $(OFDIR)/merged/log.txt
	./merge.jl merged.jld $(OFDIR)/merged/*.jld

merge-data:
	find $(DIR) -name "*.root" | $(PARCMD) -n10 -j32 $(JULIA_ROOT_DIR)/julia mergedf.jl $(DIR)/merged/md.txt {}
	#echo "run OOM adjuster: echo -16 > /proc/X/oom_adj"
	#julia -F mergedf.jl /scratch/joosep/feb15 $(DIR)/merged/md.txt /scratch/joosep/feb15_2/output*.jld
	#echo "merge is done" | sendmail joosep.pata@cern.ch

merge-mva:
	$(JULIA_ROOT_DIR)/julia -F mvamerge.jl /scratch/joosep/mva.root /scratch/joosep/skim_jan31_2/output*.jld

submit-scan:
	find input/bdt_scan/cards/*.json | ~/parallel --delay 0.1 sbatch -p prio --exclude=../skim/exclude.txt parrun.sh {}

test-merge:
	$(JULIA_ROOT_DIR)/julia mergedf.jl test $(DIR)/merged/md.txt $(DIR)/output_1.jld  $(DIR)/output_2.jld

test-evloop:
	julia evloop.jl input/bdt_scan/test.json

recursive-hadd:
	rm -Rf hadd/*
	mkdir -p hadd/step1
	$(ROOTWRAP) && ( cat files.txt | $(PARCMD) -n10 hadd hadd/step1/merged_{#}.root {} )
	mkdir -p hadd/step2
	$(ROOTWRAP) && ( find hadd/step1 -name "merged_*.root" | $(PARCMD) -n5 hadd hadd/step2/merged_{#}.root {} )
	$(ROOTWRAP) && hadd hadd/merged.root hadd/step2/merged_*.root

convert-hists:
	rm -Rf output/bdt_scan
	$(ROOTWRAP) && python histmerge.py hadd/merged.root

conv2root:
	find ~/singletop/output/skims/skim_merged -name "*.jld" | ~/parallel $(JULIA_ROOT_DIR)/julia ../skim/conv2root.jl {} ~/singletop/output/skims/skim_root/{/.}.root
