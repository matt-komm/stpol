import math
#import matplotlib
#matplotlib.use('Agg')

import ROOT, sys, json
#import numpy
import os
ROOT.TH1.AddDirectory(False)

#from matplotlib import pyplot as plt
#plt.ioff()

inf = sys.argv[1]
tf = ROOT.TFile(inf)

def to_dict(kn):
    kn = kn.split(";")
    d = dict()

    for x in kn:
        a,b = x.split("=")
        d[a] = b
    return d

print("loading keys from ", inf)
#keylist = {k.GetName(): k for k in tf.GetListOfKeys() if "transfer" in k.GetName() or "cos" in k.GetName()}
keylist = {k.GetName(): k for k in tf.GetListOfKeys()}
keydicts = {k: to_dict(k) for k in keylist.keys()}
print("loaded keys: ", len(keylist))
#sys.exit(1)
mc_samples = [
    "tchan", "wjets", "ttjets",
    "twchan", "schan", "diboson", #"gjets", 
    "dyjets",
    "wjets__heavy", "wjets__light"
]
samples = mc_samples + [
    "data_mu", "data_ele"
]

def from_json(fn):
    fi = open(fn)
    ret = json.load(fi)
    fi.close()
    return ret

syst_tables = from_json("../../metadata/systematics.json")
lumis = from_json("../../metadata/lumis.json")
lumis["tau"] = 1.0
pdgid_map = {"mu":13, "ele":11, "tau":15}
qcd_sfs = from_json("../../metadata/qcd_sfs.json")

def select_hist(k, histname, lepton, selection_major, selection_minor, njets, ntags, iso):
    d = keydicts[k]
    if d["object"] != histname:
        return None

    if d["lepton"] != lepton:
        return None

    if d["selection_major"] != selection_major:
        return None

    if d["selection_minor"] != selection_minor:
        return None

    if d["njets"] != str(njets):
        return None

    if d["ntags"] != str(ntags):
        return None

    if d["iso"] != iso:
        return None

    #is double variated MC
    #Hacky parsing
    if d["systematic"]!="nominal" and d["scenario"]!="nominal" and d["systematic"]!="" and ("wjets" in d["scenario"] or "qcd" in d["scenario"]) and "FSIM" not in k:
        return None

    
    #hacky parsing of (systematic variation at generation, weight scenario) tuple
    if d["systematic"]!="" and d["systematic"]!="data":
        s2 = d["scenario"]

        #weight was not nominal
        if s2 != "nominal":
            s2 = syst_tables["systematics_table"].get(s2, s2)
            idx = s2.rfind("__")
            if idx>0:
                syst_dir = s2[idx+2:]
                syst = s2[:idx]
            else:
                syst_dir = "none"
                syst = s2
            #print "syst", d, syst, syst_dir, s2

        #weight was nominal, processing was variated
        else:
            s2 = d["systematic"]
            s2 = syst_tables["systematics_table"].get(s2, None)
            if not s2 and d["systematic"] != "wjets_fsim_nominal":
                raise Exception("systematic %s not understood" % s2)

            if d["systematic"] == "wjets_fsim_nominal":
                syst = "wjets_fsim_nominal"
                syst_dir = "none"
            elif s2!="nominal":
                idx = s2.rfind("__")
                if idx>0:
                    syst_dir = s2[idx+2:]
                    syst = s2[:idx]
                else:
                    syst_dir="none"
                    syst = s2
            else:
                syst = "nominal"
    else:
        if d["scenario"] == "unweighted":
            syst = "nominal"
        else:
            s2 = d["scenario"]
            idx = s2.rfind("__")
            syst_dir = s2[idx+2:]
            syst = s2[:idx]

    if "comphep" in d["systematic"] and d["scenario"] == "nominal":
        syst = syst_tables["systematics_table"][d["systematic"]]
        syst_dir = "none"

    if syst=="nominal":
        hk = "%s__%s" % (d["object"], d["sample"])
    elif syst_dir=="none":
        hk = "%s__%s__%s" % (d["object"], d["sample"], syst)
    else:
        hk = "%s__%s__%s__%s" % (d["object"], d["sample"], syst, syst_dir)
    hk = hk.replace("comphep_nominal", "comphep__nominal")
    return hk, d

def set_zero(h):
    for i in range(0, h.GetNbinsX()+2):
        h.SetBinContent(i, 0)
        h.SetBinError(i, 0)

def set_neg_zero(h):
    for i in range(0, h.GetNbinsX()+2):
        if h.GetBinContent(i) < 0:
            h.SetBinContent(i, 0)
            h.SetBinError(i, 0)

def select_hists(histname, lepton, selection_major, selection_minor, njets, ntags):
    hd = dict()
    hd["iso"] = dict()
    hd["antiiso"] = dict()
    ret = {}
    for iso in ["iso", "antiiso"]:
        for k in keylist.keys():
            hk = select_hist(k, histname, lepton, selection_major, selection_minor, njets, ntags, iso)

            if not hk:
                continue
            hk, d = hk

            h = keylist[k].ReadObj()
            set_neg_zero(h)

            for i in range(0, h.GetNbinsX() + 2):
                x, y = h.GetBinContent(i), h.GetBinError(i)

            kn = "%s__%s" % (hk, iso)
            if ret.has_key(kn):
                raise Exception("Already exists: %s" % kn)
            ret[kn] = h
    
            if "JetsToLNu_matching" in k or "JetsToLNu_scale" in k:
                try:
                    #get corresponding nominal fullsim and fastsim histograms and scale accordingly
                    fullsim_k = k.replace("JetsToLNu_scaleup", "Jets_exclusive").replace("JetsToLNu_scaledown", "Jets_exclusive").replace("JetsToLNu_matchingup", "Jets_exclusive").replace("JetsToLNu_matchingdown", "Jets_exclusive").replace("systematic=scaleup", "systematic=nominal").replace("systematic=scaledown", "systematic=nominal").replace("systematic=matchingup", "systematic=nominal").replace("systematic=matchingdown", "systematic=nominal").replace("_light","").replace("_heavy","")

                    h_fullsim = keylist[fullsim_k].ReadObj()
                    set_neg_zero(h_fullsim)
                    fastsim_k = k.replace("JetsToLNu_scaleup", "Jets_exclusive_FSIM").replace("JetsToLNu_scaledown", "Jets_exclusive_FSIM").replace("JetsToLNu_matchingup", "Jets_exclusive_FSIM").replace("JetsToLNu_matchingdown", "Jets_exclusive_FSIM").replace("systematic=scaleup", "systematic=wjets_fsim_nominal").replace("systematic=scaledown", "systematic=wjets_fsim_nominal").replace("systematic=matchingup", "systematic=wjets_fsim_nominal").replace("systematic=matchingdown", "systematic=wjets_fsim_nominal").replace("_light","").replace("_heavy","")
                    
                    
                    h_fastsim = keylist[fastsim_k].ReadObj()
                    set_neg_zero(h_fastsim)
                    for i in range(0, h.GetNbinsX() + 2):
                        if h_fastsim.GetBinContent(i) > 0:
                            scaleby = h_fullsim.GetBinContent(i) / h_fastsim.GetBinContent(i)
                            
                            #Otherwise introduces statistical anomalies
                            if h_fullsim.GetBinContent(i) > 0.1 and h_fastsim.GetBinContent(i) > 0.1 and (scaleby > 3 or scaleby < 0.33): 
                                #if scaleby>2 or scaleby < 0.5: 
                                #    print "scaled bin", i, "by", scaleby, "from", h.GetBinContent(i), "to", h.GetBinContent(i) *scaleby, h_fullsim.GetBinContent(i), h_fastsim.GetBinContent(i)
                                h.SetBinContent(i, h.GetBinContent(i) * scaleby)
                            
                except KeyError:
                    print "KEYERROR", fullsim_k#, "or", fastsim_k
                    #happens only rarely for unnecessary case, just ignore and don't rescale
                    continue
                    
    if len(ret)==0:
        raise Exception("no histograms produced for %s:%s:%s:%s:%s:%s" % (histname, lepton, selection_major, selection_minor, njets, ntags))

    return {"%dj%dt_%s" % (njets, ntags, k):v for (k, v) in ret.items()}

def select_transfermatrix(gen_lepton, reco_lepton, selection_major, selection_minor, njets, ntags):
    hd = dict()
    for k in keylist.keys():

        hk = select_hist(
            k, "transfer_matrix",
            "gen_%s__reco_%s"%(gen_lepton, reco_lepton),
            selection_major, selection_minor, njets, ntags, "iso"
        )

        if not hk:
            continue

        hk, d = hk

        hk = hk.split("__")
        #print "TM", hk

        x = "__".join(hk[2:])
        if len(x)==0:
            x = "nominal"

        #x = "tm__pdgid_g%d_r%d__%s" % (pdgid_map[gen_lepton], pdgid_map[reco_lepton], x)
        x = "tm__%s" % (x)
        x = x.replace("scale", "tchan_scale")
        h = keylist[k].ReadObj()

        if hd.has_key(x):
            #print "Adding", hk, "to", x
            hd[x].Add(h)
        else:
            #print "Creating", hk, "to", x
            hd[x] = h

    if len(hd) == 0:
        raise Exception("no histograms produced for %s:%s" % (selection_major, selection_minor))
    tmkeys = hd.keys()

    for k in tmkeys:
        hd["%s__proj_x"%k] = hd[k].ProjectionX()
        hd["%s__proj_y"%k] = hd[k].ProjectionY()

    for k in hd.keys():
        hd[k].Scale(lumis[reco_lepton])

    return hd

#x = select_hists("bdt_sig_bg", "mu", "preselection", "nothing", 2, 1)

def write_hists(fname, hd):
    of = ROOT.TFile(fname, "RECREATE")
    of.cd()
    for (k, v) in hd.items():
        if "FSIM" in k: continue
        v = v.Clone(k)
        v.SetDirectory(of)
        v.Write()
    of.Write()
    of.Close()

def get_hist_contents(h):
    l = numpy.zeros((h.GetNbinsX()+2))
    for i in range(0, h.GetNbinsX()+2):
        l[i] = h.GetBinContent(i)
    return l

def get_hist_errors(h):
    l = numpy.zeros((h.GetNbinsX()+2))
    for i in range(0, h.GetNbinsX()+2):
        l[i] = h.GetBinError(i)
    return l

def get_hist_edges(h):
    l = numpy.zeros((h.GetNbinsX()+3))
    l[0] = -float("inf")
    for i in range(1, h.GetNbinsX()+2):
        l[i] = h.GetBinLowEdge(i)
    l[-1] = float("inf")
    return l

def plot_hists(hd, normed=True):
    ax = plt.axes()
    for (k, h) in hd.items():
        h = h.Clone()
        I = h.Integral()
        N = h.GetEntries()
        if normed:
            if h.Integral()<10 or h.GetEntries()<50:
                continue
            if h.Integral()>0:
                h.Scale(1.0 / h.Integral())
        edges = get_hist_edges(h)
        c, e = get_hist_contents(h), get_hist_errors(h)
        ax.errorbar(edges[1:], c, e, label="%s I=%.0f N=%.0f" % (k, I, N), drawstyle="steps-mid")
    ax.legend(loc="best")
    ax.grid(True, which="both")
    return ax

def get_systematics(hd, sample):
    systs = []
    for (k, v) in hd.items():
        if not sample in k:
            continue
        spl = k.split("__")
        if len(spl)==4:
            if spl[2] not in systs:
                systs.append(spl[2])
    return systs

def addhist(hd_src, hd_dst, namein, nameout):
    if not hd_src.has_key(namein):
        hd_src[namein] = hd_src["__".join(namein.split("__")[0:2])]

    if nameout in hd_dst.keys():
        hd_dst[nameout].Add(hd_src[namein])
    else:
        hd_dst[nameout] = hd_src[namein].Clone()

def merge_into(vname, inhd, outhd, outname, inname):
    systs = get_systematics(inhd, inname)

    #nominal
    ki = "%s__%s" % (vname, inname)
    ko = "%s__%s" % (vname, outname)
    addhist(inhd, outhd, ki, ko)

    #systematics
    for s in systs:
        for d in ["up", "down"]:
            _ki = "%s__%s__%s" % (ki, s, d)
            _ko = "%s__%s__%s" % (ko, s, d)
            addhist(inhd, outhd, _ki, _ko)

def merge_hists(vname, hd):
    out = dict()

    merge_into(vname, hd, out, "DATA", "DATA")

    merge_into(vname, hd, out, "ttjets", "ttjets")
    merge_into(vname, hd, out, "ttjets", "twchan")
    merge_into(vname, hd, out, "ttjets", "schan")

    merge_into(vname, hd, out, "wzjets", "wjets")
    merge_into(vname, hd, out, "wzjets", "diboson")
    merge_into(vname, hd, out, "wzjets", "dyjets")

    merge_into(vname, hd, out, "qcd", "qcd")

    merge_into(vname, hd, out, "tchan", "tchan")

    return out

output_dir = "output"
print("preqcd")
for lep in ["mu", "ele"]:
    for (nj, nt) in [(2,1), (3,1), (3,2), (2,0)]:
        print(nj, nt)

        d = "%s/bdt_scan/hists/preqcd/%dj_%dt/%s" % (output_dir, nj, nt, lep)
        os.makedirs(d)

        for variable in [
                "bdt_qcd",
                "met", "mtw",
                ]:
            x = select_hists(variable, lep, "preqcd", "nothing", nj, nt)
            write_hists("%s/%s.root" % (d, variable), x)
sys.exit(1)

print("preselection")
for lep in ["mu", "ele"]:
    for (nj, nt) in [(2,1), (3,1), (3,2), (2,0)]:
        print(nj, nt)

        d = "%s/bdt_scan/hists/preselection/%dj_%dt/%s" % (output_dir, nj, nt, lep)
        os.makedirs(d)

        for variable in [
                "bdt_sig_bg",
                "bdt_sig_bg_top_13_001",
                #"bdt_sig_bg_before_reproc",
                #"ljet_eta",
                "abs_ljet_eta",
#                "abs_ljet_eta_16",
                "C",
#                "met", "mtw", "shat", "ht",
                "cos_theta_lj",
                ]:
            x = select_hists(variable, lep, "preselection", "nothing", nj, nt)
            write_hists("%s/%s.root" % (d, variable), x)


print("reverse BDT cut for fit")
#for bdt_cut in [-0.20, -0.15, -0.10, -0.05, 0.0, 0.05, 0.06, 0.10, 0.13, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.50, 0.55, 0.6, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90]:
for bdt_cut in [0.6]:
    bdts = "%.5f" % bdt_cut
    print(bdts)
    for lep in ["mu", "ele"]:
        for (nj, nt) in [(2,1), (3,1), (3,2), (2,0)]:
            print(nj, nt)

            d = "%s/bdt_scan/hists/reverseBDT/%s/%dj_%dt/%s" % (output_dir, bdts, nj, nt, lep)
            os.makedirs(d)

            for variable in [
                    "bdt_sig_bg",
                    "bdt_sig_bg_top_13_001",
                    #"bdt_sig_bg_before_reproc",
                    #"ljet_eta",
                    "abs_ljet_eta",
    #                "abs_ljet_eta_16",
                    "C",
    #                "met", "mtw", "shat", "ht",
                    "cos_theta_lj",
                    ]:
                x = select_hists(variable, lep, "preselection", "LESSTHAN_%s" % bdts, nj, nt)
                write_hists("%s/%s.root" % (d, variable), x)


#for bdt_cut in [0.0, 0.06, 0.13, 0.2, 0.4, 0.6, 0.8, 0.9]:
#for bdt_cut in numpy.arange(-0.2, 0.9, 0.1):
#for bdt_cut in [0.0, 0.06, 0.13, 0.2, 0.4, 0.6,]:
#for bdt_cut in [0.6]:
for bdt_cut in [-0.20, -0.10, 0.00, 0.06, 0.10, 0.13, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.50, 0.55, 0.6, 0.65, 0.70, 0.75, 0.80]:
    bdts = "%.5f" % bdt_cut
    print(bdts)
    for reco_lep in ["mu", "ele"]:
        d = "%s/bdt_scan/hists/%s/%s" % (output_dir, bdts, reco_lep)
        if not os.path.exists(d):
            os.makedirs(d)
        x = select_hists("cos_theta_lj", reco_lep, "bdt", bdts, 2, 1)
        write_hists("%s/cos_theta_lj.root" % (d), x)

        for gen_lep in ["mu", "ele", "tau"]:#, "NA"]:
            tm = select_transfermatrix(gen_lep, reco_lep, "bdt", bdts, 2, 1)
            write_hists("%s/tmatrix_nocharge__gen_%s.root" % (d, gen_lep), tm)

        for (nj, nt) in [(3,1), (3,2), (2,0)]:
            d = "%s/bdt_scan/hists/%dj_%dt/%s/%s" % (output_dir, nj, nt, bdts, reco_lep)
            if not os.path.exists(d):
                os.makedirs(d)
            x = select_hists("cos_theta_lj", reco_lep, "bdt", bdts, nj, nt)
            write_hists("%s/cos_theta_lj.root" % (d), x)

for reco_lep in ["mu", "ele"]:
    d = "%s/bdt_scan/hists/%s/%s" % (output_dir, "etajprime_topmass_default", reco_lep)
    x = select_hists("cos_theta_lj", reco_lep, "cutbased", "etajprime_topmass_default", 2, 1)

    d = "%s/bdt_scan/hists/%s/%s" % (output_dir, "etajprime_topmass_default", reco_lep)
    if not os.path.exists(d):
        os.makedirs(d)

    for gen_lep in ["mu", "ele", "tau"]:
        tm = select_transfermatrix(gen_lep, reco_lep, "cutbased", "etajprime_topmass_default", 2, 1)
        write_hists("%s/tmatrix_nocharge__gen_%s.root" % (d, gen_lep), tm)

##
## cut-based selection
##
for lep in ["mu", "ele"]:
    d = "%s/bdt_scan/hists/etajprime_topmass_default/%s" % (output_dir, lep)
    if not os.path.exists(d):
        os.makedirs(d)
    x = select_hists("cos_theta_lj", lep, "cutbased", "etajprime_topmass_default", 2, 1)
    write_hists("%s/cos_theta_lj.root" % (d), x)
    for gen_lep in ["mu", "ele", "tau"]:
        tm = select_transfermatrix(gen_lep, reco_lep, "cutbased", "etajprime_topmass_default", 2, 1)
        write_hists("%s/tmatrix_nocharge__gen_%s.root" % (d, gen_lep), tm)
