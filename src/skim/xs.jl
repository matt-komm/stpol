using DataFrames

#returns a dict with :tag, :iso, :systematic, :sample classifying the sample based on the file path
function sample_type(fn, prefix="file:/hdfs/cms/store/user")
    #MC match
    r = Regex("$prefix/(.*)/(.*)/(.*)/(.*)/(.*)/output_(.*).root")
    m = match(r, fn)
    
    if m==nothing
        tag = :unknown
        syst = :unknown
        samp = :unknown
        iso = :unknown
       
        #MC did not match, try data
        cls = data_cls(fn)
        if cls != nothing
            samp = cls[2]
            iso = cls[1]
        end
    else
        tag = m.captures[2]
        iso = m.captures[3]

        syst = m.captures[4]
        samp = m.captures[5]
    end
    #TToBMuNu_anomWtb-unphys_t-channel

    while true #hack to have 'break' to match only once
    if syst == "SYST"
        ss = string(samp)
        m = match(r".*_(mass.*)", ss)
        if m != nothing
            syst = m.captures[1]
            break
        end
        
        m = match(r".*_(scale.*)", ss)
        if m != nothing
            syst = m.captures[1]
            break
        end
        
        m = match(r".*_(matching.*)", ss)
        if m != nothing
            syst = m.captures[1]
            break
        end

        m = match(r"TToB.*Nu(.*)_t-channel", ss)
        if m != nothing
            if m.captures[1] == ""
                syst = "signal_comphep_nominal"
            else
                syst = string("signal_comphep", m.captures[1])
            end
            break
        end
        
        m = match(r"W*JetsToLNu", ss)
        if m != nothing
            syst = "wjets_fsim_nominal"
            break
        end
    end
    break #in case of no match, we also want to break
    end #while

    return {:tag => string(tag), :iso => string(iso), :systematic => string(syst), :sample => string(samp)}
end

function data_cls(fn)
    if contains(fn, "/iso/SingleMu")
        return (:iso, :SingleMu)
    elseif contains(fn, "/antiiso/SingleMu")
        return (:antiiso, :SingleMu)
    elseif contains(fn, "/iso/SingleEle")
        return (:iso, :SingleEle)
    elseif contains(fn, "/antiiso/SingleEle")
        return (:antiiso, :SingleEle)
    end 
    return nothing
end

#fpath = joinpath(
#    dirname(base.source_path()), "cross_sections.txt"
#)
fpath = joinpath(
    BASE, "metadata", "cross_sections.txt"
)

df = readtable(fpath, allowcomments=true)
cross_sections = Dict{String, Float64}()
for i=1:nrow(df)
    cross_sections[df[i, 1]] = df[i, 2]
end

function xsweight(flist)
    out = Dict()
    for fi in flist
        df = readtable(fi)
        for n=1:nrow(df)
            cls = sample_type(df[n, :files])
            generated = df[n, :total_processed]
            if !haskey(out, cls)
                out[cls] = 0
            end
            out[cls] += generated
        end
    end

    ret = Dict()
    for (k, v) in out
        x = cross_sections[k[:sample]]/v
        ret[k[:sample]] = x
    end
    return ret
end

#process ->[sample1, sample2, ...]
const merges = {
    "tchan"=>
        ["T_t_ToLeptons", "Tbar_t_ToLeptons",
        "TToBENu_anomWtb-unphys_t-channel", "TToBENu_anomWtb-0100_t-channel", "TToBENu_t-channel",
        "TToBMuNu_anomWtb-unphys_t-channel", "TToBMuNu_anomWtb-0100_t-channel", "TToBMuNu_t-channel",
        "TToBTauNu_anomWtb-unphys_t-channel", "TToBTauNu_anomWtb-0100_t-channel", "TToBTauNu_t-channel",
        
        "T_t_ToLeptons_mass166_5", 
        "T_t_ToLeptons_mass169_5", 
        "Tbar_t_ToLeptons_mass166_5", 
        "Tbar_t_ToLeptons_mass169_5", 
        
        "T_t_ToLeptons_mass175_5", 
        "T_t_ToLeptons_mass178_5", 
        "Tbar_t_ToLeptons_mass175_5", 
        "Tbar_t_ToLeptons_mass178_5", 
        
        "T_t_ToLeptons_scaleup", 
        "T_t_ToLeptons_scaledown", 
        "Tbar_t_ToLeptons_scaleup", 
        "Tbar_t_ToLeptons_scaledown", 
    ],

    "tchan_inc"=>["T_t", "Tbar_t"],
    "wjets"=>[
        "W1Jets_exclusive", "W2Jets_exclusive", "W3Jets_exclusive", "W4Jets_exclusive",
        "W1JetsToLNu",
        "W1JetsToLNu_matchingdown",
        "W1JetsToLNu_matchingup",
        "W1JetsToLNu_scaleup",
        "W1JetsToLNu_scaledown",
        "W2JetsToLNu",
        "W2JetsToLNu_matchingdown",
        "W2JetsToLNu_matchingup",
        "W2JetsToLNu_scaleup",
        "W2JetsToLNu_scaledown",
        "W3JetsToLNu",
        "W3JetsToLNu_matchingdown",
        "W3JetsToLNu_matchingup",
        "W3JetsToLNu_scaleup",
        "W3JetsToLNu_scaledown",
        "W4JetsToLNu",
        "W4JetsToLNu_matchingdown",
        "W4JetsToLNu_matchingup",
        "W4JetsToLNu_scaleup",
        "W4JetsToLNu_scaledown",
    ],
    "wjets_inc"=>["WJets_inclusive"],
    "wjets_sherpa"=>["WJets_sherpa"],
    
    "ttjets"=>[
        "TTJets_FullLept", "TTJets_SemiLept",
        "TTJets_matchingdown",
        "TTJets_matchingup",
        "TTJets_scaledown",
        "TTJets_scaleup",

        "TTJets_mass166_5",
        "TTJets_mass169_5",
        "TTJets_mass175_5",
        "TTJets_mass178_5",
    ],

    "ttjets_inc"=>["TTJets_MassiveBinDECAY"],
    "twchan"=>["T_tW", "Tbar_tW"],
    "schan"=>["T_s", "Tbar_s"],
    "diboson"=>["WW", "WZ", "ZZ"],
    "dyjets"=>["DYJets"],
    "gjets"=>["GJets1", "GJets2"],
    "data_mu"=>["SingleMu", "SingleMu1", "SingleMu2", "SingleMu3", "SingleMu_miss"],
    "data_ele"=>["SingleEle", "SingleEle1", "SingleEle2", "SingleEle3", "SingleEle_miss"],
    "qcd_mc_mu"=>["QCDMu"],
    "qcd_mc_ele"=>[
        "QCD_Pt_170_250_BCtoE",
        "QCD_Pt_170_250_EMEnriched",
        "QCD_Pt_20_30_BCtoE",
        "QCD_Pt_20_30_EMEnriched",
        "QCD_Pt_250_350_BCtoE",
        "QCD_Pt_250_350_EMEnriched",
        "QCD_Pt_30_80_BCtoE",
        "QCD_Pt_30_80_EMEnriched",
        "QCD_Pt_350_BCtoE",
        "QCD_Pt_350_EMEnriched",
        "QCD_Pt_80_170_BCtoE",
        "QCD_Pt_80_170_EMEnriched",
    ],
}

function get_process(sample)
    sample = string(sample)
    for (proc, samps) in merges
        sample in samps && return symbol(proc)
    end
    return :unknown
end

function test_cls(inf)
    flist = split(readall(inf))
    for f in flist
        st = sample_type(f)
        samp = string(st[:sample])
        proc = SingleTopBase.get_process(samp)
        xs = samp in keys(SingleTopBase.cross_sections) ? SingleTopBase.cross_sections[samp] : -1.0
        println("$f $st $proc $xs")
    end
end

#create a hash-map for strings
hmap = {:to=>Dict(), :from=>Dict()}

#list of all hashmappable strings
const tomap = ASCIIString[
    "antiiso",
    "data_ele",
    "data_mu",
    "diboson",
    "DYJets",
    "dyjets",
    "EnDown",
    "EnUp",
    "gjets",
    "GJets1",
    "GJets2",
    "iso",
    "mass166_5",
    "mass169_5",
    "mass175_5",
    "mass178_5",
    "matchingdown",
    "matchingup",
    "nominal",
    "qcd_mc_ele",
    "qcd_mc_mu",
    "QCD_Pt_170_250_BCtoE",
    "QCD_Pt_170_250_EMEnriched",
    "QCD_Pt_20_30_BCtoE",
    "QCD_Pt_20_30_EMEnriched",
    "QCD_Pt_250_350_BCtoE",
    "QCD_Pt_250_350_EMEnriched",
    "QCD_Pt_30_80_BCtoE",
    "QCD_Pt_30_80_EMEnriched",
    "QCD_Pt_350_BCtoE",
    "QCD_Pt_350_EMEnriched",
    "QCD_Pt_80_170_BCtoE",
    "QCD_Pt_80_170_EMEnriched",
    "QCDMu",
    "ResDown",
    "ResUp",
    "scaledown",
    "scaleup",
    "schan",
    "signal_comphep_anomWtb-0100",
    "signal_comphep_anomWtb-unphys",
    "signal_comphep_nominal",
    "SingleEle",
    "SingleEle1",
    "SingleEle2",
    "SingleEle3",
    "SingleEle_miss",
    "SingleMu",
    "SingleMu1",
    "SingleMu2",
    "SingleMu3",
    "SingleMu_miss",
    "T_s",
    "T_t",
    "T_t_ToLeptons",
    "T_t_ToLeptons_mass166_5",
    "T_t_ToLeptons_mass169_5",
    "T_t_ToLeptons_mass175_5",
    "T_t_ToLeptons_mass178_5",
    "T_t_ToLeptons_scaledown",
    "T_t_ToLeptons_scaleup",
    "T_tW",
    "Tbar_s",
    "Tbar_t",
    "Tbar_t_ToLeptons",
    "Tbar_t_ToLeptons_mass166_5",
    "Tbar_t_ToLeptons_mass169_5",
    "Tbar_t_ToLeptons_mass175_5",
    "Tbar_t_ToLeptons_mass178_5",
    "Tbar_t_ToLeptons_scaledown",
    "Tbar_t_ToLeptons_scaleup",
    "Tbar_tW",
    "tchan", 
    "tchan_inc",
    "ttjets",
    "TTJets_FullLept",
    "ttjets_inc",
    "TTJets_mass166_5",
    "TTJets_mass169_5",
    "TTJets_mass175_5",
    "TTJets_mass178_5",
    "TTJets_MassiveBinDECAY",
    "TTJets_matchingdown",
    "TTJets_matchingup",
    "TTJets_scaledown",
    "TTJets_scaleup",
    "TTJets_SemiLept",
    "TToBENu_anomWtb-0100_t-channel",
    "TToBENu_anomWtb-unphys_t-channel",
    "TToBENu_t-channel",
    "TToBMuNu_anomWtb-0100_t-channel",
    "TToBMuNu_anomWtb-unphys_t-channel",
    "TToBMuNu_t-channel",
    "TToBTauNu_anomWtb-0100_t-channel",
    "TToBTauNu_anomWtb-unphys_t-channel",
    "TToBTauNu_t-channel",
    "twchan",
    "UnclusteredEnDown",
    "UnclusteredEnUp",
    "unknown",
    "W1Jets_exclusive",
    "W1JetsToLNu",
    "W1JetsToLNu_matchingdown",
    "W1JetsToLNu_matchingup",
    "W1JetsToLNu_scaledown",
    "W1JetsToLNu_scaleup",
    "W2Jets_exclusive",
    "W2JetsToLNu",
    "W2JetsToLNu_matchingdown",
    "W2JetsToLNu_matchingup",
    "W2JetsToLNu_scaledown",
    "W2JetsToLNu_scaleup",
    "W3Jets_exclusive",
    "W3JetsToLNu",
    "W3JetsToLNu_matchingdown",
    "W3JetsToLNu_matchingup",
    "W3JetsToLNu_scaledown",
    "W3JetsToLNu_scaleup",
    "W4Jets_exclusive",
    "W4JetsToLNu",
    "W4JetsToLNu_matchingdown",
    "W4JetsToLNu_matchingup",
    "W4JetsToLNu_scaledown",
    "W4JetsToLNu_scaleup",
    "wjets",
    "wjets_fsim_nominal",
    "wjets_inc",
    "WJets_inclusive",
    "WJets_sherpa",
    "wjets_sherpa",
    "WW",
    "WZ",
    "ZZ",
]

#convert all strings to hash, create a two-way dict
for tm in tomap
    hmap[:to][tm] = int(hash(tm))
    hmap[:from][int(hash(tm))] = tm
end

_hmap_symb_to = Dict()
for k in hmap[:to]|>keys
    _hmap_symb_to[symbol(k)] = hmap[:to][k]
end
_hmap_symb_from= Dict()
for k in hmap[:from]|>keys
    _hmap_symb_from[k] = hmap[:from][k]|>symbol
end
const hmap_symb_to = deepcopy(_hmap_symb_to)
const hmap_symb_from = deepcopy(_hmap_symb_from)

#write out the hashmap as a CSV
function write_hmap(fname)
    cv = collect(hmap[:to])

    writetable(fname,
        DataFrame(
            name=ASCIIString[x[1] for x in cv],
            hash=Int64[x[2] for x in cv]
        )
    )
end

export cross_sections, hmap_symb_from, hmap_symb_to, get_process, sample_type
