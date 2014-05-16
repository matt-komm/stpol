include("histo.jl")
using HDF5, JLD
fi = jldopen(ARGS[1])
hists = read(fi, "ret")
for (k, v) in hists
    println("$k $v")
end
