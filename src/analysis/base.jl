include(joinpath(ENV["HOME"], ".juliarc.jl"))
using HDF5, JLD, DataFrames, DataArrays;

include("../analysis/selection.jl")

include("../analysis/histo.jl")
using Hist

#const BASE="/Users/joosep/Documents/stpol/"
const BASE="/home/joosep/singletop/stpol2/src/skim";

const DEBUG=("DEBUG" in keys(ENV) && int(ENV["DEBUG"])==1)
if DEBUG
    println("*** DEBUG mode activated")
end
