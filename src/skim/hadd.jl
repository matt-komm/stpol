#!/home/joosep/.julia/ROOT/julia
using DataFrames
using ROOT

include("../analysis/util.jl")
include("../skim/xs.jl")
include("../skim/jet_cls.jl")

fname = ARGS[1]
ofile = ARGS[2]

flist = split(readall(fname))
println("Running over $(length(flist)) files")

cols = [:C, :bjet_phi, :ljet_phi, :njets, :ntags, :ljet_dr, :bjet_dr, :shat, :ht, :cos_theta, :top_mass, :ljet_eta, :mtw, :lepton_id, :lepton_type, :fileindex]
outcols = [:C, :bjet_phi, :ljet_phi, :njets, :ntags, :ljet_dr, :bjet_dr, :mtw, :shat, :ht, :top_mass, :ljet_eta, :cos_theta, :lepton_type, :xsweight, :sample, :isolation]

tot_res = Dict()
for fi in flist
    res = Dict()
    acc = accompanying(fi)
    md = readtable(acc["processed"], allowcomments=true)
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
    md = readtable(acc["processed"], allowcomments=true)
    nrow(md) > 0 || error("metadata was empty")
    
    sample_types = [sample_type(x) for x in md[:, :files]]

    edf = TreeDataFrame(acc["df"])
    subdf = edf[:, cols]
    
    xsweights = DataArray(Float32, nrow(subdf))
    processes = DataArray(ASCIIString, nrow(subdf))
    isos = DataArray(ASCIIString, nrow(subdf))
    for i=1:nrow(subdf)
        sample = string(sample_types[subdf[i, :fileindex]][:sample])
        iso = string(sample_types[subdf[i, :fileindex]][:iso])

        xsweights[i] = 20000 * cross_sections[sample] / tot_res["$(sample)/counters/generated"]
        proc = get_process(sample)
        processes[i] = proc != :unknown ? string(proc) : string(sample)
        isos[i] = string(iso)
    end
    subdf["xsweight"] = xsweights
    subdf["sample"] = processes
    subdf["isolation"] = isos
    
    local_outcols = deepcopy(outcols)
    for k in keys(acc)
        m = match(r"mva_(.*)", string(k))
        m == nothing && continue
        mvaname = m.captures[1]
        println("adding mva from $k:$(acc[k]):$(mvaname)")
        mvatable = readtable(acc[k], allowcomments=true)[1]
        @assert length(mvatable)==nrow(subdf) "number of rows in mva table $k is wrong"
        subdf[string(mvaname)] = mvatable
        push!(local_outcols, symbol(mvaname)) 
    end
    df = subdf
    
    df = df[:, local_outcols]
    println(colnames(df)) 
    push!(dfs, df)
end

@assert length(dfs)>0 "no DataFrames were produced"

df = rbind(dfs)
println("writing $(nrow(df)) events to $ofile")
writetable(ofile, df, separator=',')
#writetree("test.root", df)
