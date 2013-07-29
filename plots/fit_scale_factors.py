#Fit parameters from the final fit
#Extracted in the muon channel using lqetafit/topfit.py
#The first element in the tuple is a list of regex patterns to which you want to match this scale factor
#The second element is the scale factor to apply (flat)
#FIXME: most likely, one can incorporate the QCD scale factor from the QCD fit here as well
#-JP
fitpars = {}
fitpars["mu"] = {}
fitpars["ele"] = {}
fitpars["mu"]['final_2j1t'] = [
    (
        PhysicsProcess.tchan.subprocesses,
        1.227350
    ),
    (
        PhysicsProcess.TTJets_exc.subprocesses + PhysicsProcess.schan.subprocesses + PhysicsProcess.tWchan.subprocesses,
        1.075594
    ),
    (
        PhysicsProcess.WJets_mg_exc.subprocesses + PhysicsProcess.diboson.subprocesses,
        1.051505
    ),
    (
        ["QCDSingle.*"], #Data-driven QCD
        1.018268
    ),
]

fitpars["mu"]['final_2j1t_mva_no_mt_cut'] = [
    (
        PhysicsProcess.tchan.subprocesses,
        1.193656
    ),
    (
        PhysicsProcess.TTJets_exc.subprocesses + PhysicsProcess.schan.subprocesses + PhysicsProcess.tWchan.subprocesses,
        1.159650
    ),
    (
        PhysicsProcess.WJets_mg_exc.subprocesses + PhysicsProcess.diboson.subprocesses,
        1.026309
    ),
    (
        ["QCDSingle.*"], #Data-driven QCD
        0.961991
    ),
]

fitpars["mu"]['final_2j1t'] = [
    (
        PhysicsProcess.tchan.subprocesses,
        1.082103
    ),
    (
        PhysicsProcess.TTJets_exc.subprocesses + PhysicsProcess.schan.subprocesses + PhysicsProcess.tWchan.subprocesses,
        1.038168
    ),
    (
        PhysicsProcess.WJets_mg_exc.subprocesses + PhysicsProcess.diboson.subprocesses,
        1.307381
    ),
    (
        ["QCDSingle.*"], #Data-driven QCD
        1.008779
    ),
]

fitpars["ele"]['final_2j1t_mva_no_mt_cut'] = [
    (
        PhysicsProcess.tchan.subprocesses,
        1.113995
    ),
    (
        PhysicsProcess.TTJets_exc.subprocesses + PhysicsProcess.schan.subprocesses + PhysicsProcess.tWchan.subprocesses,
        0.989816
    ),
    (
        PhysicsProcess.WJets_mg_exc.subprocesses + PhysicsProcess.diboson.subprocesses,
        1.40333
    ),
    (
        ["QCDSingle.*"], #Data-driven QCD
        0.977402
    ),
]
