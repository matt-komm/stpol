from plots.common.utils import NestedDict

#Determined using qcd_estimation/get_qcd_yield.py and qcd_estimation/update_sf.py
def load_qcd_sf(channel, met):
    import os
    base = os.path.join(os.environ['STPOL_DIR'], 'qcd_estimation', 'fitted', channel)
    fn = base + '/2j1t_no_MC_subtraction_mt_%s_plus.txt' % met
    fi = open(fn)
    li = fi.readline().strip().split()
    sf = float(li[0])
    return sf

qcdScale = dict()
qcdScale['mu'] = dict()
qcdScale['ele'] = dict()

#Determined as the ratio of the integral of anti-iso data after full selection / full selection minus MVA
#See qcd_scale_factors.ipynb for determination
qcd_cut_SF = NestedDict()
qcd_cut_SF['mva']['loose']['mu'] = 0.114379084967
qcd_cut_SF['mva']['loose']['ele'] = 0.0728291316527
qcd_cut_SF = qcd_cut_SF.as_dict()
