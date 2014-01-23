#!/home/joosep/.julia/ROOT/julia
include("histo.jl");
include("base.jl");
include("../skim/xs.jl");
using ROOT, DataFrames, Hist

inf = ARGS[1]
ofname = ARGS[2]

df = TreeDataFrame(inf);
for k in sort(collect(keys(df.tree.branches)))
    println(k)
end

tic()
ROOT.set_branch_status!(df.tree, "*", false);
for k in [
    "hlt_mu", "hlt_ele",
    "n_signal_mu", "n_signal_ele",
    "n_veto_mu", "n_veto_ele",
    "systematic", "isolation",
    "sample",
    "cos_theta_lj", "xsweight",
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

h = Histogram(100, -1, 1)
NB = 0
N = 0

res = Dict()
nbins = 119
hdescs = {
  :cos_theta_lj=>(nbins, -1, 1),
  :met=>(nbins, 0, 300),
  :mtw=>(nbins, 0, 300),
  :bdt_sig_bg=>(nbins, -1, 1),
  :C=>(nbins, 0, 1),
  :lepton_pt=>(nbins, 0, 300),
  :ljet_eta=>(nbins, -5, 5),
}

println("looping over ", nrow(df), " events")

function gethist(res, k, var)
  if !in(k, keys(res))
    res[k] = Histogram(hdescs[var]...)
  end
  return res[k]
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
  
  lepton = int(df.tree[:lepton_type])
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
    bdt < bdt_cut && continue
    bdts = @sprintf("%.2f", bdt_cut)
    
    hn ="$leptype/$iso/$syst/$njets/$ntags/$sample/met__$passes_met/$bdts" 
    
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

of = jldopen(ofname, "w")
write(of, "res", res)
println("wrote $(length(res)) histograms")
close(of)
