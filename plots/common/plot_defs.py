from plots.common.cuts import Cuts,Cut
import copy
from plots.common.utils import PhysicsProcess

cp = copy.deepcopy

#FIXME: these cutlists need to be factorised away badly!
cutlist={}
cutlist['2j']=Cuts.n_jets(2)
cutlist['3j']=Cuts.n_jets(3)

cutlist['2j1t']=Cuts.n_jets(2)*Cuts.n_tags(1)
cutlist['2j0t']=Cuts.n_jets(2)*Cuts.n_tags(0)
cutlist['3j0t']=Cuts.n_jets(3)*Cuts.n_tags(0)
cutlist['3j1t']=Cuts.n_jets(3)*Cuts.n_tags(1)
cutlist['3j2t']=Cuts.n_jets(3)*Cuts.n_tags(2)


#Needed for RMS cut validation
cutlist['presel_ele_no_rms']=Cuts.hlt_isoele*Cuts.lepton_veto*Cuts.pt_jet*Cuts.one_electron
cutlist['presel_mu_no_rms']=Cuts.hlt_isomu*Cuts.lepton_veto*Cuts.pt_jet*Cuts.one_muon

cutlist['presel_ele'] = cutlist['presel_ele_no_rms']*Cuts.rms_lj
cutlist['presel_mu'] = cutlist['presel_mu_no_rms']*Cuts.rms_lj

cutlist['nomet_ele']=cutlist['presel_ele']*Cuts.top_mass_sig*Cuts.eta_lj
cutlist['nomt_mu']=cutlist['presel_mu']*Cuts.top_mass_sig*Cuts.eta_lj
cutlist['noeta_ele']=cutlist['presel_ele']*Cuts.top_mass_sig*Cuts.met
cutlist['noeta_mu']=cutlist['presel_mu']*Cuts.top_mass_sig*Cuts.mt_mu
cutlist['final_ele']=cutlist['nomet_ele']*Cuts.met
cutlist['final_mu']=cutlist['nomt_mu']*Cuts.mt_mu

cutlist['bdt_mu_tight'] = Cut('mva_BDT>0.6')
cutlist['bdt_ele_tight'] = Cut('mva_BDT>0.7')
cutlist['bdt_mu_loose'] = Cut('mva_BDT>0.36')
cutlist['bdt_ele_loose'] = Cut('mva_BDT>0.2')


#Fit parameters from the final fit
#Extracted in the muon channel using lqetafit/topfit.py
#The first element in the tuple is a list of regex patterns to which you want to match this scale factor
#The second element is the scale factor to apply (flat)
#FIXME: most likely, one can incorporate the QCD scale factor from the QCD fit here as well
#-JP
fitpars = {}
fitpars['final_2j1t_cut'] = [
    (
        PhysicsProcess.tchan.subprocesses,
        1.202393
    ),
    (
        PhysicsProcess.TTJets_exc.subprocesses + PhysicsProcess.schan.subprocesses + PhysicsProcess.tWchan.subprocesses,
        1.052675
    ),
    (
        PhysicsProcess.WJets_mg_exc.subprocesses + PhysicsProcess.diboson.subprocesses,
        1.120621
    ),
    (
        ["QCDSingle.*"], #Data-driven QCD
        1.037131
    ),
]
#FIXME: Andres, is this with the loose or tight WP?
fitpars['final_2j1t_mva'] = [
    (
        PhysicsProcess.tchan.subprocesses,
         1.19366
    ),
    (
        PhysicsProcess.TTJets_exc.subprocesses + PhysicsProcess.schan.subprocesses + PhysicsProcess.tWchan.subprocesses,
        1.15965
    ),
    (
        PhysicsProcess.WJets_mg_exc.subprocesses + PhysicsProcess.diboson.subprocesses,
        1.02631
    ),
    (
        ["QCDSingle.*"], #Data-driven QCD
        0.961991
    ),
]

#Load the scale factors externally for better factorisation
from plots.qcd_scale_factors import qcdScale
qcdScale['ele']['presel'] = 1.33
qcdScale['mu']['presel'] = 27.9

plot_defs={}

"""
Set the variable names centrally so that you don't have to do
find/replace if you want to change one of them and have them propagate to all the relevant plots
FIXME: Migrate to some central place, not only make_all_plots.py needs the nice names!
"""
varnames = dict()
varnames["cos_theta"] = 'cos #theta'
varnames["eta_lj"] = "#eta of the light jet"
#varnames["abs_eta_lj"] = "|#eta| of the light jet"
varnames["abs_eta_lj"] = "|#eta_{lj}|" #Like it is in the AN
varnames["top_mass"] = 'M_{b l #nu} [GeV]'
varnames["mt_mu"] = 'M_{t}(W) [GeV]'
varnames["met"] = 'E_{T}^{miss} [GeV]'
varnames["pt_lep"] = ['e p_{T} [GeV]', '#mu p_{T} [GeV]']
varnames["BDT_uncat"] = 'BDT'
varnames["n_tags"] = 'N_{tags}'
varnames["n_jets"] = 'N_{jets}'
varnames["rms_lj"] = 'RMS_{lj}'

plot_defs['lep_pt']={
    'enabled': True,
    'var': ['el_pt', 'mu_pt'],
    'range': [35, 25, 200],
    'iso': True,
    'estQcd': False,
    'gev': True,
    'log': True,
    'xlab': varnames["pt_lep"],
    'labloc': 'top-right',
    'elecut': cutlist['presel_ele'],
    'mucut': cutlist['presel_mu']
}


plot_defs['dr_bj']={
    'enabled': True,
    'var': 'deltaR_bj',
    'range': [20,0,5],
    'iso': True,
    'estQcd': 'final_2j1t',
    'gev': False,
    'log': False,
    'xlab': '#delta R(l,b)',
    'labloc': 'top-left',
    'elecut': cutlist['2j1t']*cutlist['final_ele'],
    'mucut': cutlist['2j1t']*cutlist['final_mu']
}

plot_defs['n_jets']={
    'enabled': True,
    'var': 'n_jets',
    'range': [3,0.5,3.5],
    'iso': True,
    'estQcd': False,
    'gev': False,
    'log': True,
    'xlab': varnames["n_jets"],
    'labloc': 'top-left',
    'elecut': cutlist['presel_ele'],
    'mucut': cutlist['presel_mu']
}

plot_defs['n_tags']={
        'enabled': True,
        'var': 'n_tags',
        'range': [3,-0.5,2.5],
        'iso': True,
        'estQcd': False,
        'gev': False,
        'log': True,
        'xlab': varnames["n_tags"],
        'labloc': 'top-right',
        'elecut': cutlist['presel_ele']*Cut('n_jets==2'),
        'mucut': cutlist['presel_mu']*Cut('n_jets==2')
}

plot_defs['n_tags_3j']={
        'enabled': True,
        'var': 'n_tags',
        'range': [4,-0.5,3.5],
        'iso': True,
        'estQcd': False,
        'gev': False,
        'log': True,
        'xlab': varnames["n_tags"],
        'labloc': 'top-right',
        'elecut': cutlist['presel_ele']*Cut('n_jets==3'),
        'mucut': cutlist['presel_mu']*Cut('n_jets==3')
}

plot_defs['cos_th_2j0t']={
    'enabled': True,
    'var': 'cos_theta',
    'range': [20,-1,1],
    'iso': True,
    'estQcd': '2j0t',
    'gev': False,
    'log': False,
    'xlab': varnames["cos_theta"],
    'labloc': 'top-left',
    'elecut': cutlist['2j0t']*cutlist['final_ele'],
    'mucut': cutlist['2j0t']*cutlist['final_mu']
}

plot_defs['cos_th_3j1t']={
    'enabled': True,
    'var': 'cos_theta',
    'range': [20,-1,1],
    'iso': True,
    'estQcd': '3j1t',
    'gev': False,
    'log': False,
    'xlab': varnames["cos_theta"],
    'labloc': 'top-left',
    'elecut': cutlist['3j1t']*cutlist['final_ele'],
    'mucut': cutlist['3j1t']*cutlist['final_mu']
}

plot_defs['cos_th_3j2t']={
    'enabled': True,
    'var': 'cos_theta',
    'range': [20,-1,1],
    'iso': True,
    'estQcd': '3j1t',
    'gev': False,
    'log': False,
    'xlab': varnames["cos_theta"],
    'labloc': 'top-left',
    'elecut': cutlist['3j2t']*cutlist['final_ele'],
    'mucut': cutlist['3j2t']*cutlist['final_mu']
}

plot_defs['cos_th_nomet']={
    'enabled': True,
    'var': 'cos_theta',
    'range': [20,-1,1],
    'iso': True,
    'estQcd': 'final_2j1t_nomtcut',
    'gev': False,
    'log': False,
    'xlab': varnames["cos_theta"],
    'labloc': 'top-left',
    'elecut': cutlist['2j1t']*cutlist['nomet_ele'],
    'mucut': cutlist['2j1t']*cutlist['nomt_mu']
}

plot_defs['met']={
    'enabled': True,
    'var': 'met',
    'range': [40,0,200],
    'iso': True,
    'estQcd': 'presel',
    'gev': True,
    'log': False,
    'xlab': varnames["met"],
    'labloc': 'top-right',
    'elecut': cutlist['2j1t']*cutlist['presel_ele'],
    'mucut': cutlist['2j1t']*cutlist['presel_mu']
}

plot_defs['met_final']={
    'enabled': True,
    'var': 'met',
    'range': [40,0,200],
    'iso': True,
    'estQcd': 'presel',
    'gev': True,
    'log': False,
    'xlab': varnames["met"],
    'labloc': 'top-right',
    'elecut': cutlist['2j1t']*cutlist['presel_ele']*Cuts.top_mass_sig*Cuts.eta_lj,
    'mucut': cutlist['2j1t']*cutlist['presel_mu']*Cuts.top_mass_sig*Cuts.eta_lj
}

plot_defs['mtW']={
    'enabled': True,
    'var': ['mt_el','mt_mu'],
    'range': [40,0,200],
    'iso': True,
    'estQcd': 'presel',
    'gev': True,
    'log': False,
    'xlab': varnames["mt_mu"],
    'labloc': 'top-right',
    'elecut': cutlist['2j1t']*cutlist['presel_ele'],
    'mucut': cutlist['2j1t']*cutlist['presel_mu']
}

plot_defs['mtW_final']={
    'enabled': True,
    'var': ['mt_el','mt_mu'],
    'range': [40,0,200],
    'iso': True,
    'estQcd': 'presel',
    'gev': True,
    'log': False,
    'xlab': varnames["mt_mu"],
    'labloc': 'top-right',
    'elecut': cutlist['2j1t']*cutlist['presel_ele']*Cuts.top_mass_sig*Cuts.eta_lj,
    'mucut': cutlist['2j1t']*cutlist['presel_mu']*Cuts.top_mass_sig*Cuts.eta_lj
}

plot_defs['abs_eta_lj']={
    'enabled': True,
    'var': 'abs(eta_lj)',
    'range': [50,0,5],
    'iso': True,
    'estQcd': 'final_2j1t',
    'gev': False,
    'log': False,
    'xlab': varnames["eta_lj"],
    'labloc': 'top-right',
    'elecut': cutlist['2j1t']*cutlist['noeta_ele'],
    'mucut': cutlist['2j1t']*cutlist['noeta_mu']
}

plot_defs['abs_eta_lj_2j0t']={
    'enabled': True,
    'var': 'abs(eta_lj)',
    'range': [50,0,5],
    'iso': True,
    'estQcd': '2j0t',
    'gev': False,
    'log': False,
    'xlab': varnames["eta_lj"],
    'labloc': 'top-right',
    'elecut': cutlist['2j0t']*cutlist['noeta_ele'],
    'mucut': cutlist['2j0t']*cutlist['noeta_mu']
}

plot_defs['abs_eta_lj_3j1t']={
    'enabled': True,
    'var': 'abs(eta_lj)',
    'range': [50,0,5],
    'iso': True,
    'estQcd': '3j1t',
    'gev': False,
    'log': False,
    'xlab': varnames["eta_lj"],
    'labloc': 'top-right',
    'elecut': cutlist['3j1t']*cutlist['noeta_ele'],
    'mucut': cutlist['3j1t']*cutlist['noeta_mu']
}

plot_defs['abs_eta_lj_3j2t']={
    'enabled': True,
    'var': 'abs(eta_lj)',
    'range': [50,0,5],
    'iso': True,
    'estQcd': '3j1t',
    'gev': False,
    'log': False,
    'xlab': varnames["eta_lj"],
    'labloc': 'top-right',
    'elecut': cutlist['3j2t']*cutlist['noeta_ele'],
    'mucut': cutlist['3j2t']*cutlist['noeta_mu']
}

plot_defs['mva_bdt']={
    'enabled': True,
    'var': 'mva_BDT',
    'range': [40,-1,1],
    'iso': True,
    'estQcd': 'presel',
    'gev': False,
    'log': True,
    'xlab': varnames["BDT_uncat"],
    'labloc': 'top-right',
    'elecut': cutlist['2j1t']*cutlist['presel_ele'],
    'mucut': cutlist['2j1t']*cutlist['presel_mu']
}

plot_defs['mva_bdt_zoom']={
    'enabled': True,
    'var': 'mva_BDT',
    'range': [50,0,1],
    'iso': True,
    'estQcd': 'presel',
    'gev': False,
    'log': False,
    'xlab': varnames["BDT_uncat"],
    'labloc': 'top-right',
    'elecut': cutlist['2j1t']*cutlist['presel_ele'],
    'mucut': cutlist['2j1t']*cutlist['presel_mu']
}

plot_defs['cos_th_mva_loose']={
    'enabled': True,
    'var': 'cos_theta',
    'range': [20,-1,1],
    'iso': True,
    'estQcd': 'final_2j1t',
    'gev': False,
    'log': False,
    'xlab': varnames["cos_theta"],
    'labloc': 'top-left',
    'elecut': cutlist['2j1t']*cutlist['presel_ele']*Cut('mva_BDT>0.28'),
    'mucut': cutlist['2j1t']*cutlist['presel_mu']*Cut('mva_BDT>0.24')
}


plot_defs['cos_th_mva_tight']={
    'enabled': True,
    'var': 'cos_theta',
    'range': [20,-1,1],
    'iso': True,
    'estQcd': 'final_2j1t',
    'gev': False,
    'log': False,
    'xlab': varnames["cos_theta"],
    'labloc': 'top-left',
    'elecut': cutlist['2j1t']*cutlist['presel_ele']*Cut('mva_BDT>0.7'),
    'mucut': cutlist['2j1t']*cutlist['presel_mu']*Cut('mva_BDT>0.5')
}

#-----------------------------------------------
# selection.tex
#-----------------------------------------------
nbins_selection = 20
plot_defs['2j1t_topMass']={
    'tags': ["an", "selection.tex"],
    'enabled': True,
    'var': 'top_mass',
    'range': [nbins_selection, 100, 500],
    'iso': True,
    'estQcd': '2j1t',
    'gev': True,
    'log': False,
    'xlab': varnames["top_mass"],
    'labloc': 'top-right',
    'elecut': cutlist['2j1t']*cutlist['presel_ele']*Cuts.met,
    'mucut': cutlist['2j1t']*cutlist['presel_mu']*Cuts.mt_mu,
    'dir': "selection"
}
plot_defs['2j1t_etaLj']={
    'tags': ["an", "selection.tex"],
    'enabled': True,
    'var': 'abs(eta_lj)',
    'range': [nbins_selection, 0, 5],
    'iso': True,
    'estQcd': '2j1t',
    'gev': False,
    'log': False,
    'xlab': varnames["eta_lj"],
    'labloc': 'top-right',
    'elecut': cutlist['2j1t']*cutlist['presel_ele']*Cuts.met,
    'mucut': cutlist['2j1t']*cutlist['presel_mu']*Cuts.mt_mu,
    'dir': "selection"
}

#For the jet RMS cut validation

#2j0t rms lj
plot_defs['2j0t_rmsLj_rmsOff']={
    'tags': ["an", "rms_jet", "selection.tex"],
    'enabled': True,
    'var': 'rms_lj',
    'range': [nbins_selection, 0, 0.1],
    'iso': True,
    'estQcd': '2j0t',
    'gev': False,
    'log': False,
    'xlab': varnames["rms_lj"],
    'labloc': 'top-right',
    'elecut': cutlist['2j0t']*cutlist['presel_ele_no_rms'],
    'mucut': cutlist['2j0t']*cutlist['presel_mu_no_rms'],
    'dir': "selection"
}

#2j0t eta lj
plot_defs['2j0t_etaLj_rmsOff']={
    'tags': ["an", "rms_jet", "selection.tex"],
    'enabled': True,
    'var': 'abs(eta_lj)',
    'range': [nbins_selection, 0, 4.5],
    'iso': True,
    'estQcd': '2j0t',
    'gev': False,
    'log': False,
    'xlab': varnames["abs_eta_lj"],
    'labloc': 'top-right',
    'elecut': cutlist['2j0t']*cutlist['presel_ele_no_rms'],
    'mucut': cutlist['2j0t']*cutlist['presel_mu_no_rms'],
    'dir': "selection"
}
plot_defs['2j0t_etaLj_rmsOn'] = cp(plot_defs['2j0t_etaLj_rmsOff'])
plot_defs['2j0t_etaLj_rmsOn']['elecut'] *= Cuts.rms_lj
plot_defs['2j0t_etaLj_rmsOn']['mucut'] *= Cuts.rms_lj
plot_defs['2j0t_etaLj_rmsOn']['estQcd'] = '2j0t'

#2j1t rms lj
plot_defs['2j1t_rmsLj_rmsOff'] = cp(plot_defs['2j0t_rmsLj_rmsOff'])
plot_defs['2j1t_rmsLj_rmsOff']['elecut'] = cutlist['2j1t']*cutlist['presel_ele_no_rms']*Cuts.top_mass_sig
plot_defs['2j1t_rmsLj_rmsOff']['mucut'] = cutlist['2j1t']*cutlist['presel_mu_no_rms']*Cuts.top_mass_sig
plot_defs['2j1t_rmsLj_rmsOff']['estQcd'] = '2j1t'

#2j1t eta lj
plot_defs['2j1t_etaLj_rmsOff'] = cp(plot_defs['2j0t_rmsLj_rmsOff'])
plot_defs['2j1t_etaLj_rmsOff']['elecut'] = cutlist['2j1t']*cutlist['presel_ele_no_rms']*Cuts.top_mass_sig
plot_defs['2j1t_etaLj_rmsOff']['mucut'] = cutlist['2j1t']*cutlist['presel_mu_no_rms']*Cuts.top_mass_sig
plot_defs['2j1t_etaLj_rmsOff']['estQcd'] = '2j1t'
plot_defs['2j1t_etaLj_rmsOn'] = cp(plot_defs['2j1t_etaLj_rmsOff'])
plot_defs['2j1t_etaLj_rmsOn']['mucut'] *= Cuts.rms_lj
plot_defs['2j1t_etaLj_rmsOn']['elecut'] *= Cuts.rms_lj

#-----------------------------------------------
# polarization.tex
#-----------------------------------------------

#-----------------------------------------------
# control.tex
#-----------------------------------------------
nbins_final = 20
plot_defs['final_cosTheta']={
    'tags': ["an", "control.tex"],
    'enabled': True,
    'var': 'cos_theta',
    'range': [nbins_final, -1, 1],
    'iso': True,
    'estQcd': 'final_2j1t',
    'gev': False,
    'log': False,
    'xlab': varnames["cos_theta"],
    'labloc': 'top-left',
    'elecut': cutlist['2j1t']*cutlist['final_ele'],
    'mucut': cutlist['2j1t']*cutlist['final_mu'],
    'dir': "control"
}


plot_defs['final_topMass']={
    'tags': ["an", "control.tex"],
    'enabled': True,
    'var': 'top_mass',
    'range': [nbins_final, 130, 220],
    'iso': True,
    'estQcd': 'final_2j1t',
    'gev': True,
    'log': False,
    'xlab': varnames["top_mass"],
    'labloc': 'top-right',
    'elecut': cutlist['2j1t']*cutlist['final_ele'],
    'mucut': cutlist['2j1t']*cutlist['final_mu'],
    'dir': "control"
}

plot_defs['final_etaLj']={
    'tags': ["an", "control.tex"],
    'enabled': True,
    'var': 'abs(eta_lj)',
    'range': [nbins_final, 2.5, 5],
    'iso': True,
    'estQcd': 'final_2j1t',
    'gev': False,
    'log': False,
    'xlab': varnames["eta_lj"],
    'labloc': 'top-right',
    'elecut': cutlist['2j1t']*cutlist['final_ele'],
    'mucut': cutlist['2j1t']*cutlist['final_mu'],
    'dir': "control"
}

#Create the final plots with after fitting
plot_defs['final_etaLj_fit'] = cp(plot_defs['final_etaLj'])
plot_defs['final_etaLj_fit']['fitpars'] = fitpars['final_2j1t_cut']
plot_defs['final_topMass_fit'] = cp(plot_defs['final_topMass'])
plot_defs['final_topMass_fit']['fitpars'] = fitpars['final_2j1t_cut']
plot_defs['final_cosTheta_fit'] = cp(plot_defs['final_cosTheta'])
plot_defs['final_met_fit']={
    'tags': ["an", "control.tex", "mva"],
    'enabled': True,
    'var': 'met',
    'range': [20, 40, 200],
    'iso': True,
    'estQcd': 'final_2j1t',
    'gev': True,
    'log': False,
    'xlab': varnames["met"],
    'labloc': 'top-right',
    'fitpars': fitpars['final_2j1t_cut'],
    'elecut': plot_defs['final_etaLj_fit']['elecut'],
    'mucut': plot_defs['final_etaLj_fit']['mucut']
}
plot_defs['final_cosTheta_fit']['fitpars'] = fitpars['final_2j1t_cut']


plot_defs['final_BDT']={
    'tags': ["an", "control.tex", "mva"],
    'enabled': True,
    'var': 'mva_BDT',
    'range': [40, -1, 1],
    'iso': True,
    'estQcd': 'presel',
    'gev': False,
    'log': True,
    'xlab': varnames["BDT_uncat"],
    'labloc': 'top-right',
    'elecut': cutlist['2j1t']*cutlist['final_ele'],
    'mucut': cutlist['2j1t']*cutlist['final_mu'],
    'dir': "control"
}

plot_defs['final_BDT_fit'] = cp(plot_defs['final_BDT'])
plot_defs['final_BDT_fit']['dir'] = fitpars['final_2j1t_mva']


plot_defs['final_cosTheta_mva_loose']={
    'tags': ["an", "control.tex", "mva"],
    'enabled': True,
    'var': 'cos_theta',
    'range': [20,-1,1],
    'iso': True,
    'estQcd': 'presel',
    'gev': False,
    'log': False,
    'xlab': varnames["cos_theta"],
    'labloc': 'top-left',
    'elecut': cutlist['2j1t']*cutlist['presel_ele']*cutlist['bdt_ele_loose'],
    'mucut': cutlist['2j1t']*cutlist['presel_mu']*cutlist['bdt_mu_loose'],
    'dir': "control"
}


plot_defs['final_met_mva_loose_fit']={
    'tags': ["an", "control.tex", "mva"],
    'enabled': True,
    'var': 'met',
    'range': [20, 0, 200],
    'iso': True,
    'estQcd': 'presel',
    'gev': True,
    'log': False,
    'xlab': varnames["met"],
    'labloc': 'top-right',
    'fitpars': fitpars['final_2j1t_mva'],
    'elecut': cutlist['2j1t']*cutlist['presel_ele']*cutlist['bdt_ele_loose'],
    'mucut': cutlist['2j1t']*cutlist['presel_mu']*cutlist['bdt_mu_loose'],
    'dir': "control"
}

plot_defs['final_cosTheta_mva_tight'] = cp(plot_defs['final_cosTheta_mva_loose'])
plot_defs['final_cosTheta_mva_tight']['elecut'] = cutlist['2j1t']*cutlist['presel_ele']*cutlist['bdt_ele_tight']
plot_defs['final_cosTheta_mva_tight']['mucut'] = cutlist['2j1t']*cutlist['presel_mu']*cutlist['bdt_mu_tight']

plot_defs['final_cosTheta_mva_tight_fit'] = cp(plot_defs['final_cosTheta_mva_tight'])
plot_defs['final_cosTheta_mva_tight_fit']['fitpars'] = fitpars['final_2j1t_mva']

plot_defs['final_cosTheta_mva_loose_fit'] = cp(plot_defs['final_cosTheta_mva_loose'])
plot_defs['final_cosTheta_mva_loose_fit']['fitpars'] = fitpars['final_2j1t_mva']

extranges = {
    "cosTheta": [nbins_final, -1, 1],
    "topMass": [nbins_final, 100, 350],
    "etaLj": [nbins_final, 0, 5],
    "BDT": [40, -1, 1],
}

#Generate all the control plots
for v in ["cosTheta", "topMass", "etaLj", "BDT"]:
    for nj in [2, 3]:
        for nt in ["no", 0,1,2]:

            #we already have this
            if nj==2 and nt==1:
                continue
            if nj==nt: #no need for plots like that
                continue

            if nt == "no": #without tagging requirement
                s = "%dj" % nj
            else:
                s = "%dj%dt" % (nj, nt)

            plot_defs[s + "_" + v] = cp(plot_defs['final_' + v])
            plot_defs[s + "_" + v]["range"] = extranges[v]
            plot_defs[s + "_" + v]['elecut'] = cutlist["presel_ele"]*cutlist[s]*Cuts.met#*cutlist['final_ele']
            plot_defs[s + "_" + v]['mucut'] = cutlist["presel_mu"]*cutlist[s]*Cuts.mt_mu#*cutlist['final_mu']
            plot_defs[s + "_" + v]['estQcd'] = "final_" + s
