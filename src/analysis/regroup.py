import ROOT, sys, json, os, numpy

def histname(hn):
    spl = hn.split("__")

    if "_heavy" in spl[1] or "_light" in spl[1]:
        print "skipping", spl
        return {}

    if ("TTJets_matching" in hn
        or "TTJets_MSDecays_matchingdown_v1" in hn
        or "TTJets_MSDecays_matchingup_v1" in hn
        or "TTJets_scaleup" in hn
        or "TTJets_mass169_5" in hn
        or "TTJets_mass175_5" in hn
        or "TTJets_scaledown" in hn):
        print "skipping", spl
        return {}

    if len(spl)==5:
        return {"var":spl[0], "subsample":spl[1], "syst":spl[2], "dir":spl[3], "iso":spl[4]}
    if len(spl)==4:
        return {"var":spl[0], "subsample":spl[1], "syst":spl[2], "dir":"none", "iso":spl[3]}
    if len(spl)==3:
        return {"var":spl[0], "subsample":spl[1], "syst":"nominal", "dir":"none", "iso":spl[2]}
    raise Exception("unknown split: %s" % str(spl))

def from_json(fn):
    fi = open(fn)
    ret = json.load(fi)
    fi.close()
    return ret

def get_bins(h):
    return numpy.array([h.GetBinContent(i) for i in range(0, h.GetNbinsX()+1)])

syst_table = from_json("systematics.json")["systematics_table"]
merges = from_json("merges.json")


systs_to_split = {
    "scale": ["ttjets", "tchan", "wzjets"],
    "matching": ["ttjets", "wzjets"]
}


f = ROOT.TFile(sys.argv[1])
dn = os.path.dirname(sys.argv[2])
if not os.path.exists(dn):
    os.makedirs(dn)
of = ROOT.TFile(sys.argv[2], "RECREATE")

lepton = sys.argv[3]
jet_tag = sys.argv[4]
grouping = sys.argv[5]

final_groups = dict()

if grouping=="fit":
    final_groups = {
        "tchan":["tchan"],
        "ttjets": ["ttjets", "twchan", "schan"],
        "wzjets": ["wjets", "diboson", "dyjets"],
        #"qcd": ["qcd"],
    }
elif grouping=="plot":
    final_groups = {
        "tchan": ["tchan"],
        "ttjets": ["ttjets"],
        "wjets": ["wjets"],
        "twchan": ["twchan"],
        "schan": ["schan"],
        "diboson": ["diboson"],
        "dyjets": ["dyjets"]
}

lumi = int(from_json("../../metadata/lumis.json")[lepton])
qcd_scale = float(from_json("../../metadata/qcd_sfs.json")[lepton][jet_tag]["qcd_mva"])
final_groups["DATA"] = ["data_%s"%lepton]

hl = [k.GetName() for k in f.GetListOfKeys()]
hl.sort()

varname = hl[0].split("__")[0]

isosplit = {
        "iso": filter(lambda x: x.endswith("_iso"), hl),
        "antiiso": filter(lambda x: x.endswith("_antiiso"), hl)
}

hd = {}
for (iso, hists) in isosplit.items():
    print iso
    for (k, subsamples) in merges.items():
        if k in ["tchan_inc", "wjets_inc"]:
            continue
        print "\t", k
        hns = sum(map(lambda subsample: filter(lambda x: subsample in x, hists), subsamples), [])
        for hn in hns:
            parsed_hn = histname(hn)
            if parsed_hn == {}:
                continue
            parsed_hn["sample"] = k
            print "\t\t", hn, round(lumi * f.Get(hn).Integral(), 3), int(f.Get(hn).GetEntries())
            hd[frozenset(parsed_hn.items())] = f.Get(hn)

def get_hists(sample, syst, di, iso):
    hks = []
    for k in hd.keys():
        d = dict(k)
        if d["sample"]==sample and d["syst"]==syst and d["dir"]==di and d["iso"]==iso:
            hks.append(k)

    #revert to systematic with no direction
    if len(hks)==0:
        for k in hd.keys():
            d = dict(k)
            if d["sample"]==sample and d["syst"]==syst and d["dir"]=="none" and d["iso"]==iso:
                print "using syst", d, "instead of", syst, di
                hks.append(k)

    #revert to nominal template
    if len(hks)==0:
        for k in hd.keys():
            d = dict(k)
            if d["sample"]==sample and d["syst"]=="nominal" and d["dir"]=="none" and d["iso"]==iso:
                print "using nominal", d, "instead of", syst, di
                hks.append(k)

    #revert to empty systematic (DATA)
    if len(hks)==0:
        for k in hd.keys():
            d = dict(k)
            if d["sample"]==sample and d["syst"]=="" and d["dir"]=="none" and d["iso"]==iso:
                print "using nominal", d, "instead of", syst, di
                hks.append(k)

    #get t-channel nominal template, but reset
    if len(hks)==0:
        if sample=="tchan" and syst=="nominal" and di=="none" and iso=="iso":
            raise Exception("tchannel nominal did not exist")
        ret = get_hists("tchan", "nominal", "none", "iso")
        r = ret[0].Clone("UNNAMED")
        r.Reset("ICESM")
        print "using resetted t-channel instead of ", sample, syst, di, iso

        return [r]
    print "selected: ", [str(hd[k].GetName()) for k in hks]

    return [hd[k] for k in hks]

def sum_hists(newname, hists):
    itot = 0
    ntot = 0
    f = hists[0].Clone(newname)
    itot += f.Integral()
    ntot += f.GetEntries()
    for h in hists[1:]:
        itot += h.Integral()
        ntot += h.GetEntries()
        f.Add(h)
    assert(abs(itot - f.Integral())<0.000001)
    assert(ntot==f.GetEntries())
    return f

of.cd()
for (gn, gs) in final_groups.items():
    print gn, gs
    h1 = sum_hists("%s__%s" % (varname, gn),
        sum([get_hists(sn, "nominal", "none", "iso")
            for sn in gs],
            []
        )
    )
    if gn != "DATA":
        h1.Scale(lumi)
    h1.Write("", ROOT.TObject.kOverwrite)
    print gn, h1.GetName(), int(round(h1.Integral()))
    #h1.Print()

for (gn, gs) in final_groups.items():
    for (sna, snb) in syst_table.items():
        if gn in ["tchan_inc", "wjets_inc", "DATA"]:
            continue
        print sna, snb, gn, gs
        spl = snb.split("__")

        syst = None

        if len(spl)==2:
            syst, d = spl
        elif len(spl)==1:
            syst = spl[0]
            d = "none"
        else:
            raise Exception(str(spl))

        hl = sum(
            [get_hists(sn, syst, d, "iso")
            for sn in gs],
            []
        )
        print "gn=", gn, syst
        if systs_to_split.has_key(syst):
            print "systs_to_split", systs_to_split[syst], gn
            if gn in systs_to_split[syst]:
                _snb = gn + "_" + snb
                print("renamed snb %s->%s" % (snb, _snb))
                snb = _snb
        print "snb=",snb, gn, syst
        h1 = sum_hists(
            "%s__%s__%s" % (varname, gn, snb),
            hl
        )
        h1.Scale(lumi)
        nomh = of.Get("__".join(h1.GetName().split("__")[0:2]))
        if h1.GetEntries() == nomh.GetEntries() and h1.Integral()==nomh.Integral() and (get_bins(h1) == get_bins(nomh)).all():
            print h1.GetName(), " is same as nominal, not writing"
        else:
            h1.Write("", ROOT.TObject.kOverwrite)
            h1.Print()

#Prepare QCD template
hantiiso_data = sum_hists("DEBUG_%s__antiiso_data" % varname,
    get_hists(final_groups["DATA"][0], "", "none", "antiiso")
)

hantiiso_mc = sum_hists("DEBUG_%s__antiiso_mc" % varname,
    sum([get_hists(gr, "nominal", "none", "antiiso") for gr in ["tchan", "ttjets", "wjets", "diboson", "dyjets", "twchan", "schan"]], [])
)
hantiiso_data.Write("", ROOT.TObject.kOverwrite)
hantiiso_mc.Write("", ROOT.TObject.kOverwrite)

hqcd = hantiiso_data.Clone("%s__qcd" % varname)
hqcd.Add(hantiiso_mc, -1.0)
hqcd.Scale(qcd_scale)
hqcd.Write("", ROOT.TObject.kOverwrite)

ofd = {}
for k in of.GetListOfKeys():
    h = k.ReadObj()
    k = k.GetName()
    ofd[k] = h

for (k, v) in sorted(ofd.items(), key=lambda x:x[0]):
    print k, round(v.Integral(), 2), int(v.GetEntries())

of.Close()

