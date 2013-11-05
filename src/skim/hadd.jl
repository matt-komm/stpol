using DataFrames
using ROOT

include("../analysis/util.jl")
include("../skim/xs.jl")
include("../skim/jet_cls.jl")

fname = ARGS[1]
ofile = ARGS[2]

flist = split(readall(fname))

cols = [:cos_theta, :top_mass, :ljet_eta, :mtw, :lepton_id, :lepton_type, :fileindex]
outcols = [:top_mass, :ljet_eta, :cos_theta, :lepton_type, :xsweight, :sample]
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
    println(fi)
    acc = accompanying(fi)
    md = readtable(acc["processed"])
    nrow(md) > 0 || error("metadata was empty")
    
    sample_types = [sample_type(x)[:sample] for x in md[:, :files]]
    #issame(sample_types) || error("multiple processes in one file, xs undefined") 
    #sample = first(sample_types)
    

    edf = TreeDataFrame(acc["df"])
    subdf = edf[:, cols]
    
    xsweights = DataArray(Float32, nrow(subdf))
    processes = DataArray(Symbol, nrow(subdf))
    for i=1:nrow(subdf)
        sample = string(sample_types[subdf[i, :fileindex]])
        xsweights[i] = 20000 * cross_sections[sample] / tot_res["$(sample)/counters/generated"]
        proc = get_process(sample)
        processes[i] = proc != :unknown ? proc : symbol(sample)
    end
    subdf["xsweight"] = xsweights
    subdf["sample"] = processes
    
    local_outcols = outcols
    for k in keys(acc)
        m = match(r"mva_(.*)", string(k))
        m == nothing && continue
        mvaname = m.captures[1]
        subdf[string(mvaname)] = readtable(acc[k])
        push!(local_outcols, symbol(mvaname)) 
    end
    
    df = subdf
    #df = df[:(mtw .> 50), :]
    #df = df[:(abs(ljet_eta) .> 2.5), :]
    #df = df[:(top_mass .> 130), :]
    #df = df[:(top_mass .< 220), :]
    
    df = df[:, local_outcols]
    push!(dfs, df)
end
df = rbind(dfs)
println("writing $(nrow(df)) events to $ofile")
writetable(ofile, df, separator=',')
