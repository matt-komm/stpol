#The global tags come from:
#https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideFrontierConditions?redirectedfrom=CMS.SWGuideFrontierConditions

global_tags = dict()
global_tags["data"] = dict()
global_tags["mc"] = dict()

#gt_mc = "START53_V20::All"
#gt_data = "FT_53_V21_AN4::All"

#https://hypernews.cern.ch/HyperNews/CMS/get/JetMET/1461.html
gt_data = "FT_53_V21_AN5::All"
gt_mc = "START53_V27::All"

#step1
global_tags["mc"]["nominal_Summer12_DR53X"] = gt_mc
global_tags["mc"]["systematic_Summer12_DR53X"] = gt_mc
global_tags["mc"]["wjets_FSIM_Summer12"] = gt_mc

global_tags["data"]["22Jan_ReReco_Runs2012ABCD"] = gt_data

#step2
global_tags["mc"]["Apr19"] = gt_mc
global_tags["mc"]["Apr19_qcd"] = gt_mc
global_tags["data"]["May20"] = gt_data

global_tags["mc"]["Jul15"] = gt_mc
global_tags["mc"]["Jul15_qcd"] = gt_mc
global_tags["mc"]["Sep4"] = gt_mc

global_tags["data"]["Jul15"] = gt_data
global_tags["data"]["Aug1"] = gt_data

