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
