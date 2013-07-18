from plots.common.cuts import Cuts,Cut

cutlist={}
cutlist['2j1t']=Cuts.n_jets(2)*Cuts.n_tags(1)
cutlist['2j0t']=Cuts.n_jets(2)*Cuts.n_tags(0)
cutlist['3j1t']=Cuts.n_jets(3)*Cuts.n_tags(1)
cutlist['3j2t']=Cuts.n_jets(3)*Cuts.n_tags(2)
cutlist['presel_ele']=Cuts.lepton_veto*Cuts.pt_jet*Cuts.rms_lj*Cuts.one_electron
cutlist['presel_mu']=Cuts.lepton_veto*Cuts.pt_jet*Cuts.rms_lj*Cuts.one_muon
cutlist['nomet_ele']=cutlist['presel_ele']*Cuts.top_mass_sig*Cuts.eta_lj
cutlist['nomt_mu']=cutlist['presel_mu']*Cuts.top_mass_sig*Cuts.eta_lj
cutlist['final_ele']=cutlist['nomet_ele']*Cuts.met
cutlist['final_mu']=cutlist['nomt_mu']*Cuts.mt_mu

qcdScale={}
qcdScale['ele']={}
qcdScale['ele']['final']=3.32
qcdScale['ele']['nomet']=3.32
qcdScale['ele']['presel']=4.05
qcdScale['mu']={}
qcdScale['mu']['final']=4
qcdScale['mu']['nomt']=4
qcdScale['mu']['presel']=4

plot_defs={}
plot_defs['cos_th_final']={
    'enabled': True,
    'var': 'cos_theta',
    'range': [20,-1,1],
    'iso': True,
    'estQcd': 'final',
    'gev': False,
    'log': False,
    'xlab': 'cos #theta',
    'labloc': 'top-left',
    'elecut': cutlist['2j1t']*cutlist['final_ele'],
    'mucut': cutlist['2j1t']*cutlist['final_mu']
}

plot_defs['cos_th_2j0t']={
    'enabled': True,
    'var': 'cos_theta',
    'range': [20,-1,1],
    'iso': True,
    'estQcd': 'final',
    'gev': False,
    'log': False,
    'xlab': 'cos #theta',
    'labloc': 'top-left',
    'elecut': cutlist['2j0t']*cutlist['final_ele'],
    'mucut': cutlist['2j0t']*cutlist['final_mu']
}

plot_defs['cos_th_3j1t']={
    'enabled': True,
    'var': 'cos_theta',
    'range': [20,-1,1],
    'iso': True,
    'estQcd': 'final',
    'gev': False,
    'log': False,
    'xlab': 'cos #theta',
    'labloc': 'top-left',
    'elecut': cutlist['3j1t']*cutlist['final_ele'],
    'mucut': cutlist['3j1t']*cutlist['final_mu']
}

plot_defs['cos_th_3j2t']={
    'enabled': True,
    'var': 'cos_theta',
    'range': [20,-1,1],
    'iso': True,
    'estQcd': 'final',
    'gev': False,
    'log': False,
    'xlab': 'cos #theta',
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
    'xlab': 'cos #theta',
    'labloc': 'top-left',
    'elecut': cutlist['2j1t']*cutlist['nomet_ele'],
    'mucut': cutlist['2j1t']*cutlist['nomt_mu']
}

plot_defs['met']={
    'enabled': True,
    'var': 'met',
    'range': [40,0,200],
    'iso': True,
    'estQcd': 'nomet',
    'gev': True,
    'log': False,
    'xlab': 'E_{T}^{miss} [GeV]',
    'labloc': 'top-right',
    'elecut': cutlist['2j1t']*cutlist['nomet_ele'],
    'mucut': cutlist['2j1t']*cutlist['nomt_mu']
}

plot_defs['abs_eta_lj']={
    'enabled': True,
    'var': 'abs(eta_lj)',
    'range': [50,0,5],
    'iso': True,
    'estQcd': 'final',
    'gev': False,
    'log': False,
    'xlab': '|#eta| of the light jet',
    'labloc': 'top-right',
    'elecut': cutlist['2j1t']*cutlist['final_ele'],
    'mucut': cutlist['2j1t']*cutlist['final_mu']
}

plot_defs['abs_eta_lj_2j0t']={
    'enabled': True,
    'var': 'abs(eta_lj)',
    'range': [50,0,5],
    'iso': True,
    'estQcd': 'final',
    'gev': False,
    'log': False,
    'xlab': '|#eta| of the light jet',
    'labloc': 'top-right',
    'elecut': cutlist['2j0t']*cutlist['final_ele'],
    'mucut': cutlist['2j0t']*cutlist['final_mu']
}

plot_defs['abs_eta_lj_3j1t']={
    'enabled': True,
    'var': 'abs(eta_lj)',
    'range': [50,0,5],
    'iso': True,
    'estQcd': 'final',
    'gev': False,
    'log': False,
    'xlab': '|#eta| of the light jet',
    'labloc': 'top-right',
    'elecut': cutlist['3j1t']*cutlist['final_ele'],
    'mucut': cutlist['3j1t']*cutlist['final_mu']
}

plot_defs['abs_eta_lj_3j2t']={
    'enabled': True,
    'var': 'abs(eta_lj)',
    'range': [50,0,5],
    'iso': True,
    'estQcd': 'final',
    'gev': False,
    'log': False,
    'xlab': '|#eta| of the light jet',
    'labloc': 'top-right',
    'elecut': cutlist['3j2t']*cutlist['final_ele'],
    'mucut': cutlist['3j2t']*cutlist['final_mu']
}

plot_defs['mva_cat4']={
    'enabled': False,
    'var': 'mva_cat4',
    'range': [40,-1,1],
    'iso': True,
    'estQcd': 'presel',
    'gev': False,
    'log': True,
    'xlab': '4-category BDT',
    'labloc': 'top-right',
    'elecut': cutlist['2j1t']*cutlist['presel_ele'],
    'mucut': cutlist['2j1t']*cutlist['presel_mu']
}
