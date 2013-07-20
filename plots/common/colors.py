import ROOT

#Different subtypes of the same physical samples have different names
sample_colors_separate = {
    'signal': ROOT.kRed,
    'T_t': ROOT.kRed,
    'T_t_ToLeptons+2': ROOT.kRed,
    'Tbar_t': ROOT.kRed+1,
    'Tbar_t_ToLeptons+2': ROOT.kRed+3,
    'T_tW': ROOT.kYellow+3,
    'Tbar_tW': ROOT.kYellow+4,
    'T_s': ROOT.kYellow,
    'Tbar_s': ROOT.kYellow+1,

    'DYJets': ROOT.kViolet,

    'WJets_inclusive': ROOT.kGreen,
    'W1Jets_exclusive': ROOT.kGreen+1,
    'W2Jets_exclusive': ROOT.kGreen+2,
    'W3Jets_exclusive': ROOT.kGreen+3,
    'W4Jets_exclusive': ROOT.kGreen+4,
    'WJets_sherpa_nominal': ROOT.kCyan,

    'diboson': ROOT.kBlue,
    'WW': ROOT.kBlue,
    'WZ': ROOT.kBlue,
    'ZZ': ROOT.kBlue,

    'TTJets': ROOT.kOrange,
    'TTJets_MassiveBinDECAY': ROOT.kOrange,
    'TTJets_FullLept': ROOT.kOrange+1,
    'TTJets_SemiLept': ROOT.kOrange+2,

    'QCD': ROOT.kGray,
    'QCDMu': ROOT.kGray,
    'GJets1': ROOT.kGray,
    'GJets2': ROOT.kGray,

    'QCD_Pt_20_30_EMEnriched': ROOT.kGray,
    'QCD_Pt_30_80_EMEnriched': ROOT.kGray,
    'QCD_Pt_80_170_EMEnriched': ROOT.kGray,
    'QCD_Pt_170_250_EMEnriched': ROOT.kGray,
    'QCD_Pt_250_350_EMEnriched': ROOT.kGray,
    'QCD_Pt_350_EMEnriched': ROOT.kGray,


    'QCD_Pt_20_30_BCtoE': ROOT.kGray,
    'QCD_Pt_30_80_BCtoE': ROOT.kGray,
    'QCD_Pt_80_170_BCtoE': ROOT.kGray,
    'QCD_Pt_170_250_BCtoE': ROOT.kGray,
    'QCD_Pt_250_350_BCtoE': ROOT.kGray,
    'QCD_Pt_350_BCtoE': ROOT.kGray,

    'SingleMu': ROOT.kBlack,
    'SingleEle': ROOT.kBlack,
    
    'EnDown' : ROOT.kGreen,
    'EnUp' : ROOT.kBlue,
    'ResDown' : ROOT.kBlue,
    'ResUp' : ROOT.kCyan,
    'UnclusteredEnDown' : ROOT.kRed,
    'UnclusteredEnUp' : ROOT.kOrange,
    'Nominal': ROOT.kBlack
}


#Different types of the same physical samples have the same colors
sample_colors_same = {
    'signal': ROOT.kRed,
    'T_t': ROOT.kRed,
    'Tbar_t': ROOT.kRed,
    'T_t_ToLeptons': ROOT.kRed,
    'Tbar_t_ToLeptons': ROOT.kRed,
    'T_tW': ROOT.kYellow+4,
    'Tbar_tW': ROOT.kYellow+4,
    'T_s': ROOT.kYellow,
    'Tbar_s': ROOT.kYellow,

    'DYJets': ROOT.kViolet,

    'WJets_inclusive': ROOT.kGreen,
    'W1Jets_exclusive': ROOT.kGreen,
    'W2Jets_exclusive': ROOT.kGreen,
    'W3Jets_exclusive': ROOT.kGreen,
    'W4Jets_exclusive': ROOT.kGreen,
    'WJets_sherpa_nominal': ROOT.kCyan,

    'diboson': ROOT.kBlue,
    'WW': ROOT.kBlue,
    'WZ': ROOT.kBlue,
    'ZZ': ROOT.kBlue,

    'TTJets': ROOT.kOrange,
    'TTJets_MassiveBinDECAY': ROOT.kOrange,
    'TTJets_FullLept': ROOT.kOrange,
    'TTJets_SemiLept': ROOT.kOrange,

    'QCD': ROOT.kGray,
    'QCDMu': ROOT.kGray,
    'GJets1': ROOT.kGray,
    'GJets2': ROOT.kGray,

    'QCD_Pt_20_30_EMEnriched': ROOT.kGray,
    'QCD_Pt_30_80_EMEnriched': ROOT.kGray,
    'QCD_Pt_80_170_EMEnriched': ROOT.kGray,
    'QCD_Pt_170_250_EMEnriched': ROOT.kGray,
    'QCD_Pt_250_350_EMEnriched': ROOT.kGray,
    'QCD_Pt_350_EMEnriched': ROOT.kGray,


    'QCD_Pt_20_30_BCtoE': ROOT.kGray,
    'QCD_Pt_30_80_BCtoE': ROOT.kGray,
    'QCD_Pt_80_170_BCtoE': ROOT.kGray,
    'QCD_Pt_170_250_BCtoE': ROOT.kGray,
    'QCD_Pt_250_350_BCtoE': ROOT.kGray,
    'QCD_Pt_350_BCtoE': ROOT.kGray,

    'SingleMu': ROOT.kBlack,
    'SingleEle': ROOT.kBlack
}
