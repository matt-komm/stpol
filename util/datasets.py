#!/usr/bin/python2.
"""
This file collects the various datasets used for the stpol analysis and creates
crab.cfg files from these datasets based on a template.
Author: Joosep Pata joosep.pata@cern.ch
"""

import sys
import os
import argparse
from SingleTopPolarization.Analysis.config_step2_cfg import Config

"""
Represents a lumi file.
"""
class Lumi:
    lumiBase8TeV = "https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions12/8TeV/"

    def __init__(self, name, url, base=lumiBase8TeV):
        self.name = name
        self.url = base + url
        self.fname = url[url.rindex("/")+1:]

lumis = {
    "rereco_golden": Lumi("rereco_golden",
    "/Cert_190456-208686_8TeV_22Jan2013ReReco_Collisions12_JSON.txt"),

    "Run2012A-13Jul2012": Lumi("Run2012A-13Jul2012",
    "/Cert_190456-196531_8TeV_13Jul2012ReReco_Collisions12_JSON_v2.txt")

    , "Run2012A-recover-06Aug2012": Lumi("Run2012A-recover-06Aug2012",
    "/Cert_190782-190949_8TeV_06Aug2012ReReco_Collisions12_JSON.txt")

    , "Run2012B-13Jul2012": Lumi("Run2012B-13Jul2012",
    "/Cert_190456-196531_8TeV_13Jul2012ReReco_Collisions12_JSON_v2.txt")

    , "Run2012C-24Aug": Lumi("Run2012C-24Aug",
    "/Cert_198022-198523_8TeV_24Aug2012ReReco_Collisions12_JSON.txt")

    , "Run2012C-PromptReco-v2": Lumi("Run2012C-PromptReco-v2",
    "/Cert_190456-203002_8TeV_PromptReco_Collisions12_JSON_v2.txt")

    , "Run2012C-EcalRecover_11Dec2012": Lumi("Run2012C-EcalRecover_11Dec2012",
    "/Cert_201191-201191_8TeV_11Dec2012ReReco-recover_Collisions12_JSON.txt")

    , "Run2012D-PromptReco-v1": Lumi("Run2012D-PromptReco-v1",
    "/Cert_190456-208686_8TeV_PromptReco_Collisions12_JSON.txt")

    , "total": Lumi("total", "/total.json")

    , "22jan_dcsonly": Lumi("22jan_dcsonly", "/22jan_dcsonly.json")
}


runRanges = dict()
runRanges["RunA"] = [190456, 193621]
runRanges["RunB"] = [193834, 196531]
runRanges["RunC"] = [198022, 203742]
runRanges["RunD"] = [203777, 208686]
runRanges["RunABCD"] = [190456, 208686]

"""
Represents a generic datasets.
"""
class DS(object):
    def __init__(self, name, ds, **kwargs):
        self.name = name
        self.ds = ds
        self.globalTag = Config.globalTagMC
        self.cmdline = kwargs.get("cmdline", "")

    def parseTemplate(self, template, tag):
        out = template
        workdir = "WD_{0}".format(self.name)
        out = out.replace("TAG", tag)
        out = out.replace("DATASET", self.ds)
        out = out.replace("WORKDIR", workdir)
        out = out.replace("CMDLINEARGS", self.cmdline)
        return out

    def __str__(self):
        return "| {0} | {1} | {2} | {3} |".format(self.name, self.ds, self.globalTag, self.cmdline)

"""
Represents a Real Data dataset
"""
class DS_Data(DS):
    def __init__(self, name, ds, lumi, globalTag, dataperiod, **kwargs):
        DS.__init__(self, name, ds, **kwargs)
        self.lumi = lumi
        self.globalTag = globalTag
        self.dataperiod = dataperiod
        self.run_range = runRanges[dataperiod]

    def parseTemplate(self, template, tag):
        out = template
        out = out.replace("LUMIFILE", lumis[self.lumi].fname)
        out = out.replace("DATAPERIOD", self.dataperiod)
        out = out.replace("GLOBALTAG", self.globalTag)
        out = out.replace("RUNRANGE", "%d-%d"%(self.run_range[0], self.run_range[1]))
        out = DS.parseTemplate(self, out, tag)
        return out

    def __str__(self):
        return "| {0} | {1} | {2} | {3} |".format(self.name, self.ds, self.globalTag, self.cmdline)

"""
Represents a step2 MC dataset
"""
class DS_S2MC(DS):
    def __init__(self, name, ds, subchannel=None, **kwargs):
        DS.__init__(self, name, ds, **kwargs)
        if subchannel is None:
            subchannel = name
        self.subchannel = subchannel
        subch_lower = subchannel.lower()
        if subch_lower in ["t_t", "tbar_t", "ttoleptons_t", "tbartoleptons_t"]:
            self.channel = "signal"
        else:
            self.channel = "background"

    def parseTemplate(self, template, tag, ch_name):
        out = super(DS_S2MC, self).parseTemplate(template, tag)
        out = out.replace("SUBCHAN", self.subchannel)
        out = out.replace("CHANNEL", self.channel)
        out = out.replace("NAME", ch_name)

        return out

#Top samples are in https://twiki.cern.ch/twiki/bin/view/CMS/TopSamplesSummer12#Prioritisation_for_Moriond2013

#Datasets and run ranges come from:
#https://twiki.cern.ch/twiki/bin/viewauth/CMS/PdmV2012Analysis#Analysis_based_on_CMSSW_5_3_X_re
#The global tags come from:
#https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideFrontierConditions?redirectedfrom=CMS.SWGuideFrontierConditions
global_tag_Data_ABCD = "FT_53_V21_AN4::All"

step1_data_rereco_2013Jan = [

#    DS_Data("SingleMu_RunA", "/SingleMu/Run2012A-22Jan2013-v1/AOD", "22jan_dcsonly", global_tag_Data_ABCD, "RunA"),
#    DS_Data("SingleMu_RunB", "/SingleMu/Run2012B-22Jan2013-v1/AOD", "22jan_dcsonly", global_tag_Data_ABCD, "RunB"),
#    DS_Data("SingleMu_RunC", "/SingleMu/Run2012C-22Jan2013-v1/AOD", "22jan_dcsonly", global_tag_Data_ABCD, "RunC"),
#    DS_Data("SingleMu_RunD", "/SingleMu/Run2012D-22Jan2013-v1/AOD", "22jan_dcsonly", global_tag_Data_ABCD, "RunD"),
#    DS_Data("SingleElectron_RunA", "/SingleElectron/Run2012A-22Jan2013-v1/AOD", "22jan_dcsonly", global_tag_Data_ABCD, "RunA"),
#    DS_Data("SingleElectron_RunB", "/SingleElectron/Run2012B-22Jan2013-v1/AOD", "22jan_dcsonly", global_tag_Data_ABCD, "RunB"),
#    DS_Data("SingleElectron_RunC", "/SingleElectron/Run2012C-22Jan2013-v1/AOD", "22jan_dcsonly", global_tag_Data_ABCD, "RunC"),
#    DS_Data("SingleElectron_RunD", "/SingleElectron/Run2012D-22Jan2013-v1/AOD", "22jan_dcsonly", global_tag_Data_ABCD, "RunD")

    DS_Data("SingleMu_RunABCD", "/SingleMu/Run2012D-22Jan2013-v1/AOD", "22jan_dcsonly", global_tag_Data_ABCD, "RunABCD"),
    DS_Data("SingleElectron_RunABCD", "/SingleElectron/Run2012D-22Jan2013-v1/AOD", "22jan_dcsonly", global_tag_Data_ABCD, "RunABCD")
]

step1_MC = [
      DS("T_t", "/T_t-channel_TuneZ2star_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM", cmdline="doSkimming=False")
    , DS("Tbar_t", "/Tbar_t-channel_TuneZ2star_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM", cmdline="doSkimming=False")

    , DS("T_s", "/T_s-channel_TuneZ2star_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")
    , DS("Tbar_s", "/Tbar_s-channel_TuneZ2star_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")

    , DS("T_tW", "/T_tW-channel-DR_TuneZ2star_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")
    , DS("Tbar_tW", "/Tbar_tW-channel-DR_TuneZ2star_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")

    , DS("TTbar", "/TTJets_MassiveBinDECAY_TuneZ2star_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM", cmdline="doSkimming=False")

    , DS("WJets1", "/WJetsToLNu_TuneZ2Star_8TeV-madgraph-tarball/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM") #smaller WJets sample
    , DS("WJets2", "/WJetsToLNu_TuneZ2Star_8TeV-madgraph-tarball/Summer12_DR53X-PU_S10_START53_V7A-v2/AODSIM") #larger WJets sample

    , DS("WW", "/WW_TuneZ2star_8TeV_pythia6_tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")
    , DS("WZ", "/WZ_TuneZ2star_8TeV_pythia6_tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")
    , DS("ZZ", "/ZZ_TuneZ2star_8TeV_pythia6_tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")

    , DS("GJets1", "/GJets_HT-200To400_8TeV-madgraph/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")
    , DS("GJets2", "/GJets_HT-400ToInf_8TeV-madgraph/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")

    , DS("QCD_Mu", "/QCD_Pt_20_MuEnrichedPt_15_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")

    , DS("QCD_BCtoE1", "/QCD_Pt_20_30_BCtoE_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")
    , DS("QCD_BCtoE2", "/QCD_Pt_30_80_BCtoE_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")
    , DS("QCD_BCtoE3", "/QCD_Pt_80_170_BCtoE_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")
    , DS("QCD_BCtoE4", "/QCD_Pt_170_250_BCtoE_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")
    , DS("QCD_BCtoE5", "/QCD_Pt_250_350_BCtoE_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")
    , DS("QCD_BCtoE6", "/QCD_Pt_350_BCtoE_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v2/AODSIM")

    , DS("QCD_EM1", "/QCD_Pt_20_30_EMEnriched_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")
    , DS("QCD_EM2", "/QCD_Pt_30_80_EMEnriched_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")
    , DS("QCD_EM3", "/QCD_Pt_80_170_EMEnriched_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")
    , DS("QCD_EM4", "/QCD_Pt_170_250_EMEnriched_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")
    , DS("QCD_EM5", "/QCD_Pt_250_350_EMEnriched_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")
    , DS("QCD_EM6", "/QCD_Pt_350_EMEnriched_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")

    , DS("DYJets", "/DYJetsToLL_M-50_TuneZ2Star_8TeV-madgraph-tarball/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")

    #From https://indico.cern.ch/getFile.py/access?contribId=1&resId=0&materialId=slides&confId=228739
#    , DS("TTbar_SemiLept1", "/TTJets_SemiLeptMGDecays_8TeV-madgraph/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM") #??
    , DS("TTbar_SemiLept2", "/TTJets_SemiLeptMGDecays_8TeV-madgraph/Summer12_DR53X-PU_S10_START53_V7A_ext-v1/AODSIM", cmdline="doSkimming=False") #25M
#    , DS("TTbar_FullLept1", "/TTJets_FullLeptMGDecays_8TeV-madgraph/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM") #4.2M
    , DS("TTbar_FullLept2", "/TTJets_FullLeptMGDecays_8TeV-madgraph/Summer12_DR53X-PU_S10_START53_V7A-v2/AODSIM", cmdline="doSkimming=False") #12M

    #https://cmsweb.cern.ch/das/request?view=list&limit=10&instance=cms_dbs_prod_global&input=dataset+dataset%3D%2FTToLeptons_t-channel_*AODSIM
    , DS("TToLeptons_t-channel", "/TToLeptons_t-channel_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM", cmdline="doSkimming=False")
    #https://cmsweb.cern.ch/das/request?view=list&limit=10&instance=cms_dbs_prod_global&input=dataset+dataset%3D%2FTbarToLeptons_t-channel*AODSIM
    , DS("TbarToLeptons_t-channel", "/TBarToLeptons_t-channel_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM", cmdline="doSkimming=False")

    #https://cmsweb.cern.ch/das/request?view=list&limit=10&instance=cms_dbs_prod_global&input=dataset+dataset%3D%2FW*JetsToLNu_TuneZ2Star_8TeV-madgraph%2FSummer12_DR53X-PU_S10_START53*AODSIM
    , DS("WJets_excl1", "/W1JetsToLNu_TuneZ2Star_8TeV-madgraph/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")
    , DS("WJets_excl2", "/W2JetsToLNu_TuneZ2Star_8TeV-madgraph/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")
    , DS("WJets_excl3", "/W3JetsToLNu_TuneZ2Star_8TeV-madgraph/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")
    , DS("WJets_excl4", "/W4JetsToLNu_TuneZ2Star_8TeV-madgraph/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")
]

step1_MC_systematic = [
    DS("Tbar_t_scaleup", "/TBarToLeptons_t-channel_scaleup_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM", cmdline="doSkimming=False"),
    DS("T_t_scaleup", "/TToLeptons_t-channel_scaleup_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM", cmdline="doSkimming=False"),
    DS("T_t_scaledown", "/TToLeptons_t-channel_scaledown_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM", cmdline="doSkimming=False"),
    DS("Tbar_t_scaledown", "/TBarToLeptons_t-channel_scaledown_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM", cmdline="doSkimming=False"),
    DS("Tbar_t_mass166_5", "/TBarToLeptons_t-channel_mass166_5_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM", cmdline="doSkimming=False"),
    DS("T_t_mass166_5", "/TToLeptons_t-channel_mass166_5_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM", cmdline="doSkimming=False"),
    DS("Tbar_t_mass178_5", "/TBarToLeptons_t-channel_mass178_5_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM", cmdline="doSkimming=False"),
    DS("T_t_mass178_5", "/TToLeptons_t-channel_mass178_5_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM", cmdline="doSkimming=False"),
    DS("WJets_scaleup", "/WJetsToLNu_scaleup_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v2/AODSIM"),
    DS("WJets_scaledown", "/WJetsToLNu_scaledown_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"),
    DS("WJets_matchingup", "/WJetsToLNu_matchingup_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"),
    DS("WJets_matchingdown", "/WJetsToLNu_matchingdown_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"),
    #DS("TTJets_mass161_5", "/TTJets_mass161_5_TuneZ2star_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"),
    DS("TTJets_mass166_5", "/TTJets_mass166_5_TuneZ2star_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM", cmdline="doSkimming=False"),
    #DS("TTJets_mass184_5", "/TTJets_mass184_5_TuneZ2star_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"),
    DS("TTJets_mass178_5", "/TTJets_mass178_5_TuneZ2star_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM", cmdline="doSkimming=False"),
    DS("TTJets_matchingup", "/TTJets_matchingup_TuneZ2star_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM", cmdline="doSkimming=False"),
    DS("TTJets_matchingdown", "/TTJets_matchingdown_TuneZ2star_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM", cmdline="doSkimming=False"),
    DS("TTJets_scaleup", "/TTJets_scaleup_TuneZ2star_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM", cmdline="doSkimming=False"),
    DS("TTJets_scaledown", "/TTJets_scaledown_TuneZ2star_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM", cmdline="doSkimming=False"),

    DS("TToBENu_anomWtb-unphys", "/TToBENu_anomWtb-unphys_t-channel_TuneZ2star_8TeV-comphep/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM", cmdline="doSkimming=False"),
    DS("TToBMuNu_anomWtb-unphys", "/TToBMuNu_anomWtb-unphys_t-channel_TuneZ2star_8TeV-comphep/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM", cmdline="doSkimming=False"),
    DS("TToBTauNu_anomWtb-unphys", "/TToBTauNu_anomWtb-unphys_t-channel_TuneZ2star_8TeV-comphep/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM", cmdline="doSkimming=False"),

    DS("TToBENu_anomWtb-0100", "/TToBENu_anomWtb-0100_t-channel_TuneZ2star_8TeV-comphep/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM", cmdline="doSkimming=False"),
    DS("TToBMuNu_anomWtb-0100", "/TToBMuNu_anomWtb-0100_t-channel_TuneZ2star_8TeV-comphep/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM", cmdline="doSkimming=False"),
    DS("TToBTauNu_anomWtb-0100", "/TToBTauNu_anomWtb-0100_t-channel_TuneZ2star_8TeV-comphep/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM", cmdline="doSkimming=False"),
]

step1_MC_systematic_out = [
    DS_S2MC("Tbar_t_mass166_5", "/TBarToLeptons_t-channel_mass166_5_8TeV-powheg-tauola/jpata-stpol_step1_05_10-dbc13e99c2b8251c2992382f53978821/USER", "Tbar_t")
    , DS_S2MC("Tbar_t_mass178_5", "/TBarToLeptons_t-channel_mass178_5_8TeV-powheg-tauola/jpata-stpol_step1_05_10-dbc13e99c2b8251c2992382f53978821/USER", "Tbar_t")
    , DS_S2MC("Tbar_t_scaledown", "/TBarToLeptons_t-channel_scaledown_8TeV-powheg-tauola/jpata-stpol_step1_05_10-dbc13e99c2b8251c2992382f53978821/USER", "Tbar_t")
    , DS_S2MC("Tbar_t_scaleup", "/TBarToLeptons_t-channel_scaleup_8TeV-powheg-tauola/jpata-stpol_step1_05_10-dbc13e99c2b8251c2992382f53978821/USER", "Tbar_t")
    , DS_S2MC("TTJets_mass166_5", "/TTJets_mass166_5_TuneZ2star_8TeV-madgraph-tauola/jpata-stpol_step1_05_20_a2437d6e0ca7eba657ba43c9c2371fff8f88e5ba-d6f3c092e0af235d8b18254ddb07959c/USER", "TTbar")
    , DS_S2MC("TTJets_mass178_5", "/TTJets_mass178_5_TuneZ2star_8TeV-madgraph-tauola/jpata-stpol_step1_05_10-dbc13e99c2b8251c2992382f53978821/USER", "TTbar")
    , DS_S2MC("TTJets_matchingdown", "/TTJets_matchingdown_TuneZ2star_8TeV-madgraph-tauola/jpata-stpol_step1_05_10-dbc13e99c2b8251c2992382f53978821/USER", "TTbar")
    , DS_S2MC("TTJets_matchingup", "/TTJets_matchingup_TuneZ2star_8TeV-madgraph-tauola/jpata-stpol_step1_05_20_a2437d6e0ca7eba657ba43c9c2371fff8f88e5ba-d6f3c092e0af235d8b18254ddb07959c/USER", "TTbar")
    , DS_S2MC("TTJets_scaledown", "/TTJets_scaledown_TuneZ2star_8TeV-madgraph-tauola/jpata-stpol_step1_05_10-dbc13e99c2b8251c2992382f53978821/USER", "TTbar")
    , DS_S2MC("TTJets_scaleup", "/TTJets_scaleup_TuneZ2star_8TeV-madgraph-tauola/jpata-stpol_step1_05_10-dbc13e99c2b8251c2992382f53978821/USER", "TTbar")
    , DS_S2MC("TToBENu_anomWtb-0100_t-channel", "/TToBENu_anomWtb-0100_t-channel_TuneZ2star_8TeV-comphep/jpata-stpol_step1_05_10-dbc13e99c2b8251c2992382f53978821/USER", "T_t")
    , DS_S2MC("TToBENu_anomWtb-unphys_t-channel", "/TToBENu_anomWtb-unphys_t-channel_TuneZ2star_8TeV-comphep/jpata-stpol_step1_05_10-dbc13e99c2b8251c2992382f53978821/USER", "T_t")
    , DS_S2MC("TToBMuNu_anomWtb-0100_t-channel", "/TToBMuNu_anomWtb-0100_t-channel_TuneZ2star_8TeV-comphep/jpata-stpol_step1_05_10-dbc13e99c2b8251c2992382f53978821/USER", "T_t")
    , DS_S2MC("TToBMuNu_anomWtb-unphys_t-channel", "/TToBMuNu_anomWtb-unphys_t-channel_TuneZ2star_8TeV-comphep/jpata-stpol_step1_05_10-dbc13e99c2b8251c2992382f53978821/USER", "T_t")
    , DS_S2MC("TToBTauNu_anomWtb-0100_t-channel", "/TToBTauNu_anomWtb-0100_t-channel_TuneZ2star_8TeV-comphep/jpata-stpol_step1_05_10-dbc13e99c2b8251c2992382f53978821/USER", "T_t")
    , DS_S2MC("TToLeptons_t-channel_mass166_5", "/TToLeptons_t-channel_mass166_5_8TeV-powheg-tauola/jpata-stpol_step1_05_10-dbc13e99c2b8251c2992382f53978821/USER", "T_t")
    , DS_S2MC("TToLeptons_t-channel_mass178_5", "/TToLeptons_t-channel_mass178_5_8TeV-powheg-tauola/jpata-stpol_step1_05_20_a2437d6e0ca7eba657ba43c9c2371fff8f88e5ba-d6f3c092e0af235d8b18254ddb07959c/USER", "T_t")
    , DS_S2MC("TToLeptons_t-channel_scaledown", "/TToLeptons_t-channel_scaledown_8TeV-powheg-tauola/jpata-stpol_step1_05_10-dbc13e99c2b8251c2992382f53978821/USER", "T_t")
    , DS_S2MC("TToLeptons_t-channel_scaleup", "/TToLeptons_t-channel_scaleup_8TeV-powheg-tauola/jpata-stpol_step1_05_10-dbc13e99c2b8251c2992382f53978821/USER", "T_t")
    , DS_S2MC("WJetsToLNu_matchingdown", "/WJetsToLNu_matchingdown_8TeV-madgraph-tauola/jpata-stpol_step1_05_20_a2437d6e0ca7eba657ba43c9c2371fff8f88e5ba-d6f3c092e0af235d8b18254ddb07959c/USER", "WJets")
    , DS_S2MC("WJetsToLNu_matchingup", "/WJetsToLNu_matchingup_8TeV-madgraph-tauola/jpata-stpol_step1_05_20_a2437d6e0ca7eba657ba43c9c2371fff8f88e5ba-d6f3c092e0af235d8b18254ddb07959c/USER", "WJets")
    , DS_S2MC("WJetsToLNu_scaledown", "/WJetsToLNu_scaledown_8TeV-madgraph-tauola/jpata-stpol_step1_05_10-dbc13e99c2b8251c2992382f53978821/USER", "WJets")
    , DS_S2MC("WJetsToLNu_scaleup", "/WJetsToLNu_scaleup_8TeV-madgraph-tauola/jpata-stpol_step1_05_10-dbc13e99c2b8251c2992382f53978821/USER", "WJets")
]


step2_sherpa_WJets = [
      DS_S2MC("WJets_sherpa_nominal", "/WJets_0p1_1p2_2p10_3p20_4p20_5p20_CT10_8TeV-sherpa/joosep-stpol_step1_misc_05_31-d6f3c092e0af235d8b18254ddb07959c/USER", "WJets", cmdline="sherpa=True")
    , DS_S2MC("WJets_sherpa_EnUp", "/WJets_0p1_1p2_2p10_3p20_4p20_5p20_CT10_8TeV-sherpa/joosep-stpol_step1_misc_05_31-d6f3c092e0af235d8b18254ddb07959c/USER", "WJets", cmdline="sherpa=True systematic=EnUp")
    , DS_S2MC("WJets_sherpa_EnDown", "/WJets_0p1_1p2_2p10_3p20_4p20_5p20_CT10_8TeV-sherpa/joosep-stpol_step1_misc_05_31-d6f3c092e0af235d8b18254ddb07959c/USER", "WJets", cmdline="sherpa=True systematic=EnDown")
    , DS_S2MC("WJets_sherpa_ResUp", "/WJets_0p1_1p2_2p10_3p20_4p20_5p20_CT10_8TeV-sherpa/joosep-stpol_step1_misc_05_31-d6f3c092e0af235d8b18254ddb07959c/USER", "WJets", cmdline="sherpa=True systematic=ResUp")
    , DS_S2MC("WJets_sherpa_ResDown", "/WJets_0p1_1p2_2p10_3p20_4p20_5p20_CT10_8TeV-sherpa/joosep-stpol_step1_misc_05_31-d6f3c092e0af235d8b18254ddb07959c/USER", "WJets", cmdline="sherpa=True systematic=ResDown")
    , DS_S2MC("WJets_sherpa_UnclusteredEnUp", "/WJets_0p1_1p2_2p10_3p20_4p20_5p20_CT10_8TeV-sherpa/joosep-stpol_step1_misc_05_31-d6f3c092e0af235d8b18254ddb07959c/USER", "WJets", cmdline="sherpa=True systematic=UnclusteredEnUp")
    , DS_S2MC("WJets_sherpa_UnclusteredEnDown", "/WJets_0p1_1p2_2p10_3p20_4p20_5p20_CT10_8TeV-sherpa/joosep-stpol_step1_misc_05_31-d6f3c092e0af235d8b18254ddb07959c/USER", "WJets", cmdline="sherpa=True systematic=UnclusteredEnDown")
]

step1_FSIM_Valid = [
    DS("TTJets_FSIM_Valid_FastSim", "/TTJets_MassiveBinDECAY_TuneZ2star_8TeV-madgraph-tauola/Summer12-START53_V7C_FSIM-v1/AODSIM"),
    DS("TTJets_FSIM_Valid_FullSim", "/TTJets_MassiveBinDECAY_TuneZ2star_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7C-v1/AODSIM"),
]


step1_FSIM_WJets = [
    DS("W1Jets_FSIM", "/W1JetsToLNu_TuneZ2Star_8TeV-madgraph/Summer12-START53_V7C_FSIM-v1/AODSIM"),
    DS("W1Jets_FSIM_matchingdown", "/W1JetsToLNu_matchingdown_TuneZ2Star_8TeV-madgraph/Summer12-START53_V7C_FSIM-v1/AODSIM"),
    DS("W1Jets_FSIM_matchingup", "/W1JetsToLNu_matchingup_TuneZ2Star_8TeV-madgraph/Summer12-START53_V7C_FSIM-v1/AODSIM"),
    DS("W1Jets_FSIM_scaledown", "/W1JetsToLNu_scaledown_TuneZ2Star_8TeV-madgraph/Summer12-START53_V7C_FSIM-v1/AODSIM"),
    DS("W1Jets_FSIM_scaleup", "/W1JetsToLNu_scaleup_TuneZ2Star_8TeV-madgraph/Summer12-START53_V7C_FSIM-v1/AODSIM"),
    DS("W2Jets_FSIM", "/W2JetsToLNu_TuneZ2Star_8TeV-madgraph/Summer12-START53_V7C_FSIM-v1/AODSIM"),
    DS("W3Jets_FSIM", "/W3JetsToLNu_TuneZ2Star_8TeV-madgraph/Summer12-START53_V7C_FSIM-v1/AODSIM"),
    DS("W4Jets_FSIM", "/W4JetsToLNu_TuneZ2Star_8TeV-madgraph/Summer12-START53_V7C_FSIM-v1/AODSIM")
]

#signal samples are May27 - switched off skimming
step1B_out_MC_signal_new = [
    DS_S2MC("T_t_ToLeptons", "/TToLeptons_t-channel_8TeV-powheg-tauola/joosep-stpol_step1_May27_noskim_sig-571e6857147b6f6cfbb44475d2524835/USER", "T_t"),
    DS_S2MC("T_t", "/T_t-channel_TuneZ2star_8TeV-powheg-tauola/joosep-stpol_step1_May27_noskim_sig-571e6857147b6f6cfbb44475d2524835/USER", "T_t"),
    DS_S2MC("Tbar_t_ToLeptons", "/TBarToLeptons_t-channel_8TeV-powheg-tauola/joosep-stpol_step1_May27_noskim_sig-571e6857147b6f6cfbb44475d2524835/USER", "Tbar_t"),
    DS_S2MC("Tbar_t", "/Tbar_t-channel_TuneZ2star_8TeV-powheg-tauola/joosep-stpol_step1_May27_noskim_sig-571e6857147b6f6cfbb44475d2524835/USER", "Tbar_t")
]

step1B_out_MC_noQCD_new = [
    DS_S2MC("T_s", "/T_s-channel_TuneZ2star_8TeV-powheg-tauola/joosep-stpol_step1_04_19-c9249c44a215ffeb8c9ba40f59092334/USER", "T_s"),
    DS_S2MC("T_tW", "/T_tW-channel-DR_TuneZ2star_8TeV-powheg-tauola/joosep-stpol_step1_04_19-c9249c44a215ffeb8c9ba40f59092334/USER", "T_tW"),

    DS_S2MC("Tbar_s", "/Tbar_s-channel_TuneZ2star_8TeV-powheg-tauola/joosep-stpol_step1_04_19-c9249c44a215ffeb8c9ba40f59092334/USER", "Tbar_s"),
    DS_S2MC("Tbar_tW", "/Tbar_tW-channel-DR_TuneZ2star_8TeV-powheg-tauola/joosep-stpol_step1_04_19-c9249c44a215ffeb8c9ba40f59092334/USER", "Tbar_tW"),

    DS_S2MC("WW", "/WW_TuneZ2star_8TeV_pythia6_tauola/joosep-stpol_step1_04_19-c9249c44a215ffeb8c9ba40f59092334/USER", "WW"),
    DS_S2MC("WZ", "/WZ_TuneZ2star_8TeV_pythia6_tauola/joosep-stpol_step1_04_19-c9249c44a215ffeb8c9ba40f59092334/USER", "WZ"),
    DS_S2MC("ZZ", "/ZZ_TuneZ2star_8TeV_pythia6_tauola/joosep-stpol_step1_04_19-c9249c44a215ffeb8c9ba40f59092334/USER", "ZZ"),

    DS_S2MC("TTJets_MassiveBinDECAY", "/TTJets_MassiveBinDECAY_TuneZ2star_8TeV-madgraph-tauola/joosep-stpol_step1_04_19-c9249c44a215ffeb8c9ba40f59092334/USER", "TTbar"),
    DS_S2MC("TTJets_FullLept", "/TTJets_FullLeptMGDecays_8TeV-madgraph/joosep-stpol_step1_05_20_a2437d6e0ca7eba657ba43c9c2371fff8f88e5ba-d6f3c092e0af235d8b18254ddb07959c/USER", "TTbar"),
    DS_S2MC("TTJets_SemiLept", "/TTJets_SemiLeptMGDecays_8TeV-madgraph/joosep-stpol_step1_05_20_a2437d6e0ca7eba657ba43c9c2371fff8f88e5ba-d6f3c092e0af235d8b18254ddb07959c/USER", "TTbar"),

    DS_S2MC("GJets1", "/GJets_HT-200To400_8TeV-madgraph/joosep-stpol_step1_04_19-c9249c44a215ffeb8c9ba40f59092334/USER", "GJets_HT-200To400"),
    DS_S2MC("GJets2", "/GJets_HT-400ToInf_8TeV-madgraph/joosep-stpol_step1_04_19-c9249c44a215ffeb8c9ba40f59092334/USER", "GJets_HT-400ToInf"),

    DS_S2MC("W1Jets_exclusive", "/W1JetsToLNu_TuneZ2Star_8TeV-madgraph/joosep-stpol_step1_04_19-c9249c44a215ffeb8c9ba40f59092334/USER", "WJets"),
    DS_S2MC("W2Jets_exclusive", "/W2JetsToLNu_TuneZ2Star_8TeV-madgraph/joosep-stpol_step1_04_19-c9249c44a215ffeb8c9ba40f59092334/USER", "WJets"),
    DS_S2MC("W3Jets_exclusive", "/W3JetsToLNu_TuneZ2Star_8TeV-madgraph/joosep-stpol_step1_04_19-c9249c44a215ffeb8c9ba40f59092334/USER", "WJets"),
    DS_S2MC("W4Jets_exclusive", "/W4JetsToLNu_TuneZ2Star_8TeV-madgraph/joosep-stpol_step1_04_19-c9249c44a215ffeb8c9ba40f59092334/USER", "WJets"),

    DS_S2MC("WJets_inclusive", "/WJetsToLNu_TuneZ2Star_8TeV-madgraph-tarball/joosep-stpol_step1_04_19-c9249c44a215ffeb8c9ba40f59092334/USER", "WJets"),
    DS_S2MC("DYJets", "/DYJetsToLL_M-50_TuneZ2Star_8TeV-madgraph-tarball/joosep-stpol_step1_04_19-c9249c44a215ffeb8c9ba40f59092334/USER", "DYJets")
]

step1B_out_MC_QCD_new = [
    DS_S2MC("QCDMu", "/QCD_Pt_20_MuEnrichedPt_15_TuneZ2star_8TeV_pythia6/joosep-stpol_step1_04_19-c9249c44a215ffeb8c9ba40f59092334/USER", "QCDMu"),

    DS_S2MC("QCD_Pt_20_30_BCtoE", "/QCD_Pt_20_30_BCtoE_TuneZ2star_8TeV_pythia6/joosep-stpol_step1_04_19-c9249c44a215ffeb8c9ba40f59092334/USER", "QCD_BCtoE"),
    DS_S2MC("QCD_Pt_30_80_BCtoE", "/QCD_Pt_30_80_BCtoE_TuneZ2star_8TeV_pythia6/joosep-stpol_step1_04_19-c9249c44a215ffeb8c9ba40f59092334/USER", "QCD_BCtoE"),
    DS_S2MC("QCD_Pt_80_170_BCtoE", "/QCD_Pt_80_170_BCtoE_TuneZ2star_8TeV_pythia6/joosep-stpol_step1_04_19-c9249c44a215ffeb8c9ba40f59092334/USER", "QCD_BCtoE"),
    DS_S2MC("QCD_Pt_170_250_BCtoE", "/QCD_Pt_170_250_BCtoE_TuneZ2star_8TeV_pythia6/joosep-stpol_step1_04_19-c9249c44a215ffeb8c9ba40f59092334/USER", "QCD_BCtoE"),
    DS_S2MC("QCD_Pt_250_350_BCtoE", "/QCD_Pt_250_350_BCtoE_TuneZ2star_8TeV_pythia6/joosep-stpol_step1_04_19-c9249c44a215ffeb8c9ba40f59092334/USER", "QCD_BCtoE"),
    DS_S2MC("QCD_Pt_350_BCtoE", "/QCD_Pt_350_BCtoE_TuneZ2star_8TeV_pythia6/joosep-stpol_step1_04_19-c9249c44a215ffeb8c9ba40f59092334/USER", "QCD_BCtoE"),

    DS_S2MC("QCD_Pt_20_30_EMEnriched", "/QCD_Pt_20_30_EMEnriched_TuneZ2star_8TeV_pythia6/joosep-stpol_step1_04_19-c9249c44a215ffeb8c9ba40f59092334/USER", "QCD_EMEnriched"),
    DS_S2MC("QCD_Pt_30_80_EMEnriched", "/QCD_Pt_30_80_EMEnriched_TuneZ2star_8TeV_pythia6/joosep-stpol_step1_04_19-c9249c44a215ffeb8c9ba40f59092334/USER", "QCD_EMEnriched"),
    DS_S2MC("QCD_Pt_80_170_EMEnriched", "/QCD_Pt_80_170_EMEnriched_TuneZ2star_8TeV_pythia6/joosep-stpol_step1_04_19-c9249c44a215ffeb8c9ba40f59092334/USER", "QCD_EMEnriched"),
    DS_S2MC("QCD_Pt_170_250_EMEnriched", "/QCD_Pt_170_250_EMEnriched_TuneZ2star_8TeV_pythia6/joosep-stpol_step1_04_19-c9249c44a215ffeb8c9ba40f59092334/USER", "QCD_EMEnriched"),
    DS_S2MC("QCD_Pt_250_350_EMEnriched", "/QCD_Pt_250_350_EMEnriched_TuneZ2star_8TeV_pythia6/joosep-stpol_step1_04_19-c9249c44a215ffeb8c9ba40f59092334/USER", "QCD_EMEnriched"),
    DS_S2MC("QCD_Pt_350_EMEnriched", "/QCD_Pt_350_EMEnriched_TuneZ2star_8TeV_pythia6/joosep-stpol_step1_04_19-c9249c44a215ffeb8c9ba40f59092334/USER", "QCD_EMEnriched"),
]

step1B_out_MC_noQCD_new.extend(step1B_out_MC_signal_new)
step1B_out_MC_new = step1B_out_MC_noQCD_new[:]
step1B_out_MC_new.extend(step1B_out_MC_QCD_new)

step1_out_newData = [
    DS_Data("SingleEle", "/SingleElectron/jpata-stpol_step1_05_20_a2437d6e0ca7eba657ba43c9c2371fff8f88e5ba-de95748cd8fdda59f3ad9b020ab1169c/USER", "rereco_golden", "FT_53_V6_AN3::All", "RunABCD")
    , DS_Data("SingleMu", "/SingleMu/jpata-stpol_step1_05_20_a2437d6e0ca7eba657ba43c9c2371fff8f88e5ba-de95748cd8fdda59f3ad9b020ab1169c/USER", "rereco_golden", "FT_53_V6_AN3::All", "RunABCD")
]

step2_FastSimValid = [
    DS_S2MC("TTJets_FSIM_Valid_FullSim", "/TTJets_MassiveBinDECAY_TuneZ2star_8TeV-madgraph-tauola/jpata-stpol_Feb8_FastSimValidation-243fe90abe1b1cf7bc2119dc7c0b2e28/USER#c66d2181-df08-407f-ae2e-0185b67e17cf"),

    DS_S2MC("TTJets_FSIM_Valid_FastSim", "/TTJets_MassiveBinDECAY_TuneZ2star_8TeV-madgraph-tauola/jpata-stpol_Feb8_FastSimValidation_v2_FSIM-243fe90abe1b1cf7bc2119dc7c0b2e28/USER")
]

"""
Possible datasets to process
"""
possible_ds = {
    "S1_D": step1_data_rereco_2013Jan, #direct data
    "S1_MC": step1_MC, #direct AODSIM
    "S1_MC_syst": step1_MC_systematic, #direct AODSIM
    "S1_FSIM_WJ": step1_FSIM_WJets,

    #step2
    "S2_D": step1_out_newData,
    "S2_MC": step1B_out_MC_new,
    "S2_SIG": step1B_out_MC_signal_new,
    "S2_MC_noQCD": step1B_out_MC_noQCD_new,
    "S2_MC_QCD": step1B_out_MC_QCD_new,
    "S2_MC_syst": step1_MC_systematic_out,

    "S2_MC_WJets_sherpa": step2_sherpa_WJets
}

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Creates crab.cfg files based on \
                                                  a template file.')
    parser.add_argument("-t", "--tag", type=str, default="notag",
                        help="A unique tag for publishing")
    parser.add_argument("-T", "--template", type=str, default="", required=True,
                        help="template file to use")
    parser.add_argument("-o", "--ofdir", type=str, default="", required=True,
                        help="output directory for files")
    parser.add_argument("-d", "--data", type=str, default="", required=True,
                        help="name of the list of datasets to parse", choices=possible_ds.keys())
    parser.add_argument("-s", "--systematic", type=str, default="", required=False,
                        help="name of systematic uncertainty investigated")
    args = parser.parse_args()
    print args
    tag = args.tag
    ofdir = args.ofdir
    systematic = args.systematic

    def read_template(fn):
        f = open(fn)
        s = f.read()
        f.close()
        return s

    template = read_template(args.template)
    dslist = possible_ds[args.data]

    os.makedirs(ofdir)
    for ds in dslist:
        ofn = "{2}/crab_{0}_{1}.cfg".format(ds.name, tag, ofdir)
        of = open(ofn, "w")
        if isinstance(ds, DS_S2MC):
            if len(systematic)>0 and systematic in ["SYST", "Presel", "EnDown", "EnUp", "ResDown", "ResUp", "UnclusteredEnDown", "UnclusteredEnUp"]:
                ds.cmdline += "%s" % systematic
            elif len(systematic)>0:
                ds.cmdline += "systematic=%s" % systematic
            cfg = ds.parseTemplate(template, tag, ds.name)
        else:
            cfg = ds.parseTemplate(template, tag)
        of.write(cfg)
        of.close()
        print "{0} done".format(ofn)
