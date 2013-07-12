#The global tags come from:
#https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideFrontierConditions?redirectedfrom=CMS.SWGuideFrontierConditions

global_tags = dict()
global_tags["data"] = dict()
global_tags["mc"] = dict()

gt_mc = "START53_V20::All"
gt_data = "FT_53_V21_AN4::All"

#step1
global_tags["mc"]["nominal_Summer12_DR53X"] = gt_mc
global_tags["mc"]["systematic_Summer12_DR53X"] = gt_mc
global_tags["mc"]["wjets_FSIM_Summer12"] = gt_mc

global_tags["data"]["22Jan_ReReco_Runs2012ABCD"] = gt_data

#step2
global_tags["mc"]["Apr19"] = gt_mc
global_tags["mc"]["Apr19_qcd"] = gt_mc
global_tags["data"]["May20"] = gt_data

