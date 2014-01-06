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
    "systematic",
    "sample",
    "cos_theta_lj",
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
for i=1:nrow(df)
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

  k = "$(lepton)/$(njets)j/$(ntags)t/$(syst)/$(sample)"

  for var in [:cos_theta_lj, :met, :mtw, :bdt_sig_bg]
    k1 = "$(k)/$(var)"
    if !in(k1, keys(res))
      res[k1] = Histogram(hdescs[var]...)
    end
    hfill!(res[k1], df.tree[var])
  end

  N += 1
end

NB=NB/1024/1024
q = toq();
println("$N $(nrow(df)) $(NB)Mb $(q)s")

for k in keys(res)
  println(k, " ", sum(res[k].bin_entries))
end
