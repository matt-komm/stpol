include("../analysis/base.jl")
include("$BASE/src/skim/jet_cls.jl")
using ROOT, ROOTDataFrames

#file created by metahadd.jl
sumfname = ARGS[1]

#list of output.root files
inf = ARGS[2:length(ARGS)]

#read metahadd output as JSON
tot_res = JSON.parse(readall(sumfname))
isa(tot_res, Dict) || error("could not parse metadata $sumfname")
#timing info
meantimes = Any[]

#output data frame
resdf = DataFrame()

i=1
Ntot = 0

#list of open files
fhandles = Any[]

#W+light scale-up factor
const wjets_light_scale_factor = 0.1

for fi in inf
    println(fi)
    tic()	
    
    #get all the files related to fi
    acc = accompanying(fi)
    println("$fi $acc")
    #get the calculated mva-s
    mvas = filter(x->match(r"mva_.*", x)!=nothing, keys(acc))|>collect
    
    df = TreeDataFrame([fi])
 
    added_df = DataFrame()
    if nrow(df)>0
        for mva in mvas
            println("mva=$mva")
            t = readtable(acc[mva]; allowcomments=true)
            
            if nrow(t)==nrow(df)
                mvaname = match(r"mva_(.*)", mva).captures[1]
                added_df[symbol(mvaname)] = t[1]
            else 
                println(acc[mva])
                warn("mismatch in mva file $(acc[mva]) df=$(nrow(df)), mva($mva)=$(nrow(t))") 
            end
        end
    end
    
    added_df[:ngen] = int64(0)
    added_df[:xsweight] = float64(0.0)

    added_df[:wjets_ct_shape_weight] = float64(1.0)
    added_df[:wjets_ct_shape_weight__up] = float64(1.0)
    added_df[:wjets_ct_shape_weight__down] = float64(1.0)

    added_df[:wjets_fl_yield_weight] = float64(1.0)
    added_df[:wjets_fl_yield_weight__up] = float64(1.0)
    added_df[:wjets_fl_yield_weight__down] = float64(1.0)

    enable_branches(df, ["sample*", "subsample*", "isolation*", "systematic*", "cos_theta_lj*", "jet_cls*", "processing_tag*"])
    
    println("looping over $(nrow(df)) events")
    for j=1:nrow(df)
	load_row(df, j)
        row = DataFrameRow(df, j)
        subsample = :nothing
        sample = :nothing
        iso = :nothing
        systematic = :nothing
        tag = :nothing

	j<5 && println(df[j, :processing_tag], " ", df[j, :subsample], " ", df[j, :sample], " ", df[j, :isolation]) 
        try
            tag = hmap[:from][int(df[j, :processing_tag])]
        catch err
            error("tag=$tag: $fi, could not load key $(df[j, :processing_tag]|>int), $err")
        end
        try
            subsample = hmap[:from][int(df[j, :subsample])]
        catch err
            error("subsample=$subsample: $fi, could not load key $(df[j, :subsample]|>int) $err")
        end
        try
            sample = hmap[:from][int(df[j, :sample])]
        catch err
            error("sample=$sample: $fi, could not load key $err")
        end
        try
            iso = hmap[:from][int(df[j, :isolation])]
        catch err
            error("iso=$iso: $fi, could not load key $err")
        end
        try
            systematic = hmap[:from][int(df[j, :systematic])]
        catch err
            warn("systematic=$systematic: $fi, could not load key $err")
        end
        #println(tot_res)
        if systematic != :nothing
            const ngen = tot_res["$(tag)/$(subsample)/$(iso)/$(systematic)/counters/generated"]
        else #Data, systematic=""
            const ngen = tot_res["$(tag)/$(subsample)/$(iso)//counters/generated"]
        end
        const cls = jet_cls_from_number(df[j, :jet_cls])
        added_df[j, :ngen] = ngen
        if subsample == "SingleMu" || subsample == "SingleEle"
            added_df[j, :xsweight] = 1.0
            println("Data weight")
        else
            added_df[j, :xsweight] = haskey(cross_sections, subsample) ? cross_sections[subsample] / ngen : 1
        end
  
        #W+jets reweighting
        if symbol(sample) == :wjets && !isna(df[j, :cos_theta_lj])
            w, wdown, wup = wjets_shape_weight(row)
            added_df[j, :wjets_ct_shape_weight] = w
            added_df[j, :wjets_ct_shape_weight__up] = wup
            added_df[j, :wjets_ct_shape_weight__down] = wdown
            const cls_hl = jet_cls_heavy_light(cls)
            
            if cls_hl == :heavy
                added_df[j, :wjets_fl_yield_weight] = 1.0
                added_df[j, :wjets_fl_yield_weight__up] = 2.0
                added_df[j, :wjets_fl_yield_weight__down] = 0.5
            else
                added_df[j, :wjets_fl_yield_weight] = 1.0 + wjets_light_scale_factor
                added_df[j, :wjets_fl_yield_weight__up] = 1.0 + 2 * wjets_light_scale_factor 
                added_df[j, :wjets_fl_yield_weight__down] = 1.0 + 0.5 * wjets_light_scale_factor 
            end
        end

    end

    q = toq()
    push!(meantimes, q)
    
    eta = (length(inf)-i)*mean(meantimes)
   
    #write output through temp file and rsync 
    writetree_temp("$fi.added", added_df)
    println("$i/$(length(inf)) Ntot=$Ntot ti=$q tm=$(mean(meantimes)) ETA=$eta")

    i += 1
end
