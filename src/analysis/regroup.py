import ROOT, sys, json, os, numpy

def set_zero(h):
    for i in range(0, h.GetNbinsX()+2):
        h.SetBinContent(i, 0)
        h.SetBinError(i, 0)

def set_zero_if_neg(h):
    for i in range(0, h.GetNbinsX()+2):
        if h.GetBinContent(i) < 0:
            h.SetBinContent(i, 0)
            h.SetBinError(i, 1)

def histname(hn):
    spl = hn.split("__")

    if spl[1] in [
            "W1Jets_exclusive", "W2Jets_exclusive", "W3Jets_exclusive", "W4Jets_exclusive",
            "W1JetsToLNu", "W2JetsToLNu", "W3JetsToLNu", "W4JetsToLNu",
            ]:
        return {}

    #Use new ttbar samples
    if ("TTJets_matching" in hn
        or "TTJets_MSDecays_matchingdown_v1" in hn
        or "TTJets_MSDecays_matchingup_v1" in hn
        or "TTJets_scaleup" in hn
        or "TTJets_mass169_5" in hn
        or "TTJets_mass175_5" in hn
        or "TTJets_scaledown" in hn):
        print "skipping", spl
        return {}

    #skip comphep samples with QCD variations
    if "TTo" in hn and "qcd_antiiso" in hn:
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

syst_table = from_json("../../metadata/systematics.json")["systematics_table"]
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
        "wzjets": ["wjets", "diboson", "dyjets", "gjets"],
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
        "gjets": ["gjets"],
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
            print "\t\t", hn, parsed_hn, round(lumi * f.Get(hn).Integral(), 3), int(f.Get(hn).GetEntries())
            hd[frozenset(parsed_hn.items())] = f.Get(hn)

def get_hists(sample, syst, di, iso):
    hks = []
    subsamps = []
    for k in hd.keys():
        d = dict(k)
        if d["sample"]==sample and d["syst"]==syst and d["dir"]==di and d["iso"]==iso:
            hks.append(k)
            subsamps.append(d["subsample"])

    #FIXME: hack to get only W+jets heavy light variations
    if sample == "wjets" and "flavour" in syst:
        print "subsamps", subsamps
        for k in hd.keys():
            d = dict(k)
            if d["sample"]==sample and d["syst"]=="nominal" and d["iso"]==iso and d["subsample"] not in subsamps:
                print "extra append", d
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
    print "selected: ",sample, syst, di, iso, [str(hd[k].GetName()) for k in hks]

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
    print "toth", h1.GetName(), h1.Integral()

    #loop over subprocess in process
    subhists = dict()
    for sn in gs:
        h = get_hists(sn, "nominal", "none", "iso")
        subhists[sn] = sum_hists("%s__%s__%s" % (varname, gn, sn), h)

    for sn in gs:
        others = [h for (k, h) in subhists.items() if k!=sn]
        print "others", sn, others
        up = subhists[sn].Clone("%s__%s__%s__up" % (varname, gn, sn))
        up.Scale(1.5)
        toth_up = sum_hists("%s__%s__%s__up" % (varname, gn, sn), others + [up])
        if toth_up.Integral()>0:
            toth_up.Scale(h1.Integral() / toth_up.Integral())
        toth_up.Write("", ROOT.TObject.kOverwrite)
        print "toth_up", toth_up.GetName(), toth_up.Integral()

        down = subhists[sn].Clone("%s__%s__%s__down" % (varname, gn, sn))
        down.Scale(0.5)
        toth_down = sum_hists("%s__%s__%s__down" % (varname, gn, sn), others + [down])
        if toth_down.Integral()>0:
            toth_down.Scale(h1.Integral() / toth_down.Integral())
        toth_down.Write("", ROOT.TObject.kOverwrite)
        print "toth_down", toth_down.GetName(), toth_down.Integral()

    h1.Write("", ROOT.TObject.kOverwrite)
    print gn, h1.GetName(), int(round(h1.Integral()))
    #h1.Print()

for (gn, gs) in final_groups.items():
    for (sna, snb) in syst_table.items():
        if gn in ["tchan_inc", "wjets_inc", "DATA"]:
            continue

        if "qcd_antiiso" in sna:
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

        #matching and scale systematics should be split according to sample name
        if systs_to_split.has_key(syst):
            print "systs_to_split", systs_to_split[syst], gn
            if gn in systs_to_split[syst]:
                _snb = gn + "_" + snb
                print("renamed snb %s->%s" % (snb, _snb))
                snb = _snb

        print "snb=", snb, gn, syst

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

hss = sum([get_hists(gr, "nominal", "none", "antiiso") for gr in ["tchan", "ttjets", "wjets", "diboson", "dyjets", "twchan", "schan"]], [])
for h in hss:
    print "HSS nom", h.GetName(), h.Integral(), h.GetEntries()

hantiiso_mc = sum_hists("DEBUG_%s__antiiso_mc" % varname,
    sum([get_hists(gr, "nominal", "none", "antiiso") for gr in ["tchan", "ttjets", "wjets", "diboson", "dyjets", "twchan", "schan"]], [])
)
hantiiso_mc.Scale(lumi)
hantiiso_data.Write("", ROOT.TObject.kOverwrite)
hantiiso_mc.Write("", ROOT.TObject.kOverwrite)
hmc = hantiiso_mc
print "hmc", hmc.GetName(), hmc.Integral(), hmc.GetEntries()

hqcd = hantiiso_data.Clone("%s__qcd" % varname)
hqcd.Add(hantiiso_mc, -1.0)
hqcd.Scale(qcd_scale)
set_zero_if_neg(hqcd)
hqcd.Write("", ROOT.TObject.kOverwrite)
hqcd_up = hqcd.Clone(hqcd.GetName() + "__qcd_yield__up")
hqcd_up.Scale(1.5)
hqcd_up.Write("", ROOT.TObject.kOverwrite)

hqcd_down = hqcd.Clone(hqcd.GetName() + "__qcd_yield__down")
hqcd_down.Scale(0.5)
hqcd_down.Write("", ROOT.TObject.kOverwrite)


for sd in ["up", "down"]:
    hdata = sum_hists("DEBUG_%s__antiiso_data__qcd_antiiso__%s" % (varname, sd),
        get_hists(final_groups["DATA"][0], "qcd_antiiso", sd, "antiiso")
    )

    hss = sum([get_hists(gr, "qcd_antiiso", sd, "antiiso") for gr in ["tchan", "ttjets", "wjets", "diboson", "dyjets", "twchan", "schan"]], [])
    for h in hss:
        print "HSS", h.GetName(), h.Integral(), h.GetEntries()

    hmc = sum_hists("DEBUG_%s__antiiso_mc__qcd_antiiso__%s" % (varname, sd),
        sum([get_hists(gr, "qcd_antiiso", sd, "antiiso") for gr in ["tchan", "ttjets", "wjets", "diboson", "dyjets", "twchan", "schan"]], [])
    )
    hmc.Scale(lumi)
    print "hmc", hmc.GetName(), hmc.Integral(), hmc.GetEntries()
    hdata.Write("", ROOT.TObject.kOverwrite)
    hmc.Write("", ROOT.TObject.kOverwrite)
    hqcd = hdata.Clone("%s__qcd__qcd_antiiso__%s" % (varname, sd))
    hqcd.Add(hmc, -1.0)
    hqcd.Scale(qcd_scale)
    set_zero_if_neg(hqcd)
    hqcd.Write("", ROOT.TObject.kOverwrite)


ofd = {}
for k in of.GetListOfKeys():
    h = k.ReadObj()
    k = k.GetName()
    ofd[k] = h

for (k, v) in sorted(ofd.items(), key=lambda x:x[0]):
    print k, round(v.Integral(), 2), int(v.GetEntries())

of.Close()
