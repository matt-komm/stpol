if !isdefined(:BASE)

println("loading base.jl...")
using JSON
t0 = time()
using DataFrames, DataArrays
include(joinpath(ENV["HOME"], ".juliarc.jl"))
using HDF5, JLD

#paths to be added here
if ENV["USER"] == "joosep"
    BASE = joinpath(ENV["HOME"], "Dropbox/kbfi/top/stpol")
else
    error("undefined BASE")
end
ENV["PYTHONPATH"]="$BASE/qcd_estimation"
using PyCall

qcdweight(df::DataFrameRow) = df[:xsweight]*df[:totweight]*df[:fitweight]*df[:qcd_weight]*df[:lumi]

const DH1 = int(hash("data_mu"))
const DH2 = int(hash("data_ele"))
const WT = Float32
is_any_na(row::DataFrameRow, symbs...) = any(Bool[isna(row.df[row.row, s])::Bool for s::Symbol in symbs])::Bool

function nominal_weight(df::DataFrameRow)
    sample = df[:sample]::Int64
   
    is_any_na(df, :xsweight, :b_weight, :pu_weight, :lepton_weight__id, :lepton_weight__iso, :lepton_weight__trigger) && return NA

    if sample!=DH1 && sample!=DH2
        return df[:xsweight]::Float64*df[:b_weight]::WT*df[:pu_weight]::WT*df[:lepton_weight__id]::WT*df[:lepton_weight__iso]::WT*df[:lepton_weight__trigger]::WT
    else
        return 1.0
    end
end

const procs = [:wjets, :ttjets, :tchan, :gjets, :dyjets, :schan, :twchan, :diboson, :qcd_mc_mu, :qcd_mc_ele]
const qcd_procs = [:wjets, :ttjets, :tchan, :gjets, :dyjets, :schan, :twchan, :diboson]
const mcsamples = [:ttjets, :wjets, :tchan, :dyjets, :diboson, :twchan, :schan, :gjets];

const systematic_processings = [
   :nominal,
   :EnUp, :EnDown,
   :UnclusteredEnUp, :UnclusteredEnDown,
   :ResUp, :ResDown,
   symbol("signal_comphep_anomWtb-0100"), symbol("signal_comphep_anomWtb-unphys"), symbol("signal_comphep_nominal"),
   :mass166_5, :mass169_5, :mass175_5, :mass178_5,
   :scaleup, :scaledown,
   :matchingup, :matchingdown,
   :wjets_fsim_nominal,
   :unknown
]

include("$BASE/src/analysis/util.jl")
include("$BASE/src/analysis/selection.jl");
include("$BASE/src/analysis/histo.jl");
using Hist
include("$BASE/src/fraction_fit/hists.jl");
#include("$BASE/src/analysis/hplot.jl");
include("$BASE/src/skim/xs.jl");
include("$BASE/src/analysis/varnames.jl")
include("$BASE/src/analysis/df_extensions.jl")
include("$BASE/src/analysis/systematic.jl")
include("$BASE/src/analysis/qcd.jl")
include("$BASE/src/analysis/reweight.jl")

const PDIR = "output/plots"
const HDIR = "output/hists"
const YDIR = "output/yields"
const FITDIR = "output/fits"

readdf(fn) = read(jldopen(fn, "r";mmaparrays=true), "df")
function writedf(fn, df)
    f = jldopen(fn, "w")
    write(f, "df", df)
    close(f)
end

chunk(n, c, maxn) = sum([n]*(c-1))+1:min(n*c, maxn)
chunks(csize, nmax) = [chunk(csize, i, nmax) for i=1:convert(Int64, ceil(nmax/csize))]


#generic flatten for any iterable to uniterable
flatten{T}(a::Array{T,1}) =
    any(map(x->isa(x,Array),a)) ? flatten(vcat(map(flatten,a)...)) : a
flatten{T}(a::Array{T}) = reshape(a,prod(size(a)))
flatten(a)=a

#syst_weights = [
#    :pu_weight, :pu_weight__up, :pu_weight__down,
#    :lepton_weight__id, :lepton_weight__id__up, :lepton_weight__id__down,
#    :lepton_weight__iso, :lepton_weight__iso__up, :lepton_weight__iso__down,
#    :lepton_weight__trigger, :lepton_weight__trigger__up, :lepton_weight__trigger__down
#]

t1 = time()
println("done loading base in $(t1-t0) seconds")
end
