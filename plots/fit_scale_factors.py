from plots.common.utils import NestedDict
from plots.common.utils import PhysicsProcess

#Fit parameters from the final fit
#Extracted in the muon channel using lqetafit/topfit.py
#The first element in the tuple is a list of regex patterns to which you want to match this scale factor
#The second element is the scale factor to apply (flat)
#FIXME: most likely, one can incorporate the QCD scale factor from the QCD fit here as well
#-JP

tchan = PhysicsProcess.tchan.subprocesses
top = PhysicsProcess.TTJets_exc.subprocesses + PhysicsProcess.schan.subprocesses + PhysicsProcess.tWchan.subprocesses
WZJets = PhysicsProcess.WJets_mg_exc.subprocesses + PhysicsProcess.diboson.subprocesses
qcd = ["QCDSingle.*"]

fitpars = NestedDict()

#FIXME! make this file auto-generating!
#Make sure a 3 tuple is used, that's what the rescale_to_fit function expects.

#Cut based
fitpars['final_2j1t']['mu'] = [
    (tchan, 1.239592, -1),
    (top, 1.081600, -1),
    (WZJets, 1.057218, -1),
    (qcd, 1.015709, -1),
]

fitpars['final_2j1t']['ele'] = [
    (tchan, 1.082103, -1),
    (top, 1.038168, -1),
    (WZJets, 1.307381, -1),
    (qcd, 1.008779, -1),
]


#New MVA with cut on MT
fitpars['final_2j1t_mva']['mu'] = [
    (tchan, 1.082186, 0.066186),
    (top, 0.979322, 0.090524),
    (WZJets, 1.511599, 0.187669),
    (qcd, 1.342652, 0.895570),
]

fitpars['final_2j1t_mva']['ele'] = [
    (tchan, 1.298895, 0.102473 ),
    (top, 0.987007, 0.096535 ),
    (WZJets, 1.530719, 0.323450),
    (qcd, 1.008886, -1),
]

#OLD MVA where MET/MT was not applied
fitpars['final_2j1t_mva_no_mt_cut']['mu'] = [
    (tchan, 1.193656, -1),
    (top, 1.159650, -1),
    (WZJets, 1.026309, -1),
    (qcd, 0.961991, -1),
]
fitpars['final_2j1t_mva_no_mt_cut']['ele'] = [
    (tchan, 1.113995, -1),
    (top, 0.989816, -1),
    (WZJets, 1.40333, -1),
    (qcd, 0.977402, -1),
]

#Convert to static dict
fitpars = fitpars.as_dict()

if __name__=="__main__":
    print "Yield tables: TODO latex format"
