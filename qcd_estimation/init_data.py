from Dataset import *
from DatasetGroup import *
from ROOT import *
from copy import copy, deepcopy
from plots.common.cross_sections import *

"""
init_data.py
Defines all the datasets used in the fit and files to read them from.
Each should exist for both iso and anti-iso and also systematics (En, Res, UnclusteredEn; but it's possible to fit without the systematics)
"""


groups = []
MCgroups = []
MC_groups_noQCD = []

group_IsoUp = []
group_IsoDown = []

dgDibosons = DatasetGroup("Dibosons", kBlue)
dWW = Dataset("WW", "WW.root", xs["WW"])
dWZ = Dataset("WZ", "WZ.root", xs["WZ"])
dZZ = Dataset("ZZ", "ZZ.root", xs["ZZ"])
dgDibosons.add([dWW,dWZ,dZZ])

dgQCDMu = DatasetGroup("QCD", kGray)
dQCDMu = Dataset("QCDMu", "QCDMu.root", xs["QCDMu"])
dgQCDMu.add(dQCDMu)

dgQCDEle = DatasetGroup("QCD", kGray)
dQCDEM1 = Dataset("QCD_Pt-20to30_EMEnriched", "QCD_Pt_20to30_EMEnriched.root")
dQCDEM2 = Dataset("QCD_Pt-30to80_EMEnriched", "QCD_Pt_30to80_EMEnriched.root")
dQCDEM3 = Dataset("QCD_Pt-80to170_EMEnriched", "QCD_Pt_80to170_EMEnriched.root")
dQCDBC1 = Dataset("QCD_Pt-20to30_BCtoE", "QCD_Pt_20to30_BCtoE.root")
dQCDBC2 = Dataset("QCD_Pt-30to80_BCtoE", "QCD_Pt_30to80_BCtoE.root")
dQCDBC3 = Dataset("QCD_Pt-80to170_BCtoE", "QCD_Pt_80to170_BCtoE.root")
dgQCDEle.add([dQCDEM1, dQCDEM2, dQCDEM3, dQCDBC1, dQCDBC2, dQCDBC3])

dgGJets = DatasetGroup("GJets", kCyan)
dGJHT40 = Dataset("GJets_HT-40To100", "HT_40To100.root")
dGJHT100 = Dataset("GJets_HT-100To200", "HT_100To200.root")
dGJHT200 = Dataset("GJets_HT-200", "HT_200.root")
dgGJets.add([dGJHT40, dGJHT100, dGJHT200])

dgTChExclusive = DatasetGroup("t-channel", kRed)
dgTChInclusive = DatasetGroup("t-channel", kRed)
dTCh = Dataset("t-channel", "T_t.root", xs["T_t"])
dTChExc = Dataset("t-channel_toLeptons", "T_t_ToLeptons.root", xs["T_t_ToLeptons"])
dTbarCh = Dataset("t-channel_Tbar", "Tbar_t.root", xs["Tbar_t"])
dTbarChExc = Dataset("t-channel_toLeptons_Tbar", "Tbar_t_ToLeptons.root", xs["Tbar_t_ToLeptons"])
dgTChInclusive.add([dTCh, dTbarCh])
dgTChExclusive.add([dTChExc, dTbarChExc])

dgTWCh = DatasetGroup("tW-channel", kYellow+3)
dTWCh = Dataset("tW-channel", "T_tW.root", xs["T_tW"])
dTbarWCh = Dataset("tW-channel_Tbar", "Tbar_tW.root", xs["Tbar_tW"])
dgTWCh.add([dTWCh, dTbarWCh])

dgSCh = DatasetGroup("s-channel", kYellow )
dSCh = Dataset("s-channel", "T_s.root", xs["T_s"])
dSbarCh = Dataset("s-channel_Tbar", "Tbar_s.root", xs["Tbar_s"])
dgSCh.add([dSCh,dSbarCh])

dgTTBarExclusive = DatasetGroup("t #bar{t}", kOrange)
dgTTBarInclusive = DatasetGroup("t #bar{t}", kOrange)
dTTBar = Dataset("TTJets", "TTJets_MassiveBinDECAY.root", xs["TTJets_MassiveBinDECAY"])
dTTBarFullLept = Dataset("TTJetsFullLept", "TTJets_FullLept.root", xs["TTJets_FullLept"])
dTTBarSemiLept = Dataset("TTJetsSemiLept", "TTJets_SemiLept.root", xs["TTJets_SemiLept"])
dgTTBarInclusive.add([dTTBar])
dgTTBarExclusive.add([dTTBarFullLept, dTTBarSemiLept])

WJets_lo_nnlo_scale_factor = 37509/30400.0
dgWJets = DatasetGroup("W+Jets", kGreen)
dgWJetsExclusive = DatasetGroup("W+Jets", kGreen)
dWJets = Dataset("WJets", "WJets", "WJets_inclusive", xs["WJets_inclusive"])
dW1Jets = Dataset("W+1Jets", "W1Jets_exclusive.root", xs["W1Jets_exclusive"])
dW2Jets = Dataset("W+2Jets", "W2Jets_exclusive.root", xs["W2Jets_exclusive"])
dW3Jets = Dataset("W+3Jets", "W3Jets_exclusive.root", xs["W3Jets_exclusive"])
dW4Jets = Dataset("W+4Jets", "W4Jets_exclusive.root", xs["W4Jets_exclusive"])
dgWJets.add([dWJets])
dgWJetsExclusive.add([dW1Jets, dW2Jets, dW3Jets, dW4Jets])


dgZJets = DatasetGroup("Z+Jets", kViolet)
dZJets = Dataset("DYJets", "DYJets.root", xs["DYJets"])
dgZJets.add(dZJets)

#dgDataMuons = DatasetGroup("Data", kBlack, False)
#dSingleMuAB = Dataset("dataMuAB", "SingleMuAB.root", MC=False)
#dSingleMuC = Dataset("dataMuC", "SingleMuC.root", MC=False)
#dSingleMuD = Dataset("dataMuD", "SingleMuD.root", MC=False)
#dgDataMuons.add([dSingleMuAB, dSingleMuC, dSingleMuD])

dgDataMuons = DatasetGroup("Data", kBlack, False)
dDataMuons1 = Dataset("DataMu1", "SingleMu1.root", MC=False)
dDataMuons2 = Dataset("DataMu2", "SingleMu2.root", MC=False)
dDataMuons3 = Dataset("DataMu3", "SingleMu3.root", MC=False)
dDataMuons4 = Dataset("DataMu4", "SingleMu_miss.root", MC=False)
dgDataMuons.add([dDataMuons1, dDataMuons2, dDataMuons3, dDataMuons4])

dgDataElectrons = DatasetGroup("Data", kBlack, False)
dDataElectrons1 = Dataset("DataEle1","SingleEle1.root", MC=False)
dDataElectrons2 = Dataset("DataEle2","SingleEle2.root", MC=False)
dDataElectrons3 = Dataset("DataEle3","SingleEle_miss.root", MC=False)
dgDataElectrons.add([dDataElectrons1, dDataElectrons2, dDataElectrons3])

#Define sets of dataset groups for muons
#For electrons, just do it the same way while defining dataset groups above as needed
MC_groups_noQCD_AllExclusive =[]
MC_groups_noQCD_AllExclusive.append(dgTWCh)
MC_groups_noQCD_AllExclusive.append(dgSCh)
MC_groups_noQCD_AllExclusive.append(dgTTBarExclusive)
MC_groups_noQCD_AllExclusive.append(dgWJetsExclusive)
MC_groups_noQCD_AllExclusive.append(dgZJets)
MC_groups_noQCD_AllExclusive.append(dgDibosons)

MC_groups_noQCD_InclusiveTCh = copy(MC_groups_noQCD_AllExclusive)
MC_groups_noQCD_AllExclusive.append(dgTChExclusive)
MC_groups_noQCD_InclusiveTCh.append(dgTChInclusive)

MC_groups_noQCD = copy(MC_groups_noQCD_InclusiveTCh)
mc_groups = copy(MC_groups_noQCD_InclusiveTCh)
mc_groups.append(dgQCDMu)
