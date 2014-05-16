include("../analysis/base.jl")
include("$BASE/src/skim/jet_cls.jl")
using CMSSW

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
    
    df = TreeDataFrame(fi)
 
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

    set_branch_status!(df.tree, "*", false)

    for x in ["sample", "subsample", "iso", "systematic", "cos_theta_lj", "jet_cls", "processing_tag"]
        set_branch_status!(df.tree, "$x*", true)
    end
    
    println("looping over $(nrow(df)) events")
    for j=1:nrow(df)
        row = DataFrameRow(df, j)
        subsample = :nothing
        sample = :nothing
        iso = :nothing
        systematic = :nothing
        tag = :nothing
        try
            tag = hmap[:from][int(df[j, :processing_tag])]
            subsample = hmap[:from][int(df[j, :subsample])]
            sample = hmap[:from][int(df[j, :sample])]
            iso = hmap[:from][int(df[j, :isolation])]
            systematic = hmap[:from][int(df[j, :systematic])]
        catch err
            error("$fi, could not load key $err")
        end
        const ngen = tot_res["$(tag)/$(subsample)/$(iso)/$(systematic)/counters/generated"]
        const cls = jet_cls_from_number(df[j, :jet_cls])
        added_df[j, :ngen] = ngen
        added_df[j, :xsweight] = haskey(cross_sections, subsample) ? cross_sections[subsample] / ngen : 1

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
    
    writetree_temp("$fi.added", added_df)
    println("$i/$(length(inf)) Ntot=$Ntot ti=$q tm=$(mean(meantimes)) ETA=$eta")

    i += 1
end
