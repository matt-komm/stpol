# include("histo.jl")

using Histograms
using CMSSW

function toroot(f::TFile, hname, h::NHistogram, labels={"x", "y"})
	nx, ny = size(h)
	hi = new_th2d(hname,
		h.edges[1], h.edges[2],
		contents(h)[1:nx-1,1:ny-1], errors(h)[1:nx-1,1:ny-1],
		entries(h)
	)
	CMSSW.set_axis_label(hi, labels[1], 1)
	CMSSW.set_axis_label(hi, labels[2], 2)
end



function toroot(tf::TFile, hname::ASCIIString, h::Histogram, label="x")
	n = nbins(h)
	hi = new_th1d(hname,
		h.bin_edges,
		contents(h)[1:n-1], errors(h)[1:n-1],
		entries(h)
	)
	CMSSW.set_axis_label(hi, label, 1)
end

function toroot(fn::ASCIIString, hname::ASCIIString, h::Any, args...)
    mkpath(dirname(fn))
	tf = TFile(fn, "UPDATE")
	cd(tf)
    toroot(tf, hname, h, args...)

    write(hi)
    close(tf)
end

function toroot(dir, d::Associative)
	mkpath(dir)
	for (k, v) in d
		p = joinpath(dir, k)
		dn = dirname(p)
		bn = basename(p)
		mkpath(dn)
		toroot("$dn/$bn.root", v, "hist")
	end
end

function fromroot(tf::TFile, hn::ASCIIString, t::Type{Histogram})
	
end
