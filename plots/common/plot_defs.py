from plots.common.cuts import Cuts,Cut
import copy
from plots.common.utils import PhysicsProcess, NestedDict

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

mva_var = {}
mva_var['ele']='mva_BDT_with_top_mass_C_eta_lj_el_pt_mt_el_pt_bj_mass_bj_met_mass_lj'
mva_var['mu']='mva_BDT_with_top_mass_eta_lj_C_mu_pt_mt_mu_met_mass_bj_pt_bj_mass_lj'


bdt = NestedDict()
bdt['mu']['loose'] = 0.06
bdt['mu']['tight'] = 0.6
bdt['ele']['loose'] = 0.13
bdt['ele']['tight'] = 0.6
bdt = bdt.as_dict()
cutlist['bdt_mu_loose'] = Cuts.mt_mu*Cut('%s>%f' % (mva_var['mu'],bdt['mu']['loose']))
cutlist['bdt_ele_loose'] = Cuts.met*Cut('%s>%f' % (mva_var['ele'],bdt['ele']['loose']))
cutlist['bdt_mu_tight'] = Cuts.mt_mu*Cut('%s>%f' % (mva_var['mu'],bdt['mu']['tight']))
cutlist['bdt_ele_tight'] = Cuts.met*Cut('%s>%f' % (mva_var['ele'],bdt['ele']['tight']))

#Load the scale factors externally for better factorisation
from plots.fit_scale_factors import fitpars
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

#plot_defs['lep_pt']={
#    'enabled': True,
#    'var': ['el_pt', 'mu_pt'],
#    'range': [35, 25, 200],
#    'iso': True,
#    'estQcd': False,
#    'gev': True,
#    'log': True,
#    'xlab': varnames["pt_lep"],
#    'labloc': 'top-right',
#    'elecut': cutlist['presel_ele'],
#    'mucut': cutlist['presel_mu']
#}
#
#
#plot_defs['dr_bj']={
#    'enabled': True,
#    'var': 'deltaR_bj',
#    'range': [20,0,5],
#    'iso': True,
#    'estQcd': 'final_2j1t',
#    'gev': False,
#    'log': False,
#    'xlab': '#delta R(l,b)',
#    'labloc': 'top-left',
#    'elecut': cutlist['2j1t']*cutlist['final_ele'],
#    'mucut': cutlist['2j1t']*cutlist['final_mu']
#}
#
#plot_defs['n_jets']={
#    'enabled': True,
#    'var': 'n_jets',
#    'range': [3,0.5,3.5],
#    'iso': True,
#    'estQcd': False,
#    'gev': False,
#    'log': True,
#    'xlab': varnames["n_jets"],
#    'labloc': 'top-left',
#    'elecut': cutlist['presel_ele'],
#    'mucut': cutlist['presel_mu']
#}
#
#plot_defs['n_tags']={
#        'enabled': True,
#        'var': 'n_tags',
#        'range': [3,-0.5,2.5],
#        'iso': True,
#        'estQcd': False,
#        'gev': False,
#        'log': True,
#        'xlab': varnames["n_tags"],
#        'labloc': 'top-right',
#        'elecut': cutlist['presel_ele']*Cut('n_jets==2'),
#        'mucut': cutlist['presel_mu']*Cut('n_jets==2')
#}
#
#plot_defs['n_tags_3j']={
#        'enabled': True,
#        'var': 'n_tags',
#        'range': [4,-0.5,3.5],
#        'iso': True,
#        'estQcd': False,
#        'gev': False,
#        'log': True,
#        'xlab': varnames["n_tags"],
#        'labloc': 'top-right',
#        'elecut': cutlist['presel_ele']*Cut('n_jets==3'),
#        'mucut': cutlist['presel_mu']*Cut('n_jets==3')
#}
#
#plot_defs['cos_th_2j0t']={
#    'enabled': True,
#    'var': 'cos_theta',
#    'range': [20,-1,1],
#    'iso': True,
#    'estQcd': '2j0t',
#    'gev': False,
#    'log': False,
#    'xlab': varnames["cos_theta"],
#    'labloc': 'top-left',
#    'elecut': cutlist['2j0t']*cutlist['final_ele'],
#    'mucut': cutlist['2j0t']*cutlist['final_mu']
#}
#
#plot_defs['cos_th_3j1t']={
#    'enabled': True,
#    'var': 'cos_theta',
#    'range': [20,-1,1],
#    'iso': True,
#    'estQcd': '3j1t',
#    'gev': False,
#    'log': False,
#    'xlab': varnames["cos_theta"],
#    'labloc': 'top-left',
#    'elecut': cutlist['3j1t']*cutlist['final_ele'],
#    'mucut': cutlist['3j1t']*cutlist['final_mu']
#}
#
#plot_defs['cos_th_3j2t']={
#    'enabled': True,
#    'var': 'cos_theta',
#    'range': [20,-1,1],
#    'iso': True,
#    'estQcd': '3j1t',
#    'gev': False,
#    'log': False,
#    'xlab': varnames["cos_theta"],
#    'labloc': 'top-left',
#    'elecut': cutlist['3j2t']*cutlist['final_ele'],
#    'mucut': cutlist['3j2t']*cutlist['final_mu']
#}
#
#plot_defs['cos_th_nomet']={
#    'enabled': True,
#    'var': 'cos_theta',
#    'range': [20,-1,1],
#    'iso': True,
#    'estQcd': 'final_2j1t_nomtcut',
#    'gev': False,
#    'log': False,
#    'xlab': varnames["cos_theta"],
#    'labloc': 'top-left',
#    'elecut': cutlist['2j1t']*cutlist['nomet_ele'],
#    'mucut': cutlist['2j1t']*cutlist['nomt_mu']
#}
#
#plot_defs['met']={
#    'enabled': True,
#    'var': 'met',
#    'range': [40,0,200],
#    'iso': True,
#    'estQcd': '2j1t_nomtcut',
#    'gev': True,
#    'log': False,
#    'xlab': varnames["met"],
#    'labloc': 'top-right',
#    'elecut': cutlist['2j1t']*cutlist['presel_ele'],
#    'mucut': cutlist['2j1t']*cutlist['presel_mu']
#}
#
#plot_defs['met_BDT']=cp(plot_defs['met'])
#plot_defs['met_BDT']['estQcd']='2j1t'
#plot_defs['met_BDT']['elecut']*=Cuts.met
#plot_defs['met_BDT']['mucut']*=Cuts.mt_mu
#plot_defs['met_BDT']['fitpars'] = fitpars['final_2j1t']
#
#
#plot_defs['met_final']={
#    'enabled': True,
#    'var': 'met',
#    'range': [40,0,200],
#    'iso': True,
#    'estQcd': 'presel',
#    'gev': True,
#    'log': False,
#    'xlab': varnames["met"],
#    'labloc': 'top-right',
#    'elecut': cutlist['2j1t']*cutlist['presel_ele']*Cuts.top_mass_sig*Cuts.eta_lj,
#    'mucut': cutlist['2j1t']*cutlist['presel_mu']*Cuts.top_mass_sig*Cuts.eta_lj
#}
#
#plot_defs['mtW']={
#    'enabled': True,
#    'var': ['mt_el','mt_mu'],
#    'range': [40,0,200],
#    'iso': True,
#    'estQcd': '2j1t_nomtcut',
#    'gev': True,
#    'log': False,
#    'xlab': varnames["mt_mu"],
#    'labloc': 'top-right',
#    'elecut': cutlist['2j1t']*cutlist['presel_ele'],
#    'mucut': cutlist['2j1t']*cutlist['presel_mu']
#}
#
#plot_defs['mtW_final']={
#    'enabled': True,
#    'var': ['mt_el','mt_mu'],
#    'range': [40,0,200],
#    'iso': True,
#    'estQcd': '2j1t_final',
#    'gev': True,
#    'log': False,
#    'xlab': varnames["mt_mu"],
#    'labloc': 'top-right',
#    'elecut': cutlist['2j1t']*cutlist['presel_ele']*Cuts.top_mass_sig*Cuts.eta_lj,
#    'mucut': cutlist['2j1t']*cutlist['presel_mu']*Cuts.top_mass_sig*Cuts.eta_lj
#}
#
#plot_defs['abs_eta_lj']={
#    'enabled': True,
#    'var': 'abs(eta_lj)',
#    'range': [50,0,5],
#    'iso': True,
#    'estQcd': 'final_2j1t',
#    'gev': False,
#    'log': False,
#    'xlab': varnames["eta_lj"],
#    'labloc': 'top-right',
#    'elecut': cutlist['2j1t']*cutlist['noeta_ele'],
#    'mucut': cutlist['2j1t']*cutlist['noeta_mu']
#}
#
#plot_defs['abs_eta_lj_2j0t']={
#    'enabled': True,
#    'var': 'abs(eta_lj)',
#    'range': [50,0,5],
#    'iso': True,
#    'estQcd': '2j0t',
#    'gev': False,
#    'log': False,
#    'xlab': varnames["eta_lj"],
#    'labloc': 'top-right',
#    'elecut': cutlist['2j0t']*cutlist['noeta_ele'],
#    'mucut': cutlist['2j0t']*cutlist['noeta_mu']
#}
#
#plot_defs['abs_eta_lj_3j1t']={
#    'enabled': True,
#    'var': 'abs(eta_lj)',
#    'range': [50,0,5],
#    'iso': True,
#    'estQcd': '3j1t',
#    'gev': False,
#    'log': False,
#    'xlab': varnames["eta_lj"],
#    'labloc': 'top-right',
#    'elecut': cutlist['3j1t']*cutlist['noeta_ele'],
#    'mucut': cutlist['3j1t']*cutlist['noeta_mu']
#}
#
#plot_defs['abs_eta_lj_3j2t']={
#    'enabled': True,
#    'var': 'abs(eta_lj)',
#    'range': [50,0,5],
#    'iso': True,
#    'estQcd': '3j1t',
#    'gev': False,
#    'log': False,
#    'xlab': varnames["eta_lj"],
#    'labloc': 'top-right',
#    'elecut': cutlist['3j2t']*cutlist['noeta_ele'],
#    'mucut': cutlist['3j2t']*cutlist['noeta_mu']
#}


#-----------------------------------------------
# mva.tex
#-----------------------------------------------

plot_defs['mva_bdt'] = {
    'enabled': True,
    'var': [mva_var['ele'],mva_var['mu']],
    'range': [40,-1,1],
    'iso': True,
    'estQcd': '2j1t',
    'gev': False,
    'log': True,
    'xlab': varnames["BDT_uncat"],
    'labloc': 'top-right',
    'elecut': cutlist['2j1t']*cutlist['presel_ele']*Cuts.met,
    'mucut': cutlist['2j1t']*cutlist['presel_mu']*Cuts.mt_mu,
    #'cutname': '2J1T',
    'dir': 'BDT'
}
plot_defs['mva_bdt_fit'] = cp(plot_defs['mva_bdt'] )
plot_defs['mva_bdt_fit']['fitpars'] = fitpars['final_2j1t_mva']

plot_defs['mva_shape'] = cp(plot_defs['mva_bdt'])
plot_defs['mva_shape']['normalize'] = True
plot_defs['mva_shape']['log'] = False

plot_defs['mva_shape_log'] = cp(plot_defs['mva_shape'])
plot_defs['mva_shape_log']['log'] = True

plot_defs['mva_bdt_zoom']=cp(plot_defs['mva_bdt'])
plot_defs['mva_bdt_zoom']['range']=[50,0,1]
plot_defs['mva_bdt_zoom']['log']=False

plot_defs['mva_bdt_zoom_fit'] = cp(plot_defs['mva_bdt_zoom'] )
plot_defs['mva_bdt_zoom_fit']['fitpars'] = fitpars['final_2j1t_mva']

#-----------------------------------------------
# BDT input variables before/after cut
#-----------------------------------------------

plot_defs['invar_top_mass'] = {
        'tags': ['invars', 'mva'],
        'enabled': True,
        'var': 'top_mass',
        'range': [30,0,300],
        'iso': True,
        'estQcd': '2j1t',
        'gev': True,
        'log': False,
        'xlab': varnames['top_mass'],
        'labloc': 'top-right',
        'elecut': cutlist['2j1t']*cutlist['presel_ele']*Cuts.met,
        'mucut': cutlist['2j1t']*cutlist['presel_mu']*Cuts.mt_mu,
        #'cutname': '2J1T',
        'dir': 'BDT'
}

plot_defs['invar_C'] = cp(plot_defs['invar_top_mass'])
plot_defs['invar_C']['var']='C'
plot_defs['invar_C']['range']=[50,0,1]
plot_defs['invar_C']['gev']=False
plot_defs['invar_C']['xlab']='C'

plot_defs['invar_eta_lj'] = cp(plot_defs['invar_C'])
plot_defs['invar_eta_lj']['var']='eta_lj'
plot_defs['invar_eta_lj']['range']=[50,0,5]
plot_defs['invar_eta_lj']['xlab']=varnames['eta_lj']

plot_defs['invar_lep_pt'] = cp(plot_defs['invar_top_mass'])
plot_defs['invar_lep_pt']['var']=['el_pt','mu_pt']
plot_defs['invar_lep_pt']['range']=[35,25,200]
plot_defs['invar_lep_pt']['xlab']=varnames['pt_lep']
plot_defs['invar_lep_pt']['log']=True

plot_defs['invar_mtW'] = cp(plot_defs['invar_top_mass'])
plot_defs['invar_mtW']['var']=['mt_el','mt_mu']
plot_defs['invar_mtW']['range']=[40,0,200]
plot_defs['invar_mtW']['xlab']=varnames['mt_mu']

plot_defs['invar_met'] = cp(plot_defs['invar_top_mass'])
plot_defs['invar_met']['var']='met'
plot_defs['invar_met']['range']=[40,0,200]
plot_defs['invar_met']['xlab']=varnames['met']

plot_defs['invar_pt_bj'] = cp(plot_defs['invar_lep_pt'])
plot_defs['invar_pt_bj']['var'] = 'pt_bj'
plot_defs['invar_pt_bj']['xlab'] = 'b-jet p_{T} [GeV]'

plot_defs['invar_mass_bj'] = cp(plot_defs['invar_top_mass'])
plot_defs['invar_mass_bj']['var'] = 'mass_bj'
plot_defs['invar_mass_bj']['range'] = [40,0,200]
plot_defs['invar_mass_bj']['xlab'] = 'm_{b-jet} [GeV]'

plot_defs['invar_mass_lj'] = cp(plot_defs['invar_mass_bj'])
plot_defs['invar_mass_lj']['var'] = 'mass_lj'
plot_defs['invar_mass_lj']['xlab'] = 'm_{lq-jet} [GeV]'

from mvatools.sampleList import varRank 
vlist = varRank['mu']
vlist.remove('mu_pt')
vlist.remove('mt_mu')
vlist+=['lep_pt','mtW']
for v in vlist:
    plot_defs['invar_%s_bdt_loose' % v] = cp(plot_defs['invar_%s' % v])
    plot_defs['invar_%s_bdt_loose' % v]['elecut'] *=cutlist['bdt_ele_loose']
    plot_defs['invar_%s_bdt_loose' % v]['mucut'] *=cutlist['bdt_mu_loose']

    plot_defs['invar_%s_bdt_tight' % v] = cp(plot_defs['invar_%s' % v])
    plot_defs['invar_%s_bdt_tight' % v]['elecut'] *=cutlist['bdt_ele_tight']
    plot_defs['invar_%s_bdt_tight' % v]['mucut'] *=cutlist['bdt_mu_tight']

    for k in ['', '_bdt_loose', '_bdt_tight' ]:
        plot_defs['invar_%s%s_fit' % (v,k)] = cp(plot_defs['invar_%s%s' % (v,k)])
        plot_defs['invar_%s%s_fit' % (v,k)]['fitpars'] = fitpars['final_2j1t_mva']

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
    #'cutname': '2J1T',
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
    #'cutname': '2J1T',
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
    #'cutname': '2J0T',
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
    #'cutname': '2J0T',
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
    #'cutname': '2J1T signal region',
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
plot_defs['final_etaLj_fit']['fitpars'] = fitpars['final_2j1t']
plot_defs['final_topMass_fit'] = cp(plot_defs['final_topMass'])
plot_defs['final_topMass_fit']['fitpars'] = fitpars['final_2j1t']
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
    'elecut': plot_defs['final_etaLj_fit']['elecut'],
    'mucut': plot_defs['final_etaLj_fit']['mucut']
}

plot_defs['final_cosTheta_fit']['fitpars'] = fitpars['final_2j1t']

plot_defs['final_cosTheta_mva_loose'] = {
    'tags': ["an", "control.tex", "mva"],
    'enabled': True,
    'var': 'cos_theta',
    'range': [20,-1,1],
    'iso': True,
    'estQcd': '2j1t',
    'gev': False,
    'log': False,
    'xlab': varnames["cos_theta"],
    'labloc': 'top-left',
    'elecut': cutlist['2j1t']*cutlist['presel_ele']*cutlist['bdt_ele_loose'],
    'mucut': cutlist['2j1t']*cutlist['presel_mu']*cutlist['bdt_mu_loose'],
    'dir': "control",
    'cutname': {
        "mu": "BDT > %.2f" % bdt['mu']['loose'],
        "ele": "BDT > %.2f" % bdt['ele']['loose']
    }
}


plot_defs['final_met_mva_loose_fit'] = {
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
    'dir': "control",
}

plot_defs['final_met_phi_mva_loose_fit']={
    'tags': ["an", "control.tex", "mva"],
    'enabled': True,
    'var': 'phi_met',
    'range': [40, -3.2, 3.2],
    'iso': True,
    'estQcd': 'presel',
    'gev': False,
    'log': False,
    'xlab': "#phi_{MET}",
    'labloc': 'top-right',
    'fitpars': fitpars['final_2j1t_mva'],
    'elecut': cutlist['2j1t']*cutlist['presel_ele']*cutlist['bdt_ele_loose'],
    'mucut': cutlist['2j1t']*cutlist['presel_mu']*cutlist['bdt_mu_loose'],
    'dir': "control"
}

plot_defs['final_cosTheta_mva_tight'] = cp(plot_defs['final_cosTheta_mva_loose'])
plot_defs['final_cosTheta_mva_tight']['elecut'] = cutlist['2j1t']*cutlist['presel_ele']*cutlist['bdt_ele_tight']
plot_defs['final_cosTheta_mva_tight']['mucut'] = cutlist['2j1t']*cutlist['presel_mu']*cutlist['bdt_mu_tight']
plot_defs['final_cosTheta_mva_tight']['cutname'] = {
            "mu": "BDT > %.2f" % bdt['mu']['tight'],
            "ele": "BDT > %.2f" % bdt['ele']['tight']
        }

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

#PLotting the BDT variable in the cut-based signal region
plot_defs['final_BDT']={
    'tags': ["an", "control.tex", "mva"],
    'enabled': True,
    'var': [mva_var['ele'],mva_var['mu']],
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

if __name__=="__main__":
    for k in  plot_defs.keys():
        print k


# plot_defs['cos_th_mva_loose']={
#     'enabled': True,
#     'var': 'cos_theta',
#     'range': [20,-1,1],
#     'iso': True,
#     'estQcd': '2j1t', #FIXME?
#     'gev': False,
#     'log': False,
#     'xlab': varnames["cos_theta"],
#     'labloc': 'top-left',
#     'elecut': cutlist['2j1t']*cutlist['presel_ele']*Cut('mva_BDT>0.28'),
#     'mucut': cutlist['2j1t']*cutlist['presel_mu']*Cut('mva_BDT>0.24')
# }
# plot_defs['cos_th_mva_loose_fit'] = cp(plot_defs['cos_th_mva_loose'])
# plot_defs['cos_th_mva_loose_fit']['fitpars'] = fitpars['final_2j1t_mva']



# plot_defs['cos_th_mva_tight']={
#     'enabled': True,
#     'var': 'cos_theta',
#     'range': [20,-1,1],
#     'iso': True,
#     'estQcd': 'final_2j1t',
#     'gev': False,
#     'log': False,
#     'xlab': varnames["cos_theta"],
#     'labloc': 'top-left',
#     'elecut': cutlist['2j1t']*cutlist['presel_ele']*Cut('mva_BDT>0.7'),
#     'mucut': cutlist['2j1t']*cutlist['presel_mu']*Cut('mva_BDT>0.5')
# }


# plot_defs['final_BDT_prefit'] = cp(plot_defs['final_BDT'])
# plot_defs['final_BDT_prefit']['log'] = False
# plot_defs['final_BDT_fit'] = cp(plot_defs['final_BDT'])
# plot_defs['final_BDT_fit']['fitpars'] = fitpars['final_2j1t_mva']
# plot_defs['final_BDT_fit']['log'] = False
