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
    
    println(fi," ", acc["processed"])

    for i=1:nrow(md)
        f = md[i, :files]
        
        st = sample_type(f)
        sample, iso, systematic = st[:sample], st[:iso], st[:systematic]
        k = "$(sample)/$(iso)/$(systematic)"
        if !haskey(res, k)
            res[k] = 1
            res["$(k)/counters/generated"] = 0
        end 
        res["$(k)/counters/generated"] += md[i, :total_processed]
        println("\t$k $(md[i, :total_processed])") 
    end
    tot_res += res
end
of = open(ofile, "w")
write(of, json(tot_res))
close(of)

for (k,v) in sort(collect(tot_res), by=x->x[1])
    println(k, " ", v)
end
