if !isdefined(:BASE)

println("loading base.jl...")

include(joinpath(ENV["HOME"], ".juliarc.jl"))

t0 = time()

using DataArrays, DataFrames
using JSON
using HDF5, JLD

#paths to be added here
if ENV["USER"] == "joosep"
    BASE = joinpath(ENV["HOME"], "Dropbox/kbfi/top/stpol")
else
    error("undefined BASE")
end

#add qcd estimation modules to pythonpath
ENV["PYTHONPATH"]="$BASE/qcd_estimation"

println("PYTHONPATH before doing 'using PyCall':\n\t", ENV["PYTHONPATH"])
using PyCall

const DH1 = int(hash("data_mu"))
const DH2 = int(hash("data_ele"))
const WT = Float32 #weight type

is_any_na(row::DataFrameRow, symbs...) =
  any(Bool[isna(row.df[row.row, s])::Bool for s::Symbol in symbs])::Bool

#replaces NA and NaN with a default value
get_no_na(row::DataFrameRow, s::Symbol, d=1.0) = (!isna(row[s]) && !isnan(row[s])) ? row[s] : d

qcd_weight(r::DataFrameRow) = r[:qcd_weight] * nominal_weight(r)
is_data(row::DataFrameRow) = ((row[:sample]::Int64==DH1) || (row[:sample]::Int64==DH2))
is_mc(row::DataFrameRow) = !is_data(row)

function nominal_weight(df::DataFrameRow)
    sample = df[:sample]::Int64

    if is_mc(df)
        const b_weight = get_no_na(df, :b_weight, float32(1))::WT
        const pu_weight = get_no_na(df, :pu_weight, float32(1))::WT
        const lepton_weight__id = get_no_na(df, :lepton_weight__id, float32(1))::WT
        const lepton_weight__iso = get_no_na(df, :lepton_weight__iso, float32(1))::WT
        const lepton_weight__trigger = get_no_na(df, :lepton_weight__trigger, float32(1))::WT

        const w = df[:xsweight]::Float64 * b_weight * pu_weight * lepton_weight__id * lepton_weight__iso * lepton_weight__trigger

        (isna(w) || isnan(w)) && error("w=$w, $(df[:xsweight]) $b_weight, $pu_weight, $lepton_weight__id, $lepton_weight__iso, $lepton_weight__trigger")
        
        return w
    else
        return 1.0
    end
end

const procs = Symbol[:wjets, :ttjets, :tchan, :gjets, :dyjets, :schan, :twchan, :diboson, :qcd_mc_mu, :qcd_mc_ele]
const mcsamples = Symbol[:ttjets, :wjets, :tchan, :dyjets, :diboson, :twchan, :schan, :gjets];
const TOTAL_SAMPLES = vcat(mcsamples, :qcd)

#lists the various systematic sample types
const systematic_processings = Symbol[
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
include("$BASE/src/analysis/fit.jl")

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

infb(a::AbstractVector) = vcat(-Inf, a, Inf)

chunk(n, c, maxn) = sum([n]*(c-1))+1:min(n*c, maxn)
chunks(csize, nmax) = [chunk(csize, i, nmax) for i=1:convert(Int64, ceil(nmax/csize))]

#generic flatten for any iterable to uniterable
flatten{T}(a::Array{T,1}) =
    any(map(x->isa(x,Array),a)) ? flatten(vcat(map(flatten,a)...)) : a
flatten{T}(a::Array{T}) = reshape(a,prod(size(a)))
flatten(a)=a

#load the fit results
const FITRESULTS = {
    :mu=>FitResult("$BASE/results/scanned_hists_feb7/hists/-0.20000/mu/merged/fit.json"),
    :ele=>FitResult("$BASE/results/scanned_hists_feb7/hists/-0.20000/ele/merged/fit.json")
}

t1 = time()
println("done loading base in $(t1-t0) seconds")

end
