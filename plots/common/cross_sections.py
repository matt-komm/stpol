WJets_lo_nnlo_scale_factor = 37509/30400.0

WJets_sherpa_weight_factor = 34821360.0/96770560.0
xs = {

	#Cross-sections from AN2012-273-v7, page 4
      "T_t": 56.4
	, "T_t_ToLeptons": 0.326*56.4
	, "Tbar_t": 30.7
    , "Tbar_t_ToLeptons": 0.326*30.7
	, "T_s": 3.79
	, "Tbar_s": 1.76
	, "T_tW": 11.1
	, "Tbar_tW": 11.1
	, "TTJets_MassiveBinDECAY": 245.8 #inclusive
    , "WJets_inclusive": 37509 #30400.0 LO

	#FIXME: ttbar branching ratio
	, "TTJets_SemiLept": (0.676*0.326*2) * 245.8 #[arxiv:1303.6254]
	, "TTJets_FullLept": (0.326**2) * 245.8 #[arxiv:1303.6254]

	#exclusive sample branching ratios, same as PREP
	, "W1Jets_exclusive": 5400.0 * WJets_lo_nnlo_scale_factor
	, "W2Jets_exclusive": 1750.0 * WJets_lo_nnlo_scale_factor
	, "W3Jets_exclusive": 519.0 * WJets_lo_nnlo_scale_factor
	, "W4Jets_exclusive": 214.0 * WJets_lo_nnlo_scale_factor

    #http://cms.cern.ch/iCMS/prep/requestmanagement?dsn=WJets_0p1_1p2_2p10_3p20_4p20_5p20_CT10_8TeV-sherpa
    ,"WJets_sherpa": 30503.0 * WJets_lo_nnlo_scale_factor / WJets_sherpa_weight_factor

	#http://cms.cern.ch/iCMS/prep/requestmanagement?dsn=*GJets_HT-*_8TeV-madgraph*
	, "GJets1": 960.5 #200To400
	, "GJets2": 107.5 #400ToInf

	, "DYJets": 3503.71
	, "WW": 54.838
	, "WZ": 33.21
	, "ZZ": 8.059
	, "QCDMu": 134680

	#http://cms.cern.ch/iCMS/prep/requestmanagement?dsn=QCD_Pt_*_*_EMEnriched_TuneZ2star_8TeV_pythia6*
	, "QCD_Pt_20_30_EMEnriched": 2.886E8*0.0101
	, "QCD_Pt_30_80_EMEnriched": 7.433E7*0.0621
	, "QCD_Pt_80_170_EMEnriched": 1191000.0*0.1539
	, "QCD_Pt_170_250_EMEnriched": 30990.0*0.148
	, "QCD_Pt_250_350_EMEnriched": 4250.0*0.131
	, "QCD_Pt_350_EMEnriched": 810.0*0.11

	#http://cms.cern.ch/iCMS/prep/requestmanagement?dsn=QCD_Pt_*_*_BCtoE_TuneZ2star_8TeV_pythia6*
	, "QCD_Pt_20_30_BCtoE": 2.886E8*0.00058
	, "QCD_Pt_30_80_BCtoE": 7.424E7*0.00225
	, "QCD_Pt_80_170_BCtoE": 1191000.0*0.0109
	, "QCD_Pt_170_250_BCtoE": 30980.0*0.0204
	, "QCD_Pt_250_350_BCtoE": 4250.0*0.0243
	, "QCD_Pt_350_BCtoE": 811.0*0.0295

	#These are here for convenience (no effect)
	, "SingleMu": 1.0
	, "SingleEle": 1.0

}

#systematics:
xs["TTJets_scaleup"] = xs["TTJets_MassiveBinDECAY"]
xs["TTJets_scaledown"] = xs["TTJets_MassiveBinDECAY"]
xs["TTJets_matchingup"] = xs["TTJets_MassiveBinDECAY"]
xs["TTJets_matchingdown"] = xs["TTJets_MassiveBinDECAY"]
xs["TTJets_mass169_5"] = xs["TTJets_MassiveBinDECAY"]
xs["TTJets_mass175_5"] = xs["TTJets_MassiveBinDECAY"]
xs["T_t_ToLeptons_scaleup"] = xs["T_t_ToLeptons"]
xs["T_t_ToLeptons_scaledown"] = xs["T_t_ToLeptons"]
xs["Tbar_t_ToLeptons_scaleup"] = xs["Tbar_t_ToLeptons"]
xs["Tbar_t_ToLeptons_scaledown"] = xs["Tbar_t_ToLeptons"]
xs["Tbar_t_ToLeptons_mass175_5"] = xs["Tbar_t_ToLeptons"]
xs["Tbar_t_ToLeptons_mass169_5"] = xs["Tbar_t_ToLeptons"]

xs["T_t_ToLeptons_mass169_5"] = xs["T_t_ToLeptons"]
xs["T_t_ToLeptons_mass175_5"] = xs["T_t_ToLeptons"]

xs["TToBMuNu_t-channel"] = (xs["T_t_ToLeptons"] + xs["Tbar_t_ToLeptons"]) / 3
xs["TToBENu_t-channel"] = xs["TToBMuNu_t-channel"]
xs["TToBTauNu_t-channel"] = xs["TToBMuNu_t-channel"]
xs["TToBENu_anomWtb-0100_t-channel"] = xs["TToBMuNu_t-channel"]
xs["TToBMuNu_anomWtb-0100_t-channel"] = xs["TToBMuNu_t-channel"]
xs["TToBTauNu_anomWtb-0100_t-channel"] = xs["TToBMuNu_t-channel"]
xs["TToBENu_anomWtb-unphys_t-channel"] = xs["TToBMuNu_t-channel"]
xs["TToBMuNu_anomWtb-unphys_t-channel"] = xs["TToBMuNu_t-channel"]
xs["TToBTauNu_anomWtb-unphys_t-channel"] = xs["TToBMuNu_t-channel"]

xs["WJetsToLNu_matchingdown"] = xs["WJets_inclusive"]
xs["WJetsToLNu_matchingup"] = xs["WJets_inclusive"]
xs["WJetsToLNu_scaledown"] = xs["WJets_inclusive"]
xs["WJetsToLNu_scaleup"] = xs["WJets_inclusive"]

#Define the cross-sections for the W+jets fastsim samples
for nj in [1,2,3,4]:
    for syst in ["", "_nominal", "_matchingup", "_matchingdown", "_scaleup", "_scaledown"]:
        xs["W%dJetsToLNu"%nj + syst] = xs["W%dJets_exclusive" % nj]
        xs["W%dJets_FSIM"%nj + syst] = xs["W%dJets_exclusive" % nj]

# Use this dict to create lumis corresponding to step2 processings.
# Please don't overwrite old lumis
lumis = dict()
lumis["83a02e9_Jul22"] = dict()
lumis["83a02e9_Jul22"]["iso"] = dict()
lumis["83a02e9_Jul22"]["antiiso"] = dict()
lumis["83a02e9_Jul22"]["iso"]["mu"] = 6784+6398+5277
lumis["83a02e9_Jul22"]["iso"]["ele"] = 12410+6144
lumis["83a02e9_Jul22"]["antiiso"] = lumis["83a02e9_Jul22"]["iso"]

lumis["Aug4_0eb863_full"] = dict()
lumis["Aug4_0eb863_full"]["iso"] = dict()
lumis["Aug4_0eb863_full"]["antiiso"] = dict()
lumis["Aug4_0eb863_full"]["iso"]["mu"] = 1094 + 5319 + 6512 + 6823
lumis["Aug4_0eb863_full"]["iso"]["ele"] = 917 + 12378 + 6421
lumis["Aug4_0eb863_full"]["antiiso"]["mu"] = 1094 + 5319 + 6528 + 6823
lumis["Aug4_0eb863_full"]["antiiso"]["ele"] = 917 + 12409 + 6482

lumis["343e0a9_Aug22"] = dict()
lumis["343e0a9_Aug22"]["iso"] = dict()
lumis["343e0a9_Aug22"]["antiiso"] = dict()
lumis["343e0a9_Aug22"]["iso"]["mu"] = 19757
lumis["343e0a9_Aug22"]["iso"]["ele"] = 19767
lumis["343e0a9_Aug22"]["antiiso"] = lumis["343e0a9_Aug22"]["iso"]

lumis["343e0a9_Aug22_newLumiCal"] = dict()
lumis["343e0a9_Aug22_newLumiCal"]["iso"] = dict()
lumis["343e0a9_Aug22_newLumiCal"]["antiiso"] = dict()
lumis["343e0a9_Aug22_newLumiCal"]["iso"]["mu"] = 19680
lumis["343e0a9_Aug22_newLumiCal"]["iso"]["ele"] = 19690
lumis["343e0a9_Aug22_newLumiCal"]["antiiso"] = lumis["343e0a9_Aug22"]["iso"]

# References to the 'latest' luminosities.
lumi_iso = {
    "ele": lumis["343e0a9_Aug22_newLumiCal"]["iso"]["ele"],
    "mu": lumis["343e0a9_Aug22_newLumiCal"]["iso"]["mu"]
}

lumi_antiiso = {
    "ele": lumis["343e0a9_Aug22_newLumiCal"]["antiiso"]["ele"],
    "mu": lumis["343e0a9_Aug22_newLumiCal"]["antiiso"]["mu"]
}
