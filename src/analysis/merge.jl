#!/usr/bin/env julia
include("histo.jl");
include("base.jl");
using DataFrames, Hist

ofname = ARGS[1]
inf = ARGS[2:length(ARGS)]

function openres(fn)
    fi = jldopen(fn)
    ret = read(fi, "res")
    close(fi)
    return ret
end

out = Dict()
for fn in sort!(inf)
    tic()
    hists = openres(fn)
    println(fn, " ", length(hists))
    for (k, v) in hists
        if !(k in keys(out))
            out[k] = v
        else
            out[k] += v
        end
    end
    toc()
end

for (k, v) in out
    println(k, " ", typeof(v), " ", nentries(v))
end

println("writing output for $(length(out)) histograms")
tic()
of = jldopen(ofname, "w")
write(of, "res", out)
close(of)
toc()
