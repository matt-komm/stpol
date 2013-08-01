import ROOT
from plots.common.data_mc import data_mc_plot
from plots.common.sample import Sample
from plots.common.cuts import Weights, Cut, Cuts
from plots.common.utils import PhysicsProcess, get_file_list
import plots.common.plot_defs
import MVA2.common

cutlist = plots.common.plot_defs.cutlist
varnames = plots.common.plot_defs.varnames

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
    'elecut': cutlist['2j1t']*Cuts.lepton_veto*Cuts.pt_jet*Cuts.one_electron*Cuts.rms_lj*Cut('mva_BDT_all_mu_Mario>0.154'),
    'mucut': cutlist['2j1t']*Cuts.lepton_veto*Cuts.pt_jet*Cuts.one_muon*Cuts.rms_lj*Cut('mva_BDT_all_mu_Mario>0.154')
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

from plots.common.tdrstyle import tdrstyle
tdrstyle()

canv, merged_hists, htot_mc, htot_data = data_mc_plot(samples, plot_def, name, lepton_channel, lumi, weight, merge_cmds)

img = ROOT.TImage.Create()
img.FromPad(canv)
img.WriteImage(name+".png")




