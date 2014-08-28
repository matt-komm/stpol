p = "../../results/nominal"

for x in [
    (:tchan, ["T_t_ToLeptons", "Tbar_t_ToLeptons"]),
    (:twchan, ["T_tW", "Tbar_tW"]),
    (:schan, ["T_s", "Tbar_s"]),
#    (:wjets, ["W1Jets_exclusive", "W2Jets_exclusive", "W3Jets_exclusive", "W4Jets_exclusive"]),
    (:data_mu, ["SingleMu1", "SingleMu2", "SingleMu3", "SingleMu_miss"]),
    (:data_mu_1, ["SingleMu1"]),
    (:data_mu_2, ["SingleMu2"]),
    (:data_mu_3, ["SingleMu3"]),
    (:data_mu_miss, ["SingleMu_miss"]),
    (:data_ele, ["SingleEle1", "SingleEle2", "SingleEle_miss"]),
    (:diboson, ["WW", "WZ", "ZZ"]),
    (:gjets, ["GJets1", "GJets2"]),
    (:dyjets, ["DYJets"]),
#    (:ttjets, ["TTJets_FullLept", "TTJets_SemiLept"]),
    (:qcd, ["QCDMu",
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
        "QCD_Pt_80_170_EMEnriched"])
    ]

    sample = x[1]
    paths = ASCIIString[]
    for z in x[2]
        ls = readdir("$p/$z")
        println(z, " ", ls)
        for l in ls
            f = "$p/$z/$l/output.root"
            isfile(f) && push!(paths, f)
        end
    end
    length(paths)==0 && error("no files selected for $x")
    run(`julia yields.jl $sample $paths`)
end
