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

#The sample match rules for the fit parameters
tchan = PhysicsProcess.tchan.subprocesses
top = PhysicsProcess.TTJets_exc.subprocesses + PhysicsProcess.schan.subprocesses + PhysicsProcess.tWchan.subprocesses
wzjets = PhysicsProcess.WJets_mg_exc.subprocesses + PhysicsProcess.diboson.subprocesses
qcd = ["QCDSingle.*"]


def load_fit_results(fn):
    """
    Loads the fit results from a comma separated file.

    Args:
        fn: the file name with the fit results

    Returns:
        A dict with sample: (sf, err) items.
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

def from_file(fn, match_fmt='sample'):
    """
    Constructs the match list with the fit parameters.

    Args:
        fn: an input file name

    Keywords:
        match_fmt:
            samples: match to samples, e.g. TTJets_FullLept, T_t_Toleptons, etc.
            processes: match to the merged processes, e.g. tchan, wjets, etc.

    Returns:
        a list of the match tuples ([list, of, patterns], sf, err)
    """
    fr = load_fit_results(fn)
    if match_fmt=='sample':
        r = [
            (tchan,) + fr['tchan'],
            (top+qcd,) + fr['other'],
            (wzjets,) + fr['wzjets'],
        ]
    elif match_fmt=='process':
        r = [
            (['tchan'],) + fr['tchan'],
            (['ttjets', 'twchan', 'schan', 'qcd'],) + fr['other'],
            (['wjets', 'diboson', 'dyjets'],) + fr['wzjets'],
        ]
    else:
        raise ValueError("Undefined match_fmt: " + str(match_fmt))

    return r


#A list of the fit result files, separated by cut and channel
fit_files = [
    ('final_2j1t_mva', 'ele', os.environ["STPOL_DIR"] +
        '/final_fit/results/ele__mva_BDT_with_top_mass_C_eta_lj_el_pt_mt_el_pt_bj_mass_bj_met_mass_lj__no_metphi.txt'
    ),
    ('final_2j1t_mva', 'mu', os.environ["STPOL_DIR"] +
        '/final_fit/results/mu__mva_BDT_with_top_mass_eta_lj_C_mu_pt_mt_mu_met_mass_bj_pt_bj_mass_lj__no_metphi.txt'
    ),
]


fitpars = NestedDict()
fitpars_process = NestedDict()

#Load all the files in two formats
for (cut, chan, inf) in fit_files:
    fitpars[cut][chan] = from_file(inf, match_fmt='sample')
    fitpars_process[cut][chan] = from_file(inf, match_fmt='process')

#Separate SF-s for MET-variated templates, probably no longer needed.
names = [
    "t-channel", "top+QCD", "W, diboson"
]
for met in [30, 50, 70]:
    met = str(met)
    fitpars['final_2j1t_mva_met'+met]['mu'] = from_file(os.environ["STPOL_DIR"]+"/final_fit/results/histos/met%s/mu__mva_BDT_with_top_mass_eta_lj_C_mu_pt_mt_mu_met_mass_bj_pt_bj_mass_lj.txt" % met)
    # FIXME -> Currently no MET cut dependent results for electron channel
    fitpars['final_2j1t_mva_met'+met]['ele'] = from_file(os.environ["STPOL_DIR"]+"/final_fit/results/ele__mva_BDT_with_top_mass_C_eta_lj_el_pt_mt_el_pt_bj_mass_bj_met_mass_lj.txt")
    for i, name in zip(range(len(names)), names):
        fpmu = fitpars['final_2j1t_mva_met'+met]['mu'][i]
        fpel = fitpars['final_2j1t_mva_met'+met]['ele'][i]
        #print "%s | %.2f ± %.2f | %.2f ± %.2f |" % (name, fpmu[1], fpmu[2], fpel[1], fpel[2])

#FIXME: PLACEHOLDER
fitpars['final_2j1t'] = None
from pprint import pprint

#Convert to static dict
fitpars = fitpars.as_dict()

if __name__=="__main__":
    print "Yield tables: TODO latex format"
