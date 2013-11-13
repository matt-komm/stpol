all: histo_tchpt histo_csvt histo_csvm

histo_tchpt:
	~/.julia/ROOT.jl/julia -p 3 runhisto.jl input/tchpt.cfg

histo_csvt:
	~/.julia/ROOT.jl/julia -p 3 runhisto.jl input/csvt.cfg

histo_csvm:
	~/.julia/ROOT.jl/julia -p 3 runhisto.jl input/csvm_with_bdisc.cfg
