include(joinpath(ENV["HOME"], ".juliarc.jl"))
using HDF5, JLD, DataFrames, DataArrays;

include("../analysis/selection.jl")

#const BASE="/Users/joosep/Documents/stpol/"
const BASE="/home/joosep/singletop/stpol2/src/skim";

const DEBUG=("DEBUG" in keys(ENV) && int(ENV["DEBUG"])==1)
if DEBUG
    println("*** DEBUG mode activated")
end

const pdir = "output/plots"
const hdir = "output/hists"
const ydir = "output/yields"

for d in [pdir, hdir, ydir]
    mkpath(d)
end

readdf(fn) = read(jldopen(fn), "df")
