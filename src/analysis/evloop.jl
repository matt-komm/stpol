#!/home/joosep/.julia/ROOT/julia
include("histo.jl");
include("base.jl");
include("../skim/xs.jl");
using DataFrames, ROOT, Hist

inf = ARGS[1]
ofname = ARGS[2]

df = TreeDataFrame(inf);
println("opened TTree $inf with branches: ", join(zip(names(df), types(df)), ','))
tic()
ROOT.set_branch_status!(df.tree, "*", false);
for k in [
    "hlt_mu", "hlt_ele",
    "n_signal_mu", "n_signal_ele",
    "n_veto_mu", "n_veto_ele",
    "systematic", "isolation",
    "sample",
    "cos_theta_lj", "cos_theta_lj_gen",
    "xsweight",
    "pu_weight", "pu_weight__up", "pu_weight__down",

    "lepton_weight__id", "lepton_weight__id__up", "lepton_weight__id__down",
    "lepton_weight__iso", "lepton_weight__iso__up", "lepton_weight__iso__down",
    "lepton_weight__trigger", "lepton_weight__trigger__up", "lepton_weight__trigger__down",
    
    "njets", "ntags", "lepton_type", "met", "mtw",
    "bdt_sig_bg", "C", "lepton_pt", "ljet_eta",
    "bjet_dr", "ljet_dr"
    ]
    ROOT.set_branch_status!(df.tree, "$k*", true);
end

NB = 0
N = 0

res = Dict() #histograms
# dfres = Dict() #dataframe

bins = {:cos_theta=>vcat(-Inf, linspace(-1, 1, 21))}
hdescs = {
  :cos_theta_lj=>(Histogram, bins[:cos_theta]),

  :cos_theta_gen_reco=>(NHistogram, {bins[:cos_theta], bins[:cos_theta]})
}

println("looping over ", nrow(df), " events")

function gethist(res, k, var)
  subk = "$k/$var"
  if !in(subk, keys(res))
    T, args = hdescs[var]
    res[subk] = T(args)
  end
  return res[subk]
end

for i=1:nrow(df)
  cache = Dict()
  
  if (i%10000 == 0)
      print(".")
  end
  
  NB += ROOT.getentry!(df.tree, i);
  
  cache[:xsweight] = df.tree[:xsweight]

  for sw in syst_weights
    cache[sw] = df.tree[sw]
  end

  n_signal_mu = df.tree[:n_signal_mu]
  n_signal_ele = df.tree[:n_signal_ele]
  hlt_mu = df.tree[:hlt_mu]
  hlt_ele = df.tree[:hlt_ele]

  lepton = int(df.tree[:lepton_type])
  cos_theta_lj_gen = df.tree[:cos_theta_lj_gen]
  cos_theta_lj_reco = df.tree[:cos_theta_lj]

  # sig_df = similar(DataFrame(
  #   lepton_type=Int64[],
  #   cos_theta_lj_gen=Float64[],
  #   cos_theta_lj_reco=Float64[]
  # ), 1)
  # sig_df[1, :lepton_type] = lepton
  # sig_df[1, :cos_theta_lj_gen] = cos_theta_lj_gen


  (isna(n_signal_mu) || isna(n_signal_ele) || isna(hlt_mu) || isna(hlt_ele)) && continue

  if !(
    (n_signal_mu==1 && n_signal_ele==0 && hlt_mu) ||
    (n_signal_mu==0 && n_signal_ele==1 && hlt_ele)
  )
    continue
  end

  n_veto_mu = df.tree[:n_veto_mu]
  n_veto_ele = df.tree[:n_veto_ele]

  (isna(n_veto_mu) || isna(n_veto_ele)) && continue

  if !(n_veto_mu==0 && n_veto_ele==0)
    continue
  end

  njets = df.tree[:njets]
  ntags = df.tree[:ntags]
  (isna(ntags) || ntags<=0) && continue

  syst = df.tree[:systematic]
  
  isna(lepton) && continue
  
  if lepton==13
      leptype=:muon
  elseif lepton==11
      leptype=:electron
  else
      continue
  end
  
  passes_met = false
  
  met = df.tree[:met]
  mtw = df.tree[:mtw]
  (isna(met) || isna(mtw)) && continue

  !((leptype==:electron && met > 45) || (leptype==:muon && mtw > 50)) && continue
  passes_met = true
    
  bjet_dr = df.tree[:bjet_dr]
  ljet_dr = df.tree[:ljet_dr]

  if (isna(bjet_dr) || isna(ljet_dr) || bjet_dr < 0.5 || ljet_dr < 0.5)
    continue
  end

  cache[:cos_theta_lj] = df.tree[:cos_theta_lj]
  cache[:cos_theta_lj_gen] = df.tree[:cos_theta_lj_gen]
  sample = hmap[:from][int(df.tree[:sample])]
  syst = hmap[:from][int(df.tree[:systematic])]
  iso = hmap[:from][int(df.tree[:isolation])]

  weight = 1.0
  if ((sample != "data_mu") && (sample != "data_ele"))
      weight = weight * cache[:xsweight] * cache[:pu_weight]
  end
  
  weights = Dict()
  if syst == "nominal"
      weights[:pu_weight__up] = weight * cache[:pu_weight__up] / cache[:pu_weight]
      weights[:pu_weight__down] = weight * cache[:pu_weight__down] / cache[:pu_weight]

      weights[:lepton_weight__id__up] = weight * df.tree[:lepton_weight__id__up] / cache[:lepton_weight__id]
      weights[:lepton_weight__id__down] = weight * df.tree[:lepton_weight__id__down] / cache[:lepton_weight__id]

      weights[:lepton_weight__iso__up] = weight * df.tree[:lepton_weight__iso__up] / cache[:lepton_weight__iso]
      weights[:lepton_weight__iso__down] = weight * df.tree[:lepton_weight__iso__down] / cache[:lepton_weight__iso]

      weights[:lepton_weight__trigger__up] = weight * df.tree[:lepton_weight__trigger__up] / cache[:lepton_weight__trigger]
      weights[:lepton_weight__trigger__down] = weight * df.tree[:lepton_weight__trigger__down] / cache[:lepton_weight__trigger]
  end

  bdt = df.tree[:bdt_sig_bg]
  for bdt_cut in linspace(-1, 1, 21)
    bdts = @sprintf("%.2f", bdt_cut)
    hn ="$leptype/$iso/$syst/$njets/$ntags/$sample/met__$passes_met/$bdts" 

    passes_bdt = bdt < bdt_cut
    genval = passes_bdt ? cache[:cos_theta_lj_gen] : NA

    hgr = gethist(res, hn, :cos_theta_gen_reco)
    #println("$bdt_cut $passes_bdt", cache[:cos_theta_lj], " ", cache[:cos_theta_lj_gen], " ", findbin_nd(hgr, {cache[:cos_theta_lj], cache[:cos_theta_lj_gen]}))
    hfill!(hgr, {cache[:cos_theta_lj], genval}, weight)

    passes_bdt && continue
   
    h = gethist(res, hn, :cos_theta_lj)
    hfill!(h, cache[:cos_theta_lj], weight)
    
    for (wn, w) in weights 
        h = gethist(res, "$hn/$wn", :cos_theta_lj)
        hfill!(h, cache[:cos_theta_lj], w)
    end

  end
  
  N += 1
end

NB=NB/1024/1024
q = toq();
println("$N $(nrow(df)) $(NB)Mb $(q)s")

of = jldopen("$ofname.histograms.jld", "w")
write(of, "res", res)
println("wrote $(length(res)) histograms")

# of = jldopen("$ofname.df.jld", "w")
# write(of, "res", dfres)
# println("wrote $(length(dfres)) dataframes")
# for (k, v) in dfres
#     println(k, " ", join(types(v), ","))
# end
