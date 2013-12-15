include(joinpath(ENV["HOME"], ".juliarc.jl"))
using HDF5, JLD, DataFrames, DataArrays;

include("../analysis/selection.jl")

@osx_only const BASE="/Users/joosep/Documents/stpol/"
@linux_only const BASE="/home/joosep/singletop/stpol2/";

const DEBUG=("DEBUG" in keys(ENV) && int(ENV["DEBUG"])==1)
if DEBUG
    println("*** DEBUG mode activated")
end

const PDIR = "output/plots"
const HDIR = "output/hists"
const YDIR = "output/yields"
const FITDIR = "output/fits"

readdf(fn) = read(jldopen(fn), "df")

t = readtable("$BASE/src/analysis/varnames.csv";separator=',');
vars = {symbol(t[i, 1]) => t[i, 2] for i=1:nrow(t)};
