include ../analysis/Makefile.options

INDIR=../skim/merged1
OFDIR=out/hists

.PHONY: hists

hists:
	mkdir -p $(OFDIR)
	find $(INDIR) -name "*.root" | $(PARCMD) -j10 ./evloop.jl {} $(OFDIR)/hist.{#}.jld > $(OFDIR)/log.txt
