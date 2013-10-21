#julia cutflow.jl tchan.txt
fname = ARGS[1]
sym = symbol(split(basename(fname), ".")[1])

flist = split(readall(fname))

@everywhere begin

using ROOT
using DataFrames

include("../skim/xs.jl")

metadata(fn) = replace(fn, ".root", "_processed.csv")

new_results() = DataFrame(
    generated=[0], all=Int32[0], hlt=Int32[0], 
    lepton=Int32[0], met=Int32[0],
    jet=Int32[0], rms=Int32[0], tag=Int32[0]
)


function process_file(fi)
    res = Dict()

    md = readtable(metadata(fi))

    for i=1:nrow(md)
        f = md[i, :files]
        sample = sample_type(f)[:sample]
        if !haskey(res, sample)
            res[sample] = new_results()
        end
        res[sample][1,:generated] += md[i, :total_processed]
    end

    df = TreeDataFrame(fi)
    for i=1:nrow(df)
        findex = df[i, :fileindex]
        cls = sample_type(md[findex, :files])
        sample = cls[:sample] 

        if !(string(cls[:iso]) == "iso")

            continue
        end
        
        res[sample][1, :all] += 1
        
        if df[i, :hlt] != true
            continue
        end
        res[sample][1, :hlt] += 1
        
        lt = df[i, :lepton_type]
        if lt != "muon"
            continue
        end
        res[sample][1, :lepton] += 1
        
        mtw = df[i, :mtw] 
        if (!isna(mtw) && mtw < 40)
            continue
        end
        res[sample][1, :met] += 1
        
        if df[i, :njets] != 2
            continue
        end
        res[sample][1, :jet] += 1
        
        if df[i, :ljet_rms] > 0.025
            continue
        end
        res[sample][1, :rms] += 1
        
        if df[i, :ntags] != 1
            continue
        end
        res[sample][1, :tag] += 1
        
    end
    return res 
end

end #everywhere

el = @elapsed results = pmap(process_file, flist)
speed = length(flist)/el
println("Processed $(length(flist)) files, $speed per sec")

total_results = Dict()
for resd in results
    for (sample, resdf) in resd
        if !haskey(total_results, sample)
            total_results[sample] = new_results()
        end
        total_results[sample] += resdf
    end
end

lumi=19600
for (sample, res) in total_results
    xsweight = cross_sections[string(sample)] * lumi / res[1, :generated]
    res["xsweight"] = [xsweight]
    res["samp"] = DataVector[string(sample)]
end

results = rbind([v for (k,v) in total_results])
show(results)
writetable("results_$sym.txt", results, separator=',')
