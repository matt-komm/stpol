include("base.jl")
#include("../src/fraction_fit/hists.jl")

using ROOT, ROOT.ROOTHistograms, DataFrames, SingleTopBase
import SingleTopBase: VARS
include("python_plots.jl")
include("hplot.jl")

#rebin by 4
rb4(x) = rebin(x, 2:4:nbins(x)-5)
drb4(d) = {k=>rb4(v) for (k, v) in d}

#const p = ARGS[1]
const p = "../../results/hists/Jun13"
#const out = ARGS[2]
const out = "temp"

for lepton in [:mu, :ele]
 
    hd = load_hists_from_file("$p/0.60000/$lepton/cos_theta_lj.root") |> remove_prefix;
    hd = reweight_hists_to_fitres(FITRESULTS[lepton], hd)
    combdraw(hd|>drb4, :cos_theta_lj)
    svfg("$out/cos_theta_lj__2j_1t__$(lepton)__bdt_0_60")
   
    for (nj, nt) in [(2, 1), (2, 0), (3, 2)]
        for var in [:abs_ljet_eta, :C, :bdt_sig_bg, :met, :mtw, :cos_theta_lj]
            hd = load_hists_from_file("$p/preselection/$(nj)j_$(nt)t/$lepton/$var.root") |> remove_prefix;
            if nt != 0
                hd = reweight_hists_to_fitres(FITRESULTS[lepton], hd)
            end
            combdraw(hd, var)
            svfg("$out/$(var)__$(nj)j_$(nt)t__$(lepton)")
            
            if var == :cos_theta_lj 
            end
        end
    end
end
                
