# -*- coding: utf-8 -*-
from plots.common.utils import NestedDict
from plots.common.utils import PhysicsProcess
import os

#Fit parameters from the final fit
#Extracted in the muon channel using final_fit/final_fit.py
#The first element in the tuple is a list of regex patterns to which you want to match this scale factor
#The second element is the scale factor to apply (flat)
#The third element is the error of the scale factor
#FIXME: most likely, one can incorporate the QCD scale factor from the QCD fit here as well
#-JP

tchan = PhysicsProcess.tchan.subprocesses
top = PhysicsProcess.TTJets_exc.subprocesses + PhysicsProcess.schan.subprocesses + PhysicsProcess.tWchan.subprocesses
wzjets = PhysicsProcess.WJets_mg_exc.subprocesses + PhysicsProcess.diboson.subprocesses
qcd = ["QCDSingle.*"]

fitpars = NestedDict()

def load_fit_results(fn):
    """
    Loads the fit results from a comma separated file.

    Args:
        fn: the file name with the fit results

    Returns:
        A dict with (sample, (sf, err)) items.
    """
    fi = open(fn, 'r')
    lines = map(lambda x: x.strip(), fi.readlines())
    sfs = dict()
    for line in lines:
        spl = line.split(",")
        spl = map(lambda x: x.strip(), spl)
        if not len(spl)==4:
            continue
        typ, sample, sf, err = spl
        if not typ=="rate":
            continue
        sfs[sample] = (float(sf), float(err))
    fi.close()
    return sfs

names = [
    "t-channel", "top+QCD", "W, diboson"
]
def from_file(fn):
    fr = load_fit_results(fn)
    r = [
        (tchan,) + fr['tchan'],
        (top+qcd,) + fr['other'],
        (wzjets,) + fr['wzjets'],
    ]
    return r

#fitpars['final_2j1t_mva']['ele'] = from_file("final_fit/results/ele__mva_BDT_with_top_mass_C_eta_lj_el_pt_mt_el_pt_bj_mass_bj_met_mass_lj__top_plus_qcd.txt")
#fitpars['final_2j1t_mva']['mu'] = from_file("final_fit/results/mu__mva_BDT_with_top_mass_eta_lj_C_mu_pt_mt_mu_met_mass_bj_pt_bj_mass_lj__top_plus_qcd.txt")
fitpars['final_2j1t_mva']['ele'] = from_file(os.environ["STPOL_DIR"]+"/final_fit/results/ele__mva_BDT_with_top_mass_C_eta_lj_el_pt_mt_el_pt_bj_mass_bj_met_mass_lj.txt")
fitpars['final_2j1t_mva']['mu'] = from_file(os.environ["STPOL_DIR"]+"/final_fit/results/mu__mva_BDT_with_top_mass_eta_lj_C_mu_pt_mt_mu_met_mass_bj_pt_bj_mass_lj.txt")

for met in [30, 50, 70]:
    met = str(met)
    fitpars['final_2j1t_mva_met'+met]['mu'] = from_file(os.environ["STPOL_DIR"]+"/final_fit/results/histos/met%s/mu__mva_BDT_with_top_mass_eta_lj_C_mu_pt_mt_mu_met_mass_bj_pt_bj_mass_lj.txt" % met)
    fitpars['final_2j1t_mva_met'+met]['ele'] = from_file(os.environ["STPOL_DIR"]+"/final_fit/results/histos/ele__mva_BDT_with_top_mass_C_eta_lj_el_pt_mt_el_pt_bj_mass_bj_met_mass_lj_met%s.txt" % met)
    for i, name in zip(range(len(names)), names):
        fpmu = fitpars['final_2j1t_mva_met'+met]['mu'][i]
        fpel = fitpars['final_2j1t_mva_met'+met]['ele'][i]
        print "%s | %.2f ± %.2f | %.2f ± %.2f |" % (name, fpmu[1], fpmu[2], fpel[1], fpel[2])

#PLACEHOLDER
fitpars['final_2j1t'] = None
from pprint import pprint

pprint(fitpars)
#OLD. HERE ONLY FOR REFERENCE
# #Cut based
# fitpars['final_2j1t']['mu'] = [
#     (tchan, 1.239592, -1),
#     (top, 1.081600, -1),
#     (WZJets, 1.057218, -1),
#     (qcd, 1.015709, -1),
# ]

# fitpars['final_2j1t']['ele'] = [
#     (tchan, 1.082103, -1),
#     (top, 1.038168, -1),
#     (WZJets, 1.307381, -1),
#     (qcd, 1.008779, -1),
# ]


# #New MVA with cut on MT
# fitpars['final_2j1t_mva']['mu'] = [
#     (tchan, 1.082186, 0.066186),
#     (top, 0.979322, 0.090524),
#     (WZJets, 1.511599, 0.187669),
#     (qcd, 1.342652, 0.895570),
# ]

# fitpars['final_2j1t_mva']['ele'] = [
#     (tchan, 1.298895, 0.102473 ),
#     (top, 0.987007, 0.096535 ),
#     (WZJets, 1.530719, 0.323450),
#     (qcd, 1.008886, -1),
# ]

# #OLD MVA where MET/MT was not applied
# fitpars['final_2j1t_mva_no_mt_cut']['mu'] = [
#     (tchan, 1.193656, -1),
#     (top, 1.159650, -1),
#     (WZJets, 1.026309, -1),
#     (qcd, 0.961991, -1),
# ]
# fitpars['final_2j1t_mva_no_mt_cut']['ele'] = [
#     (tchan, 1.113995, -1),
#     (top, 0.989816, -1),
#     (WZJets, 1.40333, -1),
#     (qcd, 0.977402, -1),
# ]

#Convert to static dict
fitpars = fitpars.as_dict()

if __name__=="__main__":
    print "Yield tables: TODO latex format"
