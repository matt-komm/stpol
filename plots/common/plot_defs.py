from plots.common.cuts import Cuts,Cut
import copy
cp = copy.deepcopy

cutlist={}
cutlist['2j1t']=Cuts.n_jets(2)*Cuts.n_tags(1)
cutlist['2j0t']=Cuts.n_jets(2)*Cuts.n_tags(0)
cutlist['3j0t']=Cuts.n_jets(3)*Cuts.n_tags(0)
cutlist['3j1t']=Cuts.n_jets(3)*Cuts.n_tags(1)
cutlist['3j2t']=Cuts.n_jets(3)*Cuts.n_tags(2)


#Needed for RMS cut validation
cutlist['presel_ele_no_rms']=Cuts.lepton_veto*Cuts.pt_jet*Cuts.one_electron
cutlist['presel_mu_no_rms']=Cuts.lepton_veto*Cuts.pt_jet*Cuts.one_muon

cutlist['presel_ele'] = cutlist['presel_ele_no_rms']*Cuts.rms_lj
cutlist['presel_mu'] = cutlist['presel_mu_no_rms']*Cuts.rms_lj

cutlist['nomet_ele']=cutlist['presel_ele']*Cuts.top_mass_sig*Cuts.eta_lj
cutlist['nomt_mu']=cutlist['presel_mu']*Cuts.top_mass_sig*Cuts.eta_lj
cutlist['noeta_ele']=cutlist['presel_ele']*Cuts.top_mass_sig*Cuts.met
cutlist['noeta_mu']=cutlist['presel_mu']*Cuts.top_mass_sig*Cuts.mt_mu
cutlist['final_ele']=cutlist['nomet_ele']*Cuts.met
cutlist['final_mu']=cutlist['nomt_mu']*Cuts.mt_mu

qcdScale={}
qcdScale['ele']={}
qcdScale['mu']={}

#Better to organize like this, so logical cutstrings are close by
qcdScale['ele']['final']         =   0.83
qcdScale['mu']['final']          =   28

qcdScale['ele']['final_2j0t']    =   0
qcdScale['mu']['final_2j0t']     =   0

qcdScale['ele']['final_3j0t']    =   0
qcdScale['mu']['final_3j0t']     =   0

qcdScale['ele']['final_3j1t']    =   0
qcdScale['mu']['final_3j1t']     =   0

qcdScale['ele']['final_3j2t']    =   0
qcdScale['mu']['final_3j2t']     =   0

qcdScale['ele']['nomet']         =   1.33
qcdScale['mu']['nomet']          =   28
qcdScale['ele']['presel']        =   1.33
qcdScale['mu']['presel']         =   27.9

qcdScale['ele']['2j0t']          =   1.37
qcdScale['mu']['2j0t']           =   2.46
qcdScale['ele']['2j1t']          =   0 #FIXME
qcdScale['mu']['2j1t']           =   0 #FIXME
qcdScale['ele']['3j1t']          =   0.26
qcdScale['mu']['3j1t']           =   0.28

plot_defs={}

#Set the variable names centrally so that you don't have to do find/replace if you want to change one of them and have them propagate to all the relevant plots
varnames = dict()
varnames["cos_theta"] = 'cos #theta'
varnames["eta_lj"] = "#eta of the light jet"
#varnames["abs_eta_lj"] = "|#eta| of the light jet"
varnames["abs_eta_lj"] = "|#eta_{lj}|" #Like it is in the AN
varnames["top_mass"] = 'M_{b l #nu} [GeV]'
varnames["mt_mu"] = 'M_{t}(W) [GeV]'
varnames["met"] = 'E_{T}^{miss} [GeV]'
varnames["pt_lep"] = ['e p_{T} [GeV]', '#mu p_{T} [GeV]']
varnames["BDT_uncat"] = 'Uncategorized BDT'
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
    'estQcd': 'final',
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
    'estQcd': 'nomet',
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
    'estQcd': 'final',
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

plot_defs['cos_th_mva_loose']={
    'enabled': True,
    'var': 'cos_theta',
    'range': [20,-1,1],
    'iso': True,
    'estQcd': 'final',
    'gev': False,
    'log': False,
    'xlab': varnames["cos_theta"],
    'labloc': 'top-left',
    'elecut': cutlist['2j1t']*cutlist['presel_ele']*Cut('mva_BDT>0.38'),
    'mucut': cutlist['2j1t']*cutlist['presel_mu']*Cut('mva_BDT>0.32')
}


plot_defs['cos_th_mva_tight']={
    'enabled': True,
    'var': 'cos_theta',
    'range': [20,-1,1],
    'iso': True,
    'estQcd': 'final',
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
    'range': [nbins_selection, 50, 500],
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
    'estQcd': 'final',
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
    'estQcd': 'final',
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
    'estQcd': 'final',
    'gev': False,
    'log': False,
    'xlab': varnames["eta_lj"],
    'labloc': 'top-right',
    'elecut': cutlist['2j1t']*cutlist['final_ele'],
    'mucut': cutlist['2j1t']*cutlist['final_mu'],
    'dir': "control"
}
extranges = {
    "cosTheta": [nbins_final, -1, 1],
    "topMass": [nbins_final, 50, 350],
    "etaLj": [nbins_final, 0, 5],
}

#Generate all the control plots
for v in ["cosTheta", "topMass", "etaLj"]:
    for nj in [2, 3]:
        for nt in [0,1,2]:

            #we already have this
            if nj==2 and nt==1:
                continue
            if nj==nt: #no need for that
                continue

            s = "%dj%dt" % (nj, nt)

            plot_defs[s + "_" + v] = cp(plot_defs['final_' + v])
            plot_defs[s + "_" + v]["range"] = extranges[v]
            plot_defs[s + "_" + v]['elecut'] = cutlist["presel_ele"]*cutlist[s]*Cuts.met#*cutlist['final_ele']
            plot_defs[s + "_" + v]['mucut'] = cutlist["presel_mu"]*cutlist[s]*Cuts.mt_mu#*cutlist['final_mu']
            plot_defs[s + "_" + v]['estQcd'] = "final_" + s
