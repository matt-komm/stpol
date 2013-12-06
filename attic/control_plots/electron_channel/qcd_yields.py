
#---------------electron channel------------------------
qcd_fitvalue = { # values returned by the theta-auto fit in different control regions without MET requirement
    "final_lep" :   121, # b+el+pu
    "2j0t_lep"  :   4351,
    "3j1t_lep"  :   502,

    }

qcd_template_size = { # the size of template in the control region (actually identical for inclusive and lepotnic samples (comes directly from data) )
    "final_lep" :  1,
    "2j1t_lep"  :  1,
    "2j0t_lep":    1,
    "3j1t_lep":    1,
    }

#---------------muon channel--------------------------------
qcd_fitvalue_mu = {
    "final_lep": 281,
    "2j0t_lep": 3004.4,
    "3j1t_lep": 532,
    }

qcd_template_size_mu = {
    "final_lep": 1478,
    "2j0t_lep": 1,
    "3j1t_lep": 1,
    }

def getQCDYield( qcd_temp_hist, mode = "final", doDebug = False, channel = "ele" ):
    if channel == "ele":
        qcd_yield = qcd_fitvalue[mode] #* qcd_temp_hist.Integral()/qcd_template_size[mode]
    if channel == "mu":
        qcd_yield = qcd_fitvalue_mu[mode] #* qcd_temp_hist.Integral()/qcd_template_size_mu[mode]
    

    if doDebug:
        print "QCD yield from fit = " + str( qcd_fitvalue[mode] )
        print "Efficiency from control region to selected region = " + str( qcd_temp_hist.Integral()/qcd_template_size[mode] )
    return qcd_yield
