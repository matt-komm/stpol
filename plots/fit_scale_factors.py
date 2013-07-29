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

fitpars['final_2j1t']['mu'] = [
    (tchan, 1.227350),
    (top, 1.075594),
    (WZJets, 1.051505),
    (qcd, 1.018268),
]

fitpars['final_2j1t_mva_no_mt_cut']['mu'] = [
    (tchan, 1.193656),
    (top, 1.159650),
    (WZJets, 1.026309),
    (qcd, 0.961991),
]

fitpars['final_2j1t_mva']['mu'] = [
    (tchan, 1.164032),
    (top, 1.018774),
    (WZJets, 1.317858),
    (qcd, 0.975618),
]

fitpars['final_2j1t']['ele'] = [
    (tchan, 1.082103),
    (top, 1.038168),
    (WZJets, 1.307381),
    (qcd, 1.008779),
]

fitpars['final_2j1t_mva_no_mt_cut']['ele'] = [
    (tchan, 1.113995),
    (top, 0.989816),
    (WZJets, 1.40333),
    (qcd, 0.977402),
]

fitpars['final_2j1t_mva']['ele'] = [
    (tchan, 1.085781),
    (top, 1.045250),
    (WZJets, 1.128681),
    (qcd, 1.018550),
]

#Convert to static dict
fitpars = fitpars.as_dict()
