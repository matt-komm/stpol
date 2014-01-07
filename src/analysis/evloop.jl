include("histo.jl");
include("base.jl");
using ROOT, DataFrames, Hist

df = TreeDataFrame("$BASE/results/1t.root");

tic()
ROOT.set_branch_status!(df.tree, "*", false);
for k in [
    "hlt_mu", "hlt_ele",
    "n_signal_mu", "n_signal_ele",
    "n_veto_mu", "n_veto_ele",
    "systematic", "isolation",
    "sample",
    "cos_theta_lj", "xsweight", "pu_weight",
    "njets", "ntags", "lepton_type", "met", "mtw",
    "bdt_sig_bg", "C", "lepton_pt", "ljet_eta"
    ]
    ROOT.set_branch_status!(df.tree, "$k*", true);
end

h = Histogram(100, -1, 1)
NB = 0
N = 0

res = Dict()
hdescs = {
  :cos_theta_lj=>(120, -1, 1),
  :met=>(120, 0, 300),
  :mtw=>(120, 0, 300),
  :bdt_sig_bg=>(120, -1, 1),
  :C=>(120, 0, 1),
  :lepton_pt=>(120, 0, 300),
  :ljet_eta=>(120, -5, 5)
}

println("looping over ", nrow(df), " events")

function createhist(res, k, var)
  if !in(k, keys(res))
    res[k] = Histogram(hdescs[var]...)
  end
end

function fillhists(res, k, cache)
  for var in [:cos_theta_lj, :met, :mtw, :bdt_sig_bg]
    if !in(var, keys(cache))
      cache[var] = df.tree[var]
    end

    k1 = "$(k)/$(var)"
    createhist(res, "$(k1)/unweighted", var)
    hfill!(
      res["$k1/unweighted"],
      cache[var],
      cache[:xsweight]
    )

    createhist(res, "$(k1)/pu_weighted", var)
    hfill!(
      res["$k1/pu_weighted"],
      cache[var],
      cache[:xsweight] * cache[:pu_weight]
    )
  end
end

for i=1:nrow(df)
  cache = Dict()
  cache[:xsweight] = df.tree[:xsweight]
  cache[:pu_weight] = df.tree[:pu_weight]

  NB += ROOT.getentry!(df.tree, i);

  n_signal_mu = df.tree[:n_signal_mu]
  n_signal_ele = df.tree[:n_signal_ele]
  hlt_mu = df.tree[:hlt_mu]
  hlt_ele = df.tree[:hlt_ele]
  if !(
    (n_signal_mu==1 && n_signal_ele==0 && hlt_mu) ||
    (n_signal_mu==0 && n_signal_ele==1 && hlt_ele)
  )
    continue
  end

  n_veto_mu = df.tree[:n_veto_mu];
  n_veto_ele = df.tree[:n_veto_ele];
  if !(n_veto_mu==0 && n_veto_ele==0)
    continue
  end

  njets = df.tree[:njets];
  ntags = df.tree[:ntags];

  syst = df.tree[:systematic];
  sample = df.tree[:sample];
  
  lepton = int(df.tree[:lepton_type]);

  iso = df.tree[:isolation]

  k = "$(iso)/$(lepton)/$(njets)j/$(ntags)t/met_off/$(syst)/$(sample)"
  fillhists(res, k, cache)

  passes_met = false
  met = df.tree[:met]
  if (met>45)
    k = "$(iso)/$(lepton)/$(njets)j/$(ntags)t/met_45/$(syst)/$(sample)"
    fillhists(res, k, cache)
    passes_met = true
  end
  if (met>55)
    k = "$(iso)/$(lepton)/$(njets)j/$(ntags)t/met_55/$(syst)/$(sample)"
    fillhists(res, k, cache)
    passes_met = true
  end

  mtw = df.tree[:mtw]
  if (mtw>50)
    k = "$(iso)/$(lepton)/$(njets)j/$(ntags)t/mtw_50/$(syst)/$(sample)"
    fillhists(res, k, cache)
    passes_met = true
  end
  if (mtw>60)
    k = "$(iso)/$(lepton)/$(njets)j/$(ntags)t/mtw_60/$(syst)/$(sample)"
    fillhists(res, k, cache)
    passes_met = true
  end

  !((lepton==11 && met > 45) || (lepton==13 && mtw > 50)) && continue

  bdt = df.tree[:bdt_sig_bg]
  for bdt_cut in linspace(-1.0, 1.0, 6)
    bdt < bdt_cut && continue
    bdts = @sprintf("%.2f", bdt_cut)
    k = "$(iso)/$(lepton)/$(njets)j/$(ntags)t/met_on/bdt_$(bdts)/$(syst)/$(sample)"
    fillhists(res, k, cache)
  end

  N += 1
end

NB=NB/1024/1024
q = toq();
println("$N $(nrow(df)) $(NB)Mb $(q)s")

ofdir="OUT"
for k in keys(res)
  println(k, " ", sum(res[k].bin_entries))
  fname = "$ofdir/$k.csv"
  mkpath(dirname(fname))
  writetable(fname, todf(res[k]))
end
