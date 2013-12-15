#!/home/joosep/.julia/ROOT/julia
using ROOT,DataFrames

include(joinpath(ENV["HOME"], ".juliarc.jl"))
using HDF5, JLD

df = TreeDataFrame(ARGS[1])
println("opened TreeDataFrame ", ARGS[1], " with ", nrow(df), " events")
tic()

arr() = BitArray(nrow(df))
is_nominal = arr()
is_comphep = arr()

procs = [:tchan, :ttjets, :wjets, :wjets_sherpa, :data_mu, :data_ele]

is_proc = {k=>arr() for k in procs}

is_njets = {n=>arr() for n in [2,3]}
is_ntags = {n=>arr() for n in [0,1,2]}
is_lepton = {n=>arr() for n in [11,13]}

set_branch_status!(df.tree, "*", false)
reset_cache!(df.tree)

for b in ["sample*", "njets*", "ntags*", "lepton_type*", "systematic*"]
    set_branch_status!(df.tree, b, true)
    add_cache!(df.tree, b)
end

for i=1:nrow(df)
    if i%100000 == 0
        print(".")
        flush_cstdio()
    end
    if i%1000000 == 0
        print("|")
        flush_cstdio()
    end
    sample = df[i, :sample]
    syst = df[i, :systematic]
    njets = df[i, :njets]
    ntags = df[i, :ntags]
    lepton_type = df[i, :lepton_type]

    is_nominal[i] = (!isna(syst) && (syst == "nominal"))
    is_comphep[i] = (!isna(syst) && contains(syst, "signal_comphep"))

    for p in procs
        is_proc[p][i] = (!isna(sample) && (sample == string(p)))
    end
    for (k,v) in is_njets
        v[i] = (!isna(njets) && (njets == k)) 
    end
    for (k,v) in is_ntags
        v[i] = (!isna(ntags) && (ntags == k)) 
    end
    for (k,v) in is_lepton
        v[i] = (!isna(ntags) && (lepton_type == k)) 
    end
end
el = toq()

println("Processed ", nrow(df)/el, " events/second")

inds = {:is_comphep=>is_comphep, :is_nominal=>is_nominal, :is_proc=>is_proc, :is_njets=>is_njets, :is_ntags=>is_ntags, :is_lepton=>is_lepton}
write(jldopen(ARGS[2], "w"), "inds", inds)
