import json
from pprint import pprint
import os
import fnmatch

datasets = [
    #"DYJets", 
    #"T_t", 
    #"Tbar_tW", 
    #"W4Jets_exclusive", 
    #"ZZ", 
    #"TTJets_FullLept", 
    #"T_tW", 
    #"Tbar_t_ToLeptons", 
    #"WJets_inclusive", 
    #"TTJets_MassiveBinDECAY", 
    "T_t_ToLeptons", 
    #"W1Jets_exclusive", 
    #"WJets_sherpa", 
    #"TTJets_SemiLept", 
    #"Tbar_s", 
    #"W2Jets_exclusive", 
    #"WW", 
    #"T_s", 
    #"Tbar_t", 
    #"W3Jets_exclusive", 
    #"WZ"
]

groups = {
    "DYJets": "wzjets", 
    #"T_t", 
    "Tbar_tW": "ttjets", 
    "W4Jets_exclusive": "wzjets", 
    "ZZ": "wzjets", 
    "TTJets_FullLept": "ttjets", 
    "T_tW": "ttjets", 
    "Tbar_t_ToLeptons": "tchan", 
    #"WJets_inclusive", 
    #"TTJets_MassiveBinDECAY", 
    "T_t_ToLeptons": "tchan", 
    "W1Jets_exclusive": "wzjets", 
    #"WJets_sherpa", 
    "TTJets_SemiLept": "ttjets", 
    "Tbar_s": "ttjets", 
    "W2Jets_exclusive": "wzjets", 
    "WW": "wzjets", 
    "T_s": "ttjets", 
    #"Tbar_t", 
    "W3Jets_exclusive": "wzjets", 
    "WZ": "wzjets"
}

#datasets = ["T_s"]

#base_dir = "/hdfs/local/joosep/stpol/skims/step3/May1_metphi_on_2/iso/nominal/"
#base_dir = "/hdfs/local/joosep/stpol/skims/step3/Jul4_newsyst_newvars_metshift/iso/nominal/"
#base_dir = "/hdfs/local/joosep/stpol/skims/step3_v2/Jul4_newsyst_newvars_metshift/iso/nominal/"
base_dir = "/hdfs/local/joosep/stpol/skims/step3/csvt/Jul4_newsyst_newvars_metshift/iso/nominal/"
def get_data_files():
    data_files = dict()
    for ds in datasets:
        data_files[ds] = []
        for root, dir, files in os.walk(base_dir+ds):
            base_file = fnmatch.filter(files, "*.root")
            added_file = fnmatch.filter(files, "*.root.added")
            assert len(base_file) <= 1
            assert len(added_file) <= 1
            if len(base_file) == 1 and len(added_file) == 1:
                data_files[ds].append((root+'/'+base_file[0], root+'/'+added_file[0]))
    return data_files
        
