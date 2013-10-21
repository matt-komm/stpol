#julia cutflow.jl tchan.txt

if length(ARGS)!=1
    error("run as \$ \$/HOME/.julia/ROOT.jl/julia runhisto.jl input.txt")
end

fname = string(ARGS[1])

flist = split(readall(fname))

@everywhere begin

import Base.+

using DataFrames
using ROOT

include("histo.jl")
using Hist

include("../skim/xs.jl")

metadata(fn) = replace(fn, ".root", "_processed.csv")

emptyres() = Dict()

#add two dicts elementwise, with
#common elements being added and missing elements taken from either
#argument
function +(d1::Dict{Any, Any}, d2::Dict{Any, Any})

    k1 = Set([x for x in keys(d1)]...)
    k2 = Set([x for x in keys(d2)]...)

    common = intersect(k1, k2)

    ret = Dict()
    for k in common
        ret[k] = d1[k] + d2[k]
    end

    #in d1
    for k in [x for x in setdiff(k1, k2)]
        if !haskey(d2, k)
            ret[k] = d1[k]
        end
    end

    #in d2
    for k in [x for x in setdiff(k2, k1)]
        if !haskey(d1, k)
            ret[k] = d2[k]
        end
    end

    return ret
end


function process_file(fi)
    res = emptyres()
    md = readtable(metadata(fi))

    #loop over metadata
    for i=1:nrow(md)
        f = md[i, :files]
        sample = sample_type(f)[:sample]
        k = "$(sample)"
        if !haskey(res, k)
            res["$(sample)/cos_theta"] = Histogram(60, -1, 1)
            res["$(sample)/abs_eta_lj"] = Histogram(60, 0, 5)
            res["$(sample)/eta_lj"] = Histogram(60, -5, 5)
        end
    end

    #loop over events
    df = TreeDataFrame(fi)
    for i=1:nrow(df)
        findex = df[i, :fileindex]
        cls = sample_type(md[findex, :files])
        sample = cls[:sample]

        hcos = res["$(sample)/cos_theta"]
        habsetalj = res["$(sample)/abs_eta_lj"]
        hetalj = res["$(sample)/eta_lj"]

        if !(string(cls[:iso]) == "iso")
            continue
        end

        if !(df[i, :njets]==2 && df[i, :ntags]==1 && df[i, :mtw] > 40)
            continue
        end

        hfill!(hcos, df[i, :cos_theta])
        hfill!(habsetalj, abs(df[i, :ljet_eta]))
        hfill!(hetalj, df[i, :ljet_eta])

    end
    return res 
end

end #everywhere

results = reduce(+, emptyres(), pmap(process_file, flist))

for (k, v) in results
    p = "hists/$k.txt"
    mkpath(dirname(p))
    writetable(p, todf(v), separator=',')
end

#writetable("hist.txt", todf(results), separator=',')
