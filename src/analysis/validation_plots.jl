include("base.jl")
#include("../src/fraction_fit/hists.jl")

using ROOT, ROOT.ROOTHistograms, DataFrames, SingleTopBase
import SingleTopBase: VARS
include("python_plots.jl")
include("hplot.jl")

#const p = "$BASE/results/hists/apr15/csvt__qcd_mva__cplx/"

const p = ARGS[1]
const out = ARGS[2]

for (nj, nt) in [(2, 1), (2, 0), (3, 2)]
    for lepton in [:mu, :ele]
        for var in [:abs_ljet_eta, :C, :bdt_sig_bg, :met, :mtw, :cos_theta_lj]
            hd = load_hists_from_file("$p/preselection/$(nj)j_$(nt)t/$lepton/$var.root") |> remove_prefix;
            if nt != 0
                hd = reweight_hists_to_fitres(FITRESULTS[lepton], hd)
            end
            combdraw(hd, var)
            svfg("$out/$(var)__$(nj)j_$(nt)t__$(lepton)")
        end
    end
end
