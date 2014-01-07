include(joinpath(ENV["HOME"], ".juliarc.jl"))
using HDF5, JLD, DataFrames

include("../analysis/selection.jl")

if ENV["USER"] == "joosep"
	@osx_only const BASE="/Users/joosep/Documents/stpol/"
	@linux_only const BASE="/home/joosep/singletop/stpol2/";
end

const DEBUG=("DEBUG" in keys(ENV) && int(ENV["DEBUG"])==1)
if DEBUG
    println("*** DEBUG mode activated")
end

const PDIR = "output/plots"
const HDIR = "output/hists"
const YDIR = "output/yields"
const FITDIR = "output/fits"

readdf(fn) = read(jldopen(fn), "df")
writedf(fn, df) = write(jldopen(fn, "w"), "df", df)

include("$BASE/src/analysis/varnames.jl")

chunk(n, c, maxn) = sum([n]*(c-1))+1:min(n*c, maxn)
chunks(csize, nmax) = [chunk(csize, i, nmax) for i=1:convert(Int64, ceil(nmax/csize))]


#generic flatten for any iterable to uniterable
flatten{T}(a::Array{T,1}) =
    any(map(x->isa(x,Array),a)) ? flatten(vcat(map(flatten,a)...)) : a
flatten{T}(a::Array{T}) = reshape(a,prod(size(a)))
flatten(a)=a