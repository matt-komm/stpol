import ROOT
from plots.common.data_mc import data_mc_plot
from plots.common.sample import Sample
from plots.common.cuts import Weights, Cut, Cuts
from plots.common.utils import PhysicsProcess, get_file_list
import MVA2.common

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

cutlist['bdt_mu_tight'] = Cuts.mt_mu*Cut('mva_BDT>0.5')
cutlist['bdt_ele_tight'] = Cuts.met*Cut('mva_BDT>0.5')
cutlist['bdt_mu_loose'] = Cuts.mt_mu*Cut('mva_BDT>0.09')
cutlist['bdt_ele_loose'] = Cuts.met*Cut('mva_BDT>0.06')

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

lumis = {
    "mu": 6784+6398+5277,
    "ele":12410+6144
}

lepton_channel = "mu"
lumi = lumis[lepton_channel]
name = "antsu_plot :)"

# plot definition
plot_def={
    'enabled': True,
    'var': 'cos_theta',
    'range': [20,-1,1],
    'iso': True,
    'estQcd': 'final_2j1t',
    'gev': False,
    'log': False,
    'xlab': varnames["cos_theta"],
    'labloc': 'top-left',
    'elecut': cutlist['2j1t']*Cuts.lepton_veto*Cuts.pt_jet*Cuts.one_electron*Cut('mva_BDT_all_mu_Mario>0.154'),
    'mucut': cutlist['2j1t']*Cuts.lepton_veto*Cuts.pt_jet*Cuts.one_muon*Cut('mva_BDT_all_mu_Mario>0.154')
}

weight = Weights.total(lepton_channel)*Weights.wjets_madgraph_shape_weight()*Weights.wjets_madgraph_flat_weight()
physics_processes = PhysicsProcess.get_proc_dict(lepton_channel=lepton_channel)#Contains the information about merging samples and proper pretty names for samples
merge_cmds = PhysicsProcess.get_merge_dict(physics_processes) #The actual merge dictionary

#Get the file lists
flist = get_file_list(
	merge_cmds,
	"filled_trees_mu/"
)
if len(flist)==0:
	raise Exception("Couldn't open any files. Are you sure that %s exists and contains root files?" % args.indir)

samples={}
for f in flist:
	samples[f] = Sample.fromFile(f, tree_name='Events')

canv, merged_hists, htot_mc, htot_data = data_mc_plot(samples, plot_def, name, lepton_channel, lumi, weight, merge_cmds)

img = ROOT.TImage.Create()
img.FromPad(canv)
img.WriteImage(name+".png")




