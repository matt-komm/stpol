#julia cutflow.jl config.cfg

using IniFile

if length(ARGS)!=1
    error("run as \$ \$/HOME/.julia/ROOT.jl/julia runhisto.jl config.cfg")
end

#read input files
cfgfname = ARGS[1]
config = read(Inifile(), cfgfname)
fname = get(config, "input", "file")
flist = split(readall(fname))

#output directory
ofdir = get(config, "output", "dir")

#the name of the MVA, used for the mva.csv file
mvaname = get(config, "mva", "name")

#send mva variable to every worker
@eval @everywhere mvaname=$(mvaname)

###
@everywhere begin
###
    #name of the .csv file with the mva

    import Base.+
    
    using DataFrames
    using ROOT
    
    include("histo.jl")
    using Hist
    
    include("../skim/xs.jl")
    
    metadata(fn) = replace(fn, ".root", "_processed.csv")
    function accompanying(fn)
        files = readdir(dirname(fn))
        bn = split(basename(fn), ".")[1]
        
        out = Dict()
        for fi in files
            reg = Regex(".*$(bn)_(.*).csv")
            m = match(reg, fi)
            m == nothing && continue
            out[m.captures[1]] = joinpath(dirname(fn), fi)
        end
        return out
    end
    
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
    
        #create empty results dict
        res = emptyres()
    
    
        #get accompanying files for the .root file
        acc = accompanying(fi)
        #read the .root file metadata (files processed, events generated etc)
        md = readtable(acc["processed"])
        
        #get the MVA tables
        mva_df = None
        if mvaname != "" 
            mva_df = readtable(acc[mvaname])
        else
            if "mva_csvt" in keys(acc)
                mva_df = readtable(acc["mva_csvt"])
            elseif "mva_csvm" in keys(acc)
                mva_df = readtable(acc["mva_csvm"])
            elseif "mva_tchpt" in keys(acc)
                mva_df = readtable(acc["mva_tchpt"])
            end
        end
    
        #loop over metadata
        for i=1:nrow(md)
            f = md[i, :files]
            sample = sample_type(f)[:sample]
            k = "$(sample)"
            if !haskey(res, k)
                res["$(sample)"] = 1

                res["$(sample)/bdt"] = Histogram(60, -1, 1)
                res["$(sample)/cos_theta"] = Histogram(60, -1, 1)
                res["$(sample)/abs_eta_lj"] = Histogram(60, 0, 5)
                res["$(sample)/eta_lj"] = Histogram(60, -5, 5)
                res["$(sample)/generated"] = 0
    
                res["$(sample)/counters/processed"] = 0
                res["$(sample)/counters/isomu"] = 0
                res["$(sample)/counters/njets"] = 0
                res["$(sample)/counters/mtw"] = 0
                res["$(sample)/counters/ntags"] = 0
                res["$(sample)/counters/mva"] = 0
            end
            res["$(sample)/generated"] += md[i, :total_processed]
        end
    
        #loop over events
        df = TreeDataFrame(fi)
    
        mvacol = colnames(mva_df)[1]
        for i=1:nrow(df)
    
            findex = df[i, :fileindex]
            cls = sample_type(md[findex, :files])
            sample = cls[:sample]
            
            res["$(sample)/counters/processed"] += 1
    
            hcos = res["$(sample)/cos_theta"]
            habsetalj = res["$(sample)/abs_eta_lj"]
            hetalj = res["$(sample)/eta_lj"]
            hbdt = res["$(sample)/bdt"]
    
            !(string(cls[:iso]) == "iso") && continue
            !(df[i, :hlt]) && continue
            lepid = df[i, :lepton_id]
            !(!isna(lepid) && abs(lepid) == 13) && continue
            res["$(sample)/counters/isomu"] += 1
    
            !(df[i, :njets] == 2) && continue
            res["$(sample)/counters/njets"] += 1
            mtw = df[i, :mtw]
    
            !(!isna(mtw) && mtw >= 40) && continue
            res["$(sample)/counters/mtw"] += 1
            
            !(df[i, :ntags] == 1) && continue
            res["$(sample)/counters/ntags"] += 1
    
            #check if event passes a pre-defined BDT WP
            mva = mva_df[i, mvacol]
            hfill!(hbdt, mva)
            !(!isna(mva) && mva > 0.0) && continue
            res["$(sample)/counters/mva"] += 1
        
            #fill all "final" histograms
            hfill!(hcos, df[i, :cos_theta])
            hfill!(habsetalj, abs(df[i, :ljet_eta]))
            hfill!(hetalj, df[i, :ljet_eta])
    
        end
        return res 
    end

###
end #everywhere
###

#map processing over files, reduce via addition
results = reduce(+, emptyres(), pmap(process_file, flist))

#cross-sections need to be calculated after merging
for (k, v) in results
    m = match(r"(.*)/generated", k)
    m == nothing && continue

    sample = m.captures[1]
    results["$(sample)/xsweight"] = cross_sections[sample]/v
end

#save output
hmetadata = Dict()
for (k, v) in results
    p = "$(ofdir)/$k.csv"
    #println("saving $k:$(typeof(v))")
    if typeof(v) <: Histogram
        mkpath(dirname(p))
        writetable(p, todf(v), separator=',')
    else
        hmetadata[k] = v
    end
end

#save histogram metadata
hmetadata_df = similar(DataFrame(key=String[], value=Any[]), length(hmetadata))
i = 1
for k in sort(collect(keys(hmetadata)))
    v = hmetadata[k]
    hmetadata_df[i, :key] = k
    hmetadata_df[i, :value] = v
    i += 1
end
writetable("$(ofdir)/metadata.csv", hmetadata_df, separator=',')
