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
cutlist['noeta_ele']=cutlist['presel_ele']*Cuts.top_mass_sig*Cuts.met
cutlist['noeta_mu']=cutlist['presel_mu']*Cuts.top_mass_sig*Cuts.mt_mu
cutlist['final_ele']=cutlist['nomet_ele']*Cuts.met
cutlist['final_mu']=cutlist['nomt_mu']*Cuts.mt_mu

qcdScale={}
qcdScale['ele']={}
qcdScale['ele']['final']=0.83
qcdScale['ele']['nomet']=1.33
qcdScale['ele']['presel']=1.33
qcdScale['ele']['2j0t']=1.37
qcdScale['ele']['3j1t']=0.26
qcdScale['mu']={}
qcdScale['mu']['final']=28
qcdScale['mu']['nomet']=28
qcdScale['mu']['presel']=27.9
qcdScale['mu']['2j0t']=2.46
qcdScale['mu']['3j1t']=0.28

plot_defs={}

plot_defs['top_mass']={
    'enabled': True,
    'var': 'top_mass',
    'range': [20, 50, 500],
    'iso': True,
    'estQcd': 'final',
    'gev': True,
    'log': False,
    'xlab': 'M_{b l #nu}',
    'labloc': 'top-right',
    'elecut': cutlist['2j1t']*cutlist['presel_ele']*Cuts.eta_lj*Cuts.met,
    'mucut': cutlist['2j1t']*cutlist['presel_mu']*Cuts.eta_lj*Cuts.mt_mu
}

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
    'range': [5,0,4],
    'iso': True,
    'estQcd': 'final',
    'gev': False,
    'log': True,
    'xlab': 'N_{jets}',
    'labloc': 'top-left',
    'elecut': cutlist['presel_ele']*Cuts.met,
    'mucut': cutlist['presel_mu']*Cuts.mt_mu
}

plot_defs['cos_th_2j0t']={
    'enabled': True,
    'var': 'cos_theta',
    'range': [20,-1,1],
    'iso': True,
    'estQcd': '2j0t',
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
    'estQcd': '3j1t',
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
    'estQcd': '3j1t',
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
    'xlab': 'E_{T}^{miss} / M_{tW} [GeV]',
    'labloc': 'top-right',
    'elecut': cutlist['2j1t']*cutlist['nomet_ele'],
    'mucut': cutlist['2j1t']*cutlist['nomt_mu']
}

plot_defs['mt_mu']={
    'enabled': True,
    'var': 'mt_mu',
    'range': [40,0,200],
    'iso': True,
    'estQcd': 'nomet',
    'gev': True,
    'log': False,
    'xlab': 'M_{t}(W) [GeV]',
    'labloc': 'top-right',
    'elecut': cutlist['2j1t']*cutlist['nomet_ele'],
    'mucut': cutlist['2j1t']*cutlist['nomt_mu']
}

plot_defs['mt_mu_final']={
    'enabled': True,
    'var': 'mt_mu',
    'range': [40,50,200],
    'iso': True,
    'estQcd': 'final',
    'gev': True,
    'log': False,
    'xlab': 'M_{t}(W) [GeV]',
    'labloc': 'top-right',
    'elecut': cutlist['2j1t']*cutlist['final_ele'],
    'mucut': cutlist['2j1t']*cutlist['final_mu']
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
    'xlab': '|#eta| of the light jet',
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
    'xlab': '|#eta| of the light jet',
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
    'xlab': '|#eta| of the light jet',
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
    'xlab': 'Uncategorized BDT',
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
    'xlab': 'cos #theta',
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
    'xlab': 'cos #theta',
    'labloc': 'top-left',
    'elecut': cutlist['2j1t']*cutlist['presel_ele']*Cut('mva_BDT>0.7'),
    'mucut': cutlist['2j1t']*cutlist['presel_mu']*Cut('mva_BDT>0.5')
}

