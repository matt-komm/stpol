import sys
import os
from copy import copy
from utils import sizes
#Monkey-patch the system path to import the stpol header
#sys.path.append(os.path.join(os.environ["STPOL_DIR"], "src/headers"))
#from stpol import stpol, list_methods

import ROOT
from DataFormats.FWLite import Events, Handle, Lumis
#from src.qcd_mva.utils import *

import pickle





#print "args", sys.argv[0], sys.argv[1]
#system.exit(1)
#dataset = sys.argv[1]
#counter = sys.argv[2]
#iso = sys.argv[3]
#file_list = sys.argv[4:]


def get_file_list(file_list_file):
    lines = [line.strip() for line in open(file_list_file)]
    return lines

def get_weights(dataset, thispdf, channel, filecounter):
    weights = dict()
    weight_sum = dict()
    pdfs = {}
    pdfs["ct10"] = ["CT10", "CT10as"]
    #pdfs["mstw"] = ["MSTW2008CPdeutnlo68cl"]
    #pdfs_ct66 = ["cteq66", "cteq66alphas"]
    #pdfs["nnpdf"] = ["NNPDF23nloas0119LHgrid"]
    pdfs["nnpdf"] = ["NNPDF23"]
    pdfs["nnpdf_down"] = ["NNPDF23nloas0116LHgrid", "NNPDF23nloas0117LHgrid", "NNPDF23nloas0118LHgrid"]
    pdfs["nnpdf_up"] = ["NNPDF23nloas0120LHgrid", "NNPDF23nloas0121LHgrid", "NNPDF23nloas0122LHgrid"]

    events = {}
    handles = {}
    for p, lst in pdfs.items():
        print pdfs[p], thispdf
        if not ((thispdf in pdfs[p]) or (pdfs[p] == ["NNPDF23"] and thispdf == "NNPDF23nloas0119LHgrid")): continue
        print "AAA"
        file_list_file = os.path.join(os.environ["STPOL_DIR"], "filelists", "pdf", p, dataset+".txt")
        file_list = get_file_list(file_list_file)
        print file_list
        events[p] = Events(file_list)
        for l in lst:        
            handles[l] = Handle ('std::vector<float>')
            weight_sum[l] = [0] * sizes[l]
        
    n_events = 0
    #n_events2 = 0
    label = "pdfWeights"
    PROC = "STPOLPDF"

    path = os.path.join(os.environ["STPOL_DIR"], "src", "pdf_uncertainties", "eventlists")
    picklename = "%s/events_%s_%s_%s.pkl" % (path, channel, dataset, filecounter)
    with open(picklename, 'rb') as f:
         outdata = pickle.load(f)
         #outdatai = pickle.load(f)

    first = True
    for p in pdfs:
        print pdfs[p], thispdf
        if not ((thispdf in pdfs[p]) or (pdfs[p] == ["NNPDF23"] and thispdf == "NNPDF23nloas0119LHgrid")): continue
        print "THIS"
        for event in events[p]:
            run = event._event.eventAuxiliary().run()    
            lumi = event._event.eventAuxiliary().luminosityBlock()
            eventid = event._event.eventAuxiliary().id().event()

            if not run in outdata[channel]: continue
            if not lumi in outdata[channel][run]: continue
            if not eventid in outdata[channel][run][lumi]: continue
            if not outdata[channel][run][lumi][eventid] == True: continue

            if first:
                if run not in weights:
                    weights[run] = dict()
                if lumi not in weights[run]:
                    weights[run][lumi] = dict()
                weights[run][lumi][eventid] = dict()
                n_events += 1

            for i in range(len(pdfs[p])):
                event.getByLabel(label, 'weights'+pdfs[p][i], PROC, handles[pdfs[p][i]])
                weights[run][lumi][eventid][pdfs[p][i]] = copy(handles[pdfs[p][i]].product())
                for j in range(len(weights[run][lumi][eventid][pdfs[p][i]])):
                    weight_sum[pdfs[p][i]][j] += weights[run][lumi][eventid][pdfs[p][i]][j]
        first = False                    
        

    
    print "got weights"
    #assert n_events == n_events2
    for pdfset, wsums in weight_sum.items():
        for k in range(len(wsums)):
            wsums[k] = wsums[k] / n_events
            print pdfset, k, wsums[k], weight_sum[pdfset][k]
    return weights, weight_sum

if __name__ == "__main__":
    get_weights("Tbar_s", "NNPDF23", "mu", 0)
