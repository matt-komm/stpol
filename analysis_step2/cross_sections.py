WJets_lo_nnlo_scale_factor = 1.1926710526315789

xs = {

	#Cross-sections from AN2012-273-v7, page 4
	  "T_t": 56.4
	, "Tbar_t": 30.7
	, "T_s": 3.79
	, "Tbar_s": 1.76
	, "T_tW": 11.1
	, "Tbar_tW": 11.1
	, "TTbar": 234
	, "WJets": 36257.2 #30400.0 inclusive

	#FIXME: ttbar branching ratio
	, "TTJets_SemiLept": (0.676*0.326*2) * 234
	, "TTJets_FullLept": (0.326**2) * 234

	#exclusive sample branching ratios, same as PREP
	, "W1Jets": 5400.0 * WJets_lo_nnlo_scale_factor
	, "W2Jets": 1750.0 * WJets_lo_nnlo_scale_factor
	, "W3Jets": 519.0 * WJets_lo_nnlo_scale_factor
	, "W4Jets": 214.0 * WJets_lo_nnlo_scale_factor

    #http://cms.cern.ch/iCMS/prep/requestmanagement?dsn=*GJets_HT-*_8TeV-madgraph*
    , "GJets1": 960.5 #200To400
	, "GJets2": 107.5 #400ToInf

	, "DYJets": 3503.71
	, "WW": 54.838
	, "WZ": 32.3161
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
}

