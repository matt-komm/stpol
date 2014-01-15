include ../analysis/Makefile.options

INDIR=../skim/skim_dec20_1/chunked
OFDIR=out1

.PHONY: hists

hists:
	rm -Rf $(OFDIR)/hists
	mkdir -p $(OFDIR)/hists
	find $(INDIR) -name "*.root" | $(PARCMD) -j32 ./evloop.jl {} $(OFDIR)/hists/hist.{#}.jld > $(OFDIR)/log.txt

merge:
	rm -Rf $(OFDIR)/merged
	mkdir -p $(OFDIR)/merged
	find $(OFDIR)/hists -name "*.jld" | $(PARCMD) -n10 ./merge.jl $(OFDIR)/merged/hist.{#}.jld {} > $(OFDIR)/merged/log.txt
	./merge.jl merged.jld $(OFDIR)/merged/*.jld
