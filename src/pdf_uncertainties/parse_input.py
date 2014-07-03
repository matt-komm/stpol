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
    #"T_t_ToLeptons", 
    "W1Jets_exclusive", 
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

#datasets = ["T_s"]

base_dir = "/hdfs/local/joosep/stpol/skims/step3/May1_metphi_on/iso/nominal/"

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
        
