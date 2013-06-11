from Dataset import *
from DatasetGroup import *
from ROOT import *
from copy import copy, deepcopy

groups = []
MCgroups = []
MC_groups_noQCD = []

group_IsoUp = []
group_IsoDown = []

dgDibosons = DatasetGroup("Dibosons", kBlue)
dWW = Dataset("WW", "WW.root", 54.838)
dWZ = Dataset("WZ", "WZ.root", 33.2161)
dZZ = Dataset("ZZ", "ZZ.root", 8.25561)
dgDibosons.add([dWW,dWZ,dZZ])

dgQCDMu = DatasetGroup("QCD", kGray)
dQCDMu = Dataset("QCDMu", "QCDMu.root", 134680.)
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
dTCh = Dataset("t-channel", "T_t.root", 56.4)
dTChExc = Dataset("t-channel_toLeptons", "T_t_ToLeptons.root", 56.4*0.326)
dTbarCh = Dataset("t-channel_Tbar", "Tbar_t.root", 30.7)
dTbarChExc = Dataset("t-channel_toLeptons_Tbar", "Tbar_t_ToLeptons.root", 30.7*0.326)
dgTChInclusive.add([dTCh, dTbarCh])
dgTChExclusive.add([dTChExc, dTbarChExc])

dgTWCh = DatasetGroup("tW-channel", kOrange)
dTWCh = Dataset("tW-channel", "T_tW.root", 11.1)
dTbarWCh = Dataset("tW-channel_Tbar", "Tbar_tW.root", 11.1)
dgTWCh.add([dTWCh, dTbarWCh])

dgSCh = DatasetGroup("s-channel", kYellow )
dSCh = Dataset("s-channel", "T_s.root", 3.79)
dSbarCh = Dataset("s-channel_Tbar", "Tbar_s.root", 1.76)
dgSCh.add([dSCh,dSbarCh])

dgTTBarExclusive = DatasetGroup("t #bar{t}", kOrange-3)
dgTTBarInclusive = DatasetGroup("t #bar{t}", kOrange-3)
dTTBar = Dataset("TTJets", "TTJets_MassiveBinDECAY.root", 234.)
dTTBarFullLept = Dataset("TTJetsFullLept", "TTJets_FullLept.root", (0.326**2) * 234, 4246444 + 12119013)
dTTBarSemiLept = Dataset("TTJetsSemiLept", "TTJets_SemiLept.root", (0.676*0.326*2) * 234, 11229902 + 25424818)
dgTTBarInclusive.add([dTTBar])
dgTTBarExclusive.add([dTTBarFullLept, dTTBarSemiLept])

WJets_lo_nnlo_scale_factor = 37509/30400.0
dgWJets = DatasetGroup("W+Jets", kGreen+4)
dgWJetsExclusive = DatasetGroup("W+Jets", kGreen+4)
dWJets = Dataset("WJets", "WJets", "WJets_inclusive", 37509)
dW1Jets = Dataset("W+1Jets", "W1Jets_exclusive.root", 5400.0 * WJets_lo_nnlo_scale_factor)
dW2Jets = Dataset("W+2Jets", "W2Jets_exclusive.root", 1750.0 * WJets_lo_nnlo_scale_factor)
dW3Jets = Dataset("W+3Jets", "W3Jets_exclusive.root", 519.0 * WJets_lo_nnlo_scale_factor)
dW4Jets = Dataset("W+4Jets", "W4Jets_exclusive.root", 214.0 * WJets_lo_nnlo_scale_factor)
dgWJets.add([dWJets])
dgWJetsExclusive.add([dW1Jets, dW2Jets, dW3Jets, dW4Jets])


dgZJets = DatasetGroup("Z+Jets", kBlue-1)
dZJets = Dataset("DYJets", "DYJets.root", 3503.71)
dgZJets.add(dZJets)

dgDataMuons = DatasetGroup("Data", kBlack, False)
dSingleMu = Dataset("dataMu", "SingleMu.root", MC=False)
#dSingleMuC = Dataset("dataMuC", "SingleMuC.root", MC=False)
#dSingleMuD = Dataset("dataMuD", "SingleMuD.root", MC=False)
dgDataMuons.add([dSingleMu])

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
