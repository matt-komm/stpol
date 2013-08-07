
# This listing of base filenames describes whihc samples to use for training and which for testing
# in current iteration we use inclusive samples of signal and main backgrounds for training and then
# the exclusive samples for actual evaluation and testing

# Signal
mvaFileList={}
mvaFileList['sig']={}
mvaFileList['bg']={}
mvaFileList['sig']['train']= [
    'T_t',
    'Tbar_t'
]
mvaFileList['sig']['eval']= [
    'T_t_ToLeptons',
    'Tbar_t_ToLeptons'
]
mvaFileList['bg']['train']= [
    'TTJets_MassiveBinDECAY',
    'WJets_inclusive'
]
mvaFileList['bg']['eval']= [
    'TTJets_FullLept',
    'TTJets_SemiLept',
    'W1Jets_exclusive',
    'W2Jets_exclusive',
    'W3Jets_exclusive',
    'W4Jets_exclusive'
]

varList={}
varList['ele'] = [ 'top_mass','eta_lj','C','met','mt_el','mass_bj','mass_lj','el_pt','pt_bj' ]
varList['mu']  = [ 'top_mass','eta_lj','C','met','mt_mu','mass_bj','mass_lj','mu_pt','pt_bj' ]

varRank={}
varRank['ele'] = ['top_mass', 'C', 'eta_lj', 'el_pt', 'mt_el', 'pt_bj', 'mass_bj', 'met', 'mass_lj']
varRank['mu'] = ['top_mass', 'eta_lj', 'C', 'mu_pt', 'mt_mu', 'met', 'mass_bj', 'pt_bj', 'mass_lj']

from plots.common.cuts import Cut,Cuts

cuts = {}
cuts['ele'] = Cuts.n_jets(2)*Cuts.n_tags(1)*Cuts.hlt_isoele*Cuts.lepton_veto*Cuts.pt_jet*Cuts.one_electron*Cuts.rms_lj*Cuts.met
cuts['mu']  = Cuts.n_jets(2)*Cuts.n_tags(1)*Cuts.hlt_isomu*Cuts.lepton_veto*Cuts.pt_jet*Cuts.one_muon*Cuts.rms_lj*Cuts.mt_mu()
