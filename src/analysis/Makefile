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

submit-scan:
	find input/hists -name "*.json" | ~/parallel --delay 0.1 sbatch --exclude=../skim/exclude.txt parrun.sh {}

project-nominal:
	#find $(DIR) -name "output*.root" | ~/parallel -j100 srun -p prio --exclude=../skim/exclude.txt $(JULIA_ROOT_DIR)/julia project_nominal.jl {} {}.nominal
	find $(DIR) -name "output*.root" | ~/parallel -j32 $(JULIA_ROOT_DIR)/julia project_nominal.jl {} {}.nominal

project-tchan:
	find $(DIR) -name "output*.root" | ~/parallel -j100 srun -p prio --exclude=../skim/exclude.txt $(JULIA_ROOT_DIR)/julia project_tchan.jl {} {}.tchan

test-evloop:
	$(JULIA_ROOT_DIR)/julia evloop.jl /hdfs/local/joosep/stpol/skims/Apr04/step3/csvt/Mar13/iso/nominal/T_t_ToLeptons/844/output.root out infile.json 

merge:
	rm -Rf output

	mkdir -p results/hists/qcd__metmtw_nominal/soltype__real/bdt__bdt_sig_bg/csvt/
	python histmerge.py /Users/joosep/Dropbox/kbfi/top/stpol/results/hists/qcd__metmtw_nominal/soltype__real/bdt__bdt_sig_bg/csvt/merged.root
	mv output/bdt_scan/* results/hists/qcd__metmtw_nominal/soltype__real/bdt__bdt_sig_bg/csvt/
	
	mkdir -p results/hists/qcd__metmtw_nominal/soltype__cplx/bdt__bdt_sig_bg/csvt/
	python histmerge.py /Users/joosep/Dropbox/kbfi/top/stpol/results/hists/qcd__metmtw_nominal/soltype__cplx/bdt__bdt_sig_bg/csvt/merged.root
	mv output/bdt_scan/* results/hists/qcd__metmtw_nominal/soltype__cplx/bdt__bdt_sig_bg/csvt/

recursive-hadd: recursive-hadd-1 recursive-hadd-2 recursive-hadd-3 recursive-hadd-4
recursive-hadd-1:
	./recursive-hadd.sh /hdfs/local/joosep/stpol/hists/Apr07_C/qcd__mva_nominal/csvt/ /scratch/joosep/hists/csvt/mva_nominal

recursive-hadd-2:
	./recursive-hadd.sh /hdfs/local/joosep/stpol/hists/Apr07_C/qcd__metmtw_nominal/csvt/ /scratch/joosep/hists/csvt/metmtw_nominal
