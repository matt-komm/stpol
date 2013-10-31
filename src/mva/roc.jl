using DataFrames
using ROOT

include("../analysis/util.jl")
include("../skim/xs.jl")
include("../skim/jet_cls.jl")

fname = ARGS[1]
ofile = ARGS[2]

flist = split(readall(fname))

cols = [:jet_cls, :mtw, :lepton_id, :lepton_type]

tot_res = Dict()
for fi in flist
    res = Dict()
    acc = accompanying(fi)
    md = readtable(acc["processed"])
    for i=1:nrow(md)
        f = md[i, :files]
        sample = sample_type(f)[:sample]
        k = "$(sample)"
        if !haskey(res, k)
            res["$(sample)"] = 1
            res["$(sample)/counters/generated"] = 0
        end 
        res["$(sample)/counters/generated"] += md[i, :total_processed]
    end
    tot_res += res
end

dfs = Any[]
for fi in flist
    acc = accompanying(fi)
    mvaname = first(filter(x -> beginswith(x, "mva_"), keys(acc)))
    
    df = readtable(acc[mvaname])
    md = readtable(acc["processed"])
    
    sample_types = [sample_type(x)[:sample] for x in md[:, :files]]
    issame(sample_types) || error("multiple processes in one file, xs undefined") 
    sample = sample_type(md[1, :files])[:sample]

    edf = TreeDataFrame(acc["df"])
    subdf = edf[:, cols]
    subdf["jet_cls"] = [jet_cls_from_number(x) for x in subdf["jet_cls"]]
    
    xs = 20000 * cross_sections[sample] / tot_res["$(sample)/counters/generated"]
    df["xsweight"] = xs
    df["sample"] = sample
    df = hcat(df, subdf)

    println("$fi $(nrow(df))")
    df = df[:(mtw .> 40), :]
    push!(dfs, df)
end
df = rbind(dfs)
println("writing $(nrow(df)) events to $ofile")
writetable(ofile, df)
