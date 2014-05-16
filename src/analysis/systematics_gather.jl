include("base.jl");
include("$BASE/src/analysis/histkey.jl");

@deprecate preph merge_histogram

function makepositive!(h::Histogram)
    #println("pre: ", join(h.bin_contents, ","))
    for i=1:nbins(h)
        if h.bin_contents[i] <= 0
            h.bin_contents[i] = 0
            h.bin_entries[i] = 1
        end
    end
    #println("post: ", join(h.bin_contents, ","))
end

function merge_histogram(
    hists::Dict{HistKey, Any},
    lepton::Symbol,
    histname::Symbol,
    selection_major::Symbol,
    selection_minor::Symbol,
    njet::Int64,
    ntag::Int64,
    )
    
    ret = Dict()
    MH = Dict()
    KK = Dict()

    datasamp = symbol("data_$lepton");
    samples = vcat(mcsamples..., datasamp)
    
    for k in keys(hists)
        #choose correct lepton flavour
        k.lepton == lepton || continue

        k.sample in samples || continue
        k.object == histname || continue
        k.scenario==:unweighted && k.sample!=datasamp && continue

        (k.njets!=njets && k.ntags!=ntags) || continue
        
        s1 = k.systematic
        if s1 in keys(SYSTEMATICS_TABLE)
            s1 = SYSTEMATICS_TABLE[s1]
        end

        s2 = k.scenario
        
        if s1==:nominal && s2==:nominal
            s = :nominal
        elseif s1==:nominal
            s = s2
        elseif s2==:nominal
            s = s1
        else
            s = :unknown
        end
        
        dir = nothing
        if contains(string(s), "__up")
            dir = :up
            s = join(split(string(s), "__")[1:end-1], "__")|>symbol
        elseif contains(string(s), "__down")
            dir = :down
            s = join(split(string(s), "__")[1:end-1], "__")|>symbol
        end
        
        samp = k.sample
        if samp==datasamp
            samp = :DATA
        end
        
        kk = k.lepton, k.iso, samp, s, dir
        if haskey(MH, kk)
            error("$kk already in keys: $k, $(KK[kk])")
        end

        KK[kk...] = k
        MH[kk...] = hists[k] 
    end
    
    ret["DATA"] = MH[lepton, :iso, :DATA, :unknown, nothing]
    
    for s in mcsamples
        k = (lepton, :iso, s, :nominal, nothing)
        if haskey(MH, kk)
            ret[string(s)] = lumis[lepton] * MH[k]
        else
            warn("$k not found, histogram will be set to EMPTY")

            #create a new, empty histogram with the same binning as the data histogram
            x = Histogram(ret["DATA"].bin_edges)
            ret[string(s)] = x
        end
    end
    
    for k in [:comphep_anom_unphys, :comphep_anom_0100, :comphep_nominal]
        ret["tchan__$k"] = lumis[lepton] * MH[
            (lepton, :iso, :tchan, k, nothing)
        ]
    end

    aiso_mcs = Any[]
    for mcs in [:ttjets, :tchan, :wjets]
        k = (lepton, :antiiso, mcs, :nominal, nothing)
        if k in keys(MH)
            push!(aiso_mcs, lumis[lepton] * MH[k])
        else
            warn("$k not found")
        end
    end
    mc_aiso = sum(aiso_mcs)
    ret["antiiso_mc"] = mc_aiso

    qcd_sf = get_sf(njet, ntag, lepton)

    ret["antiiso_data"] = MH[(lepton, :antiiso, :DATA, :unknown, nothing)]
    ret["qcd"] = qcd_sf * (ret["antiiso_data"] - mc_aiso)

    makepositive!(ret["qcd"])
    
    systs = Dict()
    
    for samp in [:wjets, :tchan, :ttjets]
        for v in map(x->x[4], keys(MH))
            for d in [:up, :down]

                k = (lepton, :iso, samp, v, d)
                if k in keys(MH)
                    ret["$(samp)__$(v)__$(d)"] = lumis[lepton] * MH[k]
                end
            end
        end
    end
    return ret
end

function prep_transfermatrix(hists; separate_lepton_charge=true)
    MH = Dict()
    for k in keys(hists)
        typeof(k) <: Dict || continue
        k[:obj] == :transfer_matrix || continue
        
        s = k[:scenario]
        lepid = abs(k[:true_lep])
        (lepid == 13 || lepid == 11) || continue

        dir = nothing
        if contains(string(s), "__up")
            dir = :up
            s = join(split(string(s), "__")[1:end-1], "__")|>symbol
        elseif contains(string(s), "__down")
            dir = :down
            s = join(split(string(s), "__")[1:end-1], "__")|>symbol
        end

        if separate_lepton_charge
            truelep = string(k[:true_lep]>0 ? "m" : "p", lepid)
        else
            truelep = string(lepid)
        end

        lumi = lumis_id[lepid]
        h = lumi * hists[k]

        k = ((s==:nominal)||(s==:unweighted)) ? "tm__pdgid_$(truelep)__$(s)" : "tm__pdgid_$(truelep)__$(s)__$(dir)"

        if k in keys(MH)
            MH[k] += h
        else
            MH[k] = h
        end
    end
    return MH
end
