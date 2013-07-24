from Dataset import *
from DatasetGroup import *
from ROOT import *
from copy import copy
import os

def open_all_data_files(data_group, mc_groups, QCD_group, paths):
    files = {}
    #all_groups = copy(mc_groups)
    #all_groups.append(data_group)
    #TODO: QCD MC if needed    
    #if QCD_group is not None:
    #    all_groups.append(QCD_group)

    for ds in data_group.getDatasets():
        for iso in paths["data"]:
            f = TFile(paths["data"][iso]+ds.getFileName())
            files[ds.getName()+"_"+iso+"Nominal"]=f
            count_hist = f.Get("trees").Get("count_hist")
            if not count_hist:
                raise TObjectOpenException("Failed to open count histogram")
            ds.setOriginalEventCount(count_hist.GetBinContent(1), iso, "Nominal")
            #print paths[iso][syst]+ds.getFileName(), count_hist.GetBinContent(1)
            ds.addFile("Nominal", iso, files[ds.getName()+"_"+iso+"Nominal"])
            #print "after adding ",ds._files
    for group in mc_groups:
        for ds in group.getDatasets():
            for iso in paths["mc"]:
                for syst in paths["mc"][iso]:
                   if (ds.getName() != "QCDMu"):
                       f = TFile(paths["mc"][iso][syst]+ds.getFileName())
                       files[ds.getName()+"_"+iso+syst]=f
                       count_hist = f.Get("trees").Get("count_hist")
                       if not count_hist:
                          raise TObjectOpenException("Failed to open count histogram")
                       ds.setOriginalEventCount(count_hist.GetBinContent(1), iso, syst)
                       #print paths[iso][syst]+ds.getFileName(), count_hist.GetBinContent(1)
                       ds.addFile(syst, iso, files[ds.getName()+"_"+iso+syst])
                       #print "after adding ",ds._files
    return files

def generate_paths(systematics, base_path, lepton="mu"):
    isos = ["iso", "antiiso"]
    syst_type = ["Up", "Down"]
    paths = {}
    paths["data"] = {}
    paths["mc"] = {}
    
    date = os.listdir("/home/andres/single_top/stpol/step3_latest" + "/" + lepton + "/data/iso/")[0]
    for iso in isos:
        paths["mc"][iso] = {}
        paths["data"][iso] = base_path + "/" + lepton + "/data/" + iso + "/" + date + "/"
        for syst in systematics:
            if syst == "Nominal":
                path = base_path + "/" + lepton + "/mc/" + iso + "/" + "nominal" + "/" + date + "/"
                paths["mc"][iso][syst] = path
            else:            
                for st in syst_type:
                    path = base_path + "/" + lepton + "/mc/" + iso + "/" + syst + st + "/" + date + "/"
                    paths["mc"][iso][syst+st] = path
    return paths

def clear_histos(data_group, mc_groups):
   all_groups = mc_groups
   all_groups.append(data_group)
   for group in all_groups:
      group.cleanHistograms()
   
"""def open_all_data_files_old(data_group, mc_groups, isos, systematics, path):
   files = {}
   all_groups = copy(mc_groups)
   all_groups.append(data_group)
   for group in all_groups:
      for ds in group.getDatasets():
         for iso in isos:
            for syst in systematics:
               f = TFile(path+iso+"/nominal/"+ds.getFileName())
               #print path+iso+"/"+ds.getFileName()+syst
               files[ds.getName()+"_"+iso+syst]=f
               #print ds._files
               #print "add ", ds.getName(), syst, iso
               count_hist = f.Get("trees").Get("count_hist")
               if not count_hist:
                  raise TObjectOpenException("Failed to open count histogram")
               ds.setOriginalEventCount(count_hist.GetBinContent(1))
               ds.addFile(syst, iso, files[ds.getName()+"_"+iso+syst])
               #print "after adding ",ds._files
   return files
"""
