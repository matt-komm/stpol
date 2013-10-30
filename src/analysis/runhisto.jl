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
    
    using DataFrames
    using ROOT
    
    include("histo.jl")
    using Hist
    
    include("../skim/xs.jl")
    include("util.jl") 
    
    emptyres() = Dict()
    
    #add two dicts elementwise, with
    #common elements being added and missing elements taken from either
    #argument

    mva_wps = [
        0.051, #CSVT W+jets 800
        0.041, #CSVM+bd W+jets 800
        0.0265, #TCHPT W+jets 800
        0.0,
    ]
    
    function process_file(fi)
    
        #create empty results dict
        res = emptyres()
    
        #get accompanying files for the .root file
        acc = accompanying(fi)
        #read the .root file metadata (files processed, events generated etc)
        md = readtable(acc["processed"])
        
        #get the MVA tables
        mva_df = None
        mva_df = readtable(acc[mvaname])
        
        myid()==1 && println("starting to loop over $(nrow(md)) metadata rows")
        
        #loop over metadata
        for i=1:nrow(md)
            f = md[i, :files]
            sample = sample_type(f)[:sample]
            k = "$(sample)"
            if !haskey(res, k)
                res["$(sample)"] = 1

                res["$(sample)/bdt"] = Histogram(600, -1, 1)
                res["$(sample)/cos_theta"] = Histogram(60, -1, 1)
                res["$(sample)/abs_eta_lj"] = Histogram(60, 0, 5)
                res["$(sample)/eta_lj"] = Histogram(60, -5, 5)
                res["$(sample)/generated"] = 0
    
                res["$(sample)/counters/processed"] = 0
                res["$(sample)/counters/isolep"] = 0
                res["$(sample)/counters/njets"] = 0
                res["$(sample)/counters/mtw"] = 0
                res["$(sample)/counters/ntags"] = 0

                for j=1:length(mva_wps)
                    res["$(sample)/counters/mva_$j"] = 0
                end
            end
            res["$(sample)/generated"] += md[i, :total_processed]
        end
    
        #loop over events
        df = TreeDataFrame(fi)
    
        mvacol = colnames(mva_df)[1]
        myid()==1 && println("starting to loop over $(nrow(df)) events")
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
            #lepid = df[i, :lepton_id]
            #!(!isna(lepid) && abs(lepid) == 13) && continue
            res["$(sample)/counters/isolep"] += 1
    
            !(df[i, :njets] == 2) && continue
            res["$(sample)/counters/njets"] += 1
            
            mtw = df[i, :mtw]
            !(!isna(mtw) && mtw >= 40) && continue
            res["$(sample)/counters/mtw"] += 1
            
            !(df[i, :ntags] == 1) && continue
            res["$(sample)/counters/ntags"] += 1
    
            mva = mva_df[i, mvacol]
            hfill!(hbdt, mva)
            
            #check if event passes a pre-defined BDT WP
            isna(mva) && continue
            for j=1:length(mva_wps)
                if mva > mva_wps[j]
                    res["$(sample)/counters/mva_$j"] += 1
                end
            end

            #fill all final histograms
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
    results["$(sample)/xsweight"] = 20000 * cross_sections[sample]/v
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
