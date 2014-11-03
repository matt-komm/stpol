import ROOT, sys, numpy

f = ROOT.TFile(sys.argv[1])

kl = [k for k in f.GetListOfKeys()]

def hfilter(kn):
    r = True
    r = r and ("DEBUG" not in kn)
    r = r and ("proj" not in kn)
    r = r and ("asym" not in kn)
    r = r and ("anom" not in kn)
    return r

def is_nominal(kn):
    if "tm_" not in kn:
        r = len(kn.split("__"))==2
        r = r and ("comphep" not in kn)
        r = r and ("asym" not in kn)
        r = r and ("unweighted" not in kn)
        r = r and hfilter(kn)
    else:
        r = kn == "tm__nominal"
    return r

noms = {}
for k in kl:
    kn = k.GetName()
    #print "ISNOM", kn, is_nominal(kn)
    if is_nominal(kn):
        noms[kn] = k.ReadObj()
        print "NOMINAL", kn, noms[kn].Integral(), noms[kn].GetEntries()
def check_entries_different(kn, h1, h2):
    e1 = int(h1.GetEntries())
    e2 = int(h2.GetEntries())
    r = True
    r = r and "mass" not in kn
    r = r and "scale" not in kn
    r = r and "matching" not in kn
    r = r and "comphep" not in kn
    _r = r and "jes" not in kn
    _r = _r and "jer" not in kn
    _r = _r and "met" not in kn
    if e1==0 or e2==0:
        print "ENTRIES", kn, e1, e2
        return False
    if _r and abs(e1-e2) > 100:
        print "ENTRIES", kn, e1, e2
        return False
    if r and 100 * abs(e1-e2)/e1 > 10:
        print "ENTRIES", kn, e1, e2
        return False
    return True

def check_integral_different(kn, h1, h2):
    e1 = h1.Integral()
    e2 = h2.Integral()
    r = True
    #r = r and "mass" not in kn
    #r = r and "scale" not in kn
    #r = r and "matching" not in kn
    r = r and "comphep" not in kn
    r = r and "unweighted" not in kn

    #expected to have a pretty huge yield effect
    _r = r and "wzjets_matching" not in kn
    _r = _r and "wzjets_scale" not in kn

    if e1==0 or e2==0:
        print "INTEGRAL", kn, e1, e2
        return False

    if _r and abs(e1-e2)/e1 > 0.1:
        print "INTEGRAL", kn, e1, e2
        return False
    if r and abs(e1-e2)/e1 > 1.5:
        print "INTEGRAL", kn, e1, e2
        return False
    return True

def check_chi2shape_different(kn, h1, h2):
    chi2 = h1.Chi2Test(h2, "WW CHI2/NDF")
    r = True
    #r = r and "mass" not in kn
    #r = r and "scale" not in kn
    #r = r and "matching" not in kn
    r = r and "comphep" not in kn
    r = r and "unweighted" not in kn
    if r and chi2 > 9.0:
        print "CHI2", kn, chi2
        return False
    return True

def check_ksshape_different(kn, h1, h2):
    ks = h1.KolmogorovTest(h2, "X")
    r = True
    #r = r and "mass" not in kn
    #r = r and "scale" not in kn
    #r = r and "matching" not in kn
    r = r and "comphep" not in kn
    r = r and "unweighted" not in kn
    if r and ks < 0.00001:
        print "KS", kn, ks
        return False
    return True

def check_is_different(kn, h1, h2):
    if "tm_" in kn:
        return True
    bc1 = numpy.array(
        [h1.GetBinContent(i) for i in range(0,h1.GetNbinsX()+1)]
    )
    bc2 = numpy.array(
        [h2.GetBinContent(i) for i in range(0,h2.GetNbinsX()+1)]
    )
    if "qcd" not in kn and sum(bc1-bc2)==0:
        print "SAME", kn, bc1[2], bc2[2]
        return False
    return True

def nomname(kn):
    if "tm_" not in kn:
        return "__".join(kn.split("__")[0:2])
    else:
        return "tm__nominal"
totr = True
for k in kl:
    kn = k.GetName()
    if not hfilter(kn):
        continue
    h = k.ReadObj()
    if not is_nominal(kn):
        nom = noms[nomname(kn)]
        r1 = check_entries_different(kn, h, nom)
        r2 = check_integral_different(kn, h, nom)
        r3 = check_chi2shape_different(kn, h, nom)

        #r = r and check_ksshape_different(kn, h, nom)
        r4 = check_is_different(kn, h, nom)
        r = r1 and r2 and r3 and r4
        if r:
            print "PASS", kn
        else:
            print "FAIL", kn
        totr = totr and r
if not totr:
    sys.stderr.write("Some tests failed!\n")
    exit(1)
