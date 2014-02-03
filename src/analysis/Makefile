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
	~/.julia/ROOT/julia -F mergedf.jl /scratch/joosep/test3.df $(DIR)/merged/md.txt /scratch/joosep/skim_jan31_2/output*.jld
	echo "merge is done" | sendmail joosep.pata@cern.ch

merge-mva:
	~/.julia/ROOT/julia -F mvamerge.jl /scratch/joosep/mva.root /scratch/joosep/skim_jan31_2/output*.jld

submit-scan:
	find cards/*.json | ~/parallel --delay 1.0 sbatch -c24 --contigous --exclude=../skim/exclude.txt parrun.sh {}
convert-hists:
	find results/scanned/ -name "*.jld" | ~/parallel --no-notice ~/.julia/ROOT/julia convert_hists.jl {} results/hists/{/.}
