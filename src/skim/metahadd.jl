#!/home/joosep/.julia/ROOT/julia
include("$(homedir())/.juliarc.jl")
using DataFrames, JSON

include("../analysis/util.jl")
include("../skim/xs.jl")
include("../skim/jet_cls.jl")

fname = ARGS[1]
ofile = ARGS[2]

flist = split(readall(fname))
@assert length(flist)>0 "no files specified"

println("Running over $(length(flist)) files")

tot_res = Dict()
for fi in flist
    res = Dict()
    acc = accompanying(fi)
    md = readtable(acc["processed"], allowcomments=true)
    for i=1:nrow(md)
        f = md[i, :files]
        
        st = sample_type(f)
        sample, iso, systematic = st[:sample], st[:iso], st[:systematic]

        k = "$(sample)"
        if !haskey(res, k)
            res["$(sample)/$(iso)/$(systematic)"] = 1
            res["$(sample)/$(iso)/$(systematic)/counters/generated"] = 0
        end 
        res["$(sample)/$(iso)/$(systematic)/counters/generated"] += md[i, :total_processed]
    end
    tot_res += res
end
println(tot_res)
of = open(ofile, "w")
write(of, json(tot_res))
close(of)
