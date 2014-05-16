require("base.jl")
using CMSSW

infile = ARGS[1]

const df_base = TreeDataFrame(infile)
const df_added = TreeDataFrame("$infile.added")

samples = df_base[:sample]
iso = df_base[:isolation]
syst = df_base[:systematic]

noms = (
    (samples .== hmap[:to]["tchan"]) & 
    (iso .== hmap[:to]["iso"]) & 

    ((syst .== hmap[:to]["nominal"]) | 
    (syst .== hmap[:to]["signal_comphep_anomWtb-0100"]) | 
    (syst .== hmap[:to]["signal_comphep_anomWtb-unphys"]) | 
    (syst .== hmap[:to]["signal_comphep_nominal"]))
)

ba = BitArray(length(noms))
for i=1:length(noms)
    ba[i] = noms[i]
end

println("loading main df")
df = df_base[ba,
    [
    :cos_theta_lj, :cos_theta_lj_gen,
    :hlt_mu, :hlt_ele,
    :njets, :ntags,
    :lepton_type, :n_signal_mu, :n_signal_ele,
    :n_veto_mu, :n_veto_ele,
    :systematic, :subsample,
    :pu_weight,
    :ljet_dr, :bjet_dr,
    ]
]

println("loading added df")
df2 = df_added[ba, [:bdt_sig_bg, :bdt_qcd, :xsweight]]
println("catting")
df = hcat(df, df2)

#apply the selection cuts
is_reco = (Cuts.is_mu(df) | Cuts.is_ele(df)) & Cuts.njets(df, 2) &
    Cuts.ntags(df, 1) & Cuts.dr(df) & 
    (Cuts.qcd_mva_wp(df, :mu) | Cuts.qcd_mva_wp(df, :ele))
is_reco[isna(is_reco)] = false

df[:is_reco] = is_reco
df[:weight] = df[:xsweight] .* df[:pu_weight]
df[:weight][isna(df[:weight])] = 0.0

df[:sample] = ""
for s in [
    "T_t", "Tbar_t", #inclusive
    "T_t_ToLeptons", "Tbar_t_ToLeptons", #exclusive

    #anomalous
    "TToBENu_anomWtb-unphys_t-channel", "TToBENu_anomWtb-0100_t-channel", "TToBENu_t-channel",
    "TToBMuNu_anomWtb-unphys_t-channel", "TToBMuNu_anomWtb-0100_t-channel", "TToBMuNu_t-channel",
    "TToBTauNu_anomWtb-unphys_t-channel", "TToBTauNu_anomWtb-0100_t-channel", "TToBTauNu_t-channel"]
    idx = df[:subsample] .== hmap[:to][s]
    df[idx, :sample] = s
end
size(df, 1) > 0 &&any(df[:sample] .== "") && error("unset sample: $(unique(df[:subsample])[:])")
df[:sample_hash] = convert(Vector{Uint64}, map(x -> uint(hash(x)), df[:sample]))

df_sel = df[:,
    [:lepton_type, :cos_theta_lj, :cos_theta_lj_gen,
    :is_reco, :weight, :sample, :sample_hash]
]
df_sel[:bdt] = df[:bdt_sig_bg]

any(isna(df[:cos_theta_lj][df[:is_reco]])) && error("reconstructed event had NA cos theta")

println("writing output")
println(df_sel)
outfile = ARGS[2]
tempf = mktemp()[1]
writetree(tempf, df_sel)

for i=1:5
    try
        println("cleaning $outfile...");isfile(outfile) && rm(outfile)
        println("copying...");cp(tempf, outfile)
        s = stat(outfile)
        s.size == 0 && error("file corrupted $s")
        break
    catch err
        println("$err: retrying")
        sleep(5)
    end
end
