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
import numpy



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
    maxscale = 200
    minscale = 170
    maxid = 0
    minid = 0
    maxx = 0.
    minx = 0.
    weights = dict()
    weight_sum = dict()
    others = dict()
    pdfs = {}
    pdfs["ct10"] = ["CT10LHgrid", "CT10asLHgrid"]
    pdfs["mstw"] = ["MSTW2008CPdeutnlo68clLHgrid"]
    #pdfs_ct66 = ["cteq66", "cteq66alphas"]
    #pdfs["nnpdf"] = ["NNPDF23nloas0119LHgrid", "NNPDF22nlo100LHgrid", "NNPDF21100LHgrid"]
    #pdfs["nnpdf"] = ["NNPDF23"]
    pdfs["nnpdf"] = ["NNPDF30nloas0118LHgrid"]
    pdfs["nnpdf_down"] = ["NNPDF23nloas0116LHgrid", "NNPDF23nloas0117LHgrid", "NNPDF23nloas0118LHgrid"]
    pdfs["nnpdf_up"] = ["NNPDF23nloas0120LHgrid", "NNPDF23nloas0121LHgrid", "NNPDF23nloas0122LHgrid"]

    events = {}
    handles = {}
    flhandle = Handle ('float')
    inthandle = Handle ('int')
    for p, lst in pdfs.items():
        print pdfs[p], thispdf
        if not (thispdf in pdfs[p]): continue
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
    print picklename
    with open(picklename, 'rb') as f:
         outdata = pickle.load(f)
         #outdatai = pickle.load(f)

    first = True
    for p in pdfs:
        print pdfs[p], thispdf
        if not (thispdf in pdfs[p]): continue
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
                    others[run] = dict()
                if lumi not in weights[run]:
                    weights[run][lumi] = dict()
                    others[run][lumi] = dict()
                weights[run][lumi][eventid] = dict()
                others[run][lumi][eventid] = dict()
                n_events += 1

            event.getByLabel(label, 'scalePDF', PROC, flhandle)
            scale = flhandle.product()
            scale = numpy.frombuffer(scale, "float32", 1)[0]
            event.getByLabel(label, 'x1', PROC, flhandle)
            x1 = flhandle.product()
            x1 = numpy.frombuffer(x1, "float32", 1)[0]
            event.getByLabel(label, 'x2', PROC, flhandle)
            x2 = flhandle.product()
            x2 = numpy.frombuffer(x2, "float32", 1)[0]
            event.getByLabel(label, 'id1', PROC, inthandle)
            id1 = inthandle.product()
            id1 = numpy.frombuffer(id1, "int32", 1)[0]
            event.getByLabel(label, 'id2', PROC, inthandle)
            id2 = inthandle.product()
            id2 = numpy.frombuffer(id2, "int32", 1)[0]
            others[run][lumi][eventid]["scale"] = scale
            others[run][lumi][eventid]["x1"] = x1
            others[run][lumi][eventid]["x2"] = x2
            others[run][lumi][eventid]["id1"] = id1
            others[run][lumi][eventid]["id2"] = id2
            if scale>maxscale:
                maxscale = scale
            if scale<minscale:
                minscale = scale
            if max(id1, id2) > maxid:
                maxid = max(id1, id2)
            if min(id1, id2) < minid:
                minid = min(id1, id2)
            if max(x1, x2) > maxx:
                maxx = max(x1, x2)
            if min(x1, x2) < minx:
                minx = min(x1, x2)
            #print others  
            for i in range(len(pdfs[p])):
                event.getByLabel(label, 'weights'+pdfs[p][i], PROC, handles[pdfs[p][i]])
                weights[run][lumi][eventid][pdfs[p][i]] = copy(handles[pdfs[p][i]].product())
                for j in range(len(weights[run][lumi][eventid][pdfs[p][i]])):
                    """if abs(weights[run][lumi][eventid][pdfs[p][i]][j]) > 50:
                        
                        print "weight fail", dataset, thispdf, run, lumi, eventid, j, weights[run][lumi][eventid][pdfs[p][i]][j], scale, x1, x2, id1, id2"""
                    weight_sum[pdfs[p][i]][j] += weights[run][lumi][eventid][pdfs[p][i]][j]
        first = False                    
        

    
    print "got weights"
    print "minmax1", maxscale, minscale, maxid, minid, maxx, minx
    #assert n_events == n_events2
    for pdfset, wsums in weight_sum.items():
        for k in range(len(wsums)):
            wsums[k] = wsums[k] / n_events
            print pdfset, k, wsums[k], weight_sum[pdfset][k]
    return weights, weight_sum, others

if __name__ == "__main__":
    #(weights, wsum, others) = get_weights("Tbar_s", "CT10LHgrid", "mu", 0)
    #(weights, wsum, others) = get_weights("Tbar_s", "MSTW2008CPdeutnlo68clLHgrid", "mu", 0)
    #(weights, wsum, others) = get_weights("Tbar_s", "NNPDF23nloas0120LHgrid", "mu", 0)
    #(weights, wsum, others) = get_weights("T_t_ToLeptons", "CT10LHgrid", "mu", 0)
    #(weights, wsum, others) = get_weights("T_t_ToLeptons", "MSTW2008CPdeutnlo68clLHgrid", "mu", 0)
    #(weights, wsum, others) = get_weights("T_t_ToLeptons", "NNPDF23nloas0119LHgrid", "mu", 0)
    #(weights, wsum, others) = get_weights("T_t_ToLeptons", "NNPDF22nlo100LHgrid", "mu", 0)
    (weights, wsum, others) = get_weights("T_t_ToLeptons", "NNPDF30nloas0118LHgrid", "mu", 0)
    print wsum, weights
