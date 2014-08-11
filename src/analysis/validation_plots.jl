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
const p = "../../results/hists/Aug5/merged"
#const out = ARGS[2]
const out = "temp"

for lepton in [:mu, :ele]
    
    hd = load_hists_from_file("$p/2j_0t/0.60000/$lepton/cos_theta_lj.root") |> remove_prefix;
    wjets_sf = integral(hd["DATA"]) / integral(hd["wjets"] + hd["ttjets"] + hd["qcd"] + hd["tchan"] + hd["diboson"] + hd["dyjets"])
    println(wjets_sf)
    hd["wjets"] = wjets_sf * hd["wjets"]

    # hd = reweight_hists_to_fitres(FITRESULTS[lepton], hd)
    combdraw(hd|>drb4, :cos_theta_lj)
    svfg("$out/cos_theta_lj__2j_0t__bdt_0_60__$(lepton)")
 
    hd = load_hists_from_file("$p/0.60000/$lepton/cos_theta_lj.root") |> remove_prefix;
    hd = reweight_hists_to_fitres(FITRESULTS[lepton], hd)
    combdraw(hd|>drb4, :cos_theta_lj)
    svfg("$out/cos_theta_lj__2j_1t__bdt_0_60__$(lepton)")
    
    hd = load_hists_from_file("$p/3j_2t/0.60000/$lepton/cos_theta_lj.root") |> remove_prefix;
    hd = reweight_hists_to_fitres(FITRESULTS[lepton], hd)
    combdraw(hd|>drb4, :cos_theta_lj)
    svfg("$out/cos_theta_lj__3j_2t__bdt_0_60__$(lepton)")
    
    hd = load_hists_from_file("$p/3j_1t/0.60000/$lepton/cos_theta_lj.root") |> remove_prefix;
    hd = reweight_hists_to_fitres(FITRESULTS[lepton], hd)
    combdraw(hd|>drb4, :cos_theta_lj)
    svfg("$out/cos_theta_lj__3j_1t__bdt_0_60__$(lepton)")
   
   
    for (nj, nt) in [(2, 1), (2, 0), (3, 1), (3, 2)]
        #for var in [:abs_ljet_eta, :C, :bdt_sig_bg, :met, :mtw, :cos_theta_lj]
        for var in [:bdt_sig_bg, :cos_theta_lj]
            hd = load_hists_from_file("$p/preselection/$(nj)j_$(nt)t/$lepton/$var.root") |> remove_prefix;
            if nt != 0
                hd = reweight_hists_to_fitres(FITRESULTS[lepton], hd)
            else
                wjets_sf = integral(hd["DATA"]) / integral(hd["wjets"] + hd["ttjets"] + hd["qcd"] + hd["tchan"] + hd["diboson"] + hd["dyjets"])
                println(wjets_sf)
                hd["wjets"] = wjets_sf * hd["wjets"]
            end
            combdraw(hd, var)
            svfg("$out/$(var)__$(nj)j_$(nt)t__$(lepton)")
            
            if var == :cos_theta_lj 
            end
        end
    end
    
    for (nj, nt) in [(2, 1), (2, 0), (3, 1), (3, 2)]
        for var in [:bdt_qcd]
            hd = load_hists_from_file("$p/preqcd/$(nj)j_$(nt)t/$lepton/$var.root") |> remove_prefix;
            if nt != 0
                hd = reweight_hists_to_fitres(FITRESULTS[lepton], hd)
            else
                wjets_sf = integral(hd["DATA"]) / integral(hd["wjets"] + hd["ttjets"] + hd["qcd"] + hd["tchan"] + hd["diboson"] + hd["dyjets"])
                println(wjets_sf)
                hd["wjets"] = wjets_sf * hd["wjets"]
            end
            combdraw(hd, var)
            svfg("$out/$(var)__$(nj)j_$(nt)t__$(lepton)")
            
            if var == :cos_theta_lj 
            end
        end
    end
end
                
