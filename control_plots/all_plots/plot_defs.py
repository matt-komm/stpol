from plots.common.cuts import Cuts,Cut

plot_defs={}
plot_defs['cos_th_final']={
    'enabled': True,
    'var': 'cos_theta',
    'range': [20,-1,1],
    'iso': True,
    'estQcd': True,
    'gev': False,
    'log': False,
    'xlab': 'cos #theta',
    'labloc': 'top-left',
    'commonCut': Cuts.n_jets(2)*Cuts.n_tags(1)*Cuts.lepton_veto*Cuts.pt_jet*Cuts.rms_lj*Cuts.top_mass_sig*Cuts.eta_lj,
    'elecut': Cuts.one_electron*Cuts.met,
    'mucut': Cuts.one_muon*Cuts.mt_mu
}

plot_defs['cos_th_2j0t']={
    'enabled': True,
    'var': 'cos_theta',
    'range': [20,-1,1],
    'iso': True,
    'estQcd': True,
    'gev': False,
    'log': False,
    'xlab': 'cos #theta',
    'labloc': 'top-left',
     'commonCut': Cuts.n_jets(2)*Cuts.n_tags(0)*Cuts.lepton_veto*Cuts.pt_jet*Cuts.rms_lj*Cuts.top_mass_sig*Cuts.eta_lj,
    'elecut': Cuts.one_electron*Cuts.met,
    'mucut': Cuts.one_muon*Cuts.mt_mu
}

plot_defs['cos_th_3j1t']={
    'enabled': True,
    'var': 'cos_theta',
    'range': [20,-1,1],
    'iso': True,
    'estQcd': True,
    'gev': False,
    'log': False,
    'xlab': 'cos #theta',
    'labloc': 'top-left',
    'commonCut': Cuts.n_jets(3)*Cuts.n_tags(1)*Cuts.lepton_veto*Cuts.pt_jet*Cuts.rms_lj*Cuts.top_mass_sig*Cuts.eta_lj,
    'elecut': Cuts.one_electron*Cuts.met,
    'mucut': Cuts.one_muon*Cuts.mt_mu
}

plot_defs['cos_th_3j2t']={
    'enabled': True,
    'var': 'cos_theta',
    'range': [20,-1,1],
    'iso': True,
    'estQcd': True,
    'gev': False,
    'log': False,
    'xlab': 'cos #theta',
    'labloc': 'top-left',
    'commonCut': Cuts.n_jets(3)*Cuts.n_tags(2)*Cuts.lepton_veto*Cuts.pt_jet*Cuts.rms_lj*Cuts.top_mass_sig*Cuts.eta_lj,
    'elecut': Cuts.one_electron*Cuts.met,
    'mucut': Cuts.one_muon*Cuts.mt_mu
}

plot_defs['cos_th_nomet']={
    'enabled': True,
    'var': 'cos_theta',
    'range': [20,-1,1],
    'iso': True,
    'estQcd': True,
    'gev': False,
    'log': False,
    'xlab': 'cos #theta',
    'labloc': 'top-left',
    'commonCut': Cuts.n_jets(2)*Cuts.n_tags(1)*Cuts.lepton_veto*Cuts.pt_jet*Cuts.rms_lj*Cuts.top_mass_sig*Cuts.eta_lj,
    'elecut': Cuts.one_electron,
    'mucut': Cuts.one_muon
}

plot_defs['met']={
    'enabled': True,
    'var': 'met',
    'range': [20,0,100],
    'iso': True,
    'estQcd': True,
    'gev': True,
    'log': False,
    'xlab': 'E_{T}^{miss} [GeV]',
    'labloc': 'top-right',
    'commonCut': Cuts.n_jets(2)*Cuts.n_tags(1)*Cuts.lepton_veto*Cuts.pt_jet*Cuts.rms_lj*Cuts.top_mass_sig*Cuts.eta_lj,
    'elecut': Cuts.one_electron,
    'mucut': Cuts.one_muon
}

plot_defs['abs_eta_lj']={
    'enabled': True,
    'var': 'abs(eta_lj)',
    'range': [50,0,5],
    'iso': True,
    'estQcd': True,
    'gev': False,
    'log': False,
    'xlab': '|#eta| of the light jet',
    'labloc': 'top-right',
    'commonCut': Cuts.n_jets(2)*Cuts.n_tags(1)*Cuts.lepton_veto*Cuts.pt_jet*Cuts.rms_lj*Cuts.top_mass_sig,
    'elecut': Cuts.one_electron*Cuts.met,
    'mucut': Cuts.one_muon*Cuts.mt_mu
}

plot_defs['abs_eta_lj_2j0t']={
    'enabled': True,
    'var': 'abs(eta_lj)',
    'range': [50,0,5],
    'iso': True,
    'estQcd': True,
    'gev': False,
    'log': False,
    'xlab': '|#eta| of the light jet',
    'labloc': 'top-right',
    'commonCut': Cuts.n_jets(2)*Cuts.n_tags(0)*Cuts.lepton_veto*Cuts.pt_jet*Cuts.rms_lj*Cuts.top_mass_sig,
    'elecut': Cuts.one_electron*Cuts.met,
    'mucut': Cuts.one_muon*Cuts.mt_mu
}

plot_defs['abs_eta_lj_3j1t']={
    'enabled': True,
    'var': 'abs(eta_lj)',
    'range': [50,0,5],
    'iso': True,
    'estQcd': True,
    'gev': False,
    'log': False,
    'xlab': '|#eta| of the light jet',
    'labloc': 'top-right',
    'commonCut': Cuts.n_jets(3)*Cuts.n_tags(1)*Cuts.lepton_veto*Cuts.pt_jet*Cuts.rms_lj*Cuts.top_mass_sig,
    'elecut': Cuts.one_electron*Cuts.met,
    'mucut': Cuts.one_muon*Cuts.mt_mu
}

plot_defs['abs_eta_lj_3j2t']={
    'enabled': True,
    'var': 'abs(eta_lj)',
    'range': [50,0,5],
    'iso': True,
    'estQcd': True,
    'gev': False,
    'log': False,
    'xlab': '|#eta| of the light jet',
    'labloc': 'top-right',
    'commonCut': Cuts.n_jets(3)*Cuts.n_tags(2)*Cuts.lepton_veto*Cuts.pt_jet*Cuts.rms_lj*Cuts.top_mass_sig,
    'elecut': Cuts.one_electron*Cuts.met,
    'mucut': Cuts.one_muon*Cuts.mt_mu
}

plot_defs['mva_cat4']={
    'enabled': False,
    'var': 'mva_cat4',
    'range': [40,-1,1],
    'iso': True,
    'estQcd': True,
    'gev': False,
    'log': True,
    'xlab': '4-category BDT',
    'labloc': 'top-right',
    'commonCut': Cuts.n_jets(2)*Cuts.n_tags(1)*Cuts.lepton_veto*Cuts.pt_jet*Cuts.rms_lj,
    'elecut': Cuts.one_electron,
    'mucut': Cuts.one_muon
}
