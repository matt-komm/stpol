import sys

import ROOT

from mvalib.train import MVATrainer

trainoptions = "!H:!V:NTrees=2000:BoostType=Grad:Shrinkage=0.1:!UseBaggedGrad:nCuts=2000:nEventsMin=100:NNodesMax=5:"\
               "UseNvars=4:PruneStrength=5:PruneMethod=CostComplexity:MaxDepth=6"

def name(varlist):
	return '__'.join(varlist)

def train(lept, varlist):
	trainer = MVATrainer("trees/prepared_{0}.root".format(lept), ofName = "trees/trained_{0}_BDT__{1}.root".format(lept, name(varlist)), jobname=name(varlist))
	for var in varlist:
		trainer.add_variable(var)
	trainer.book_method("BDT", "BDT__" + name(varlist), trainoptions)
	trainer.get_factory().TrainAllMethods()
	trainer.evaluate()
	trainer.pack()
	trainer.finish()

cuteff = {}
cuteff['ele'] = 0.25983790132790596
cuteff['mu']  = 0.287744526372574

def find_score(lept, method_name):
	print "finding score ({0}) for {1}".format(lept, method_name)
	f = ROOT.TFile("trees/trained_{0}_{1}.root".format(lept, method_name))
	roc = f.Get("Method_BDT/{0}/MVA_{0}_rejBvsS".format(method_name)) #type = ROOT::TH1D
	score = roc.GetBinContent(roc.GetXaxis().FindBin(cuteff[lept]))
	f.Close()
	return score

def find_ranking(lept, varlist):
	score = {}
	train(lept, varlist)
	score[name(varlist)] = find_score(lept, "BDT__" + name(varlist))
	for var in varlist:
		newlist = list(varlist)
		newlist.remove(var)
		train(lept, newlist)
		score[name(newlist)] = find_score(lept, "BDT__" + name(newlist))
		if score[name(newlist)] > score[name(varlist)]:
			return find_ranking(lept, newlist)
	return score

varlist = {}
varlist['ele'] = ['top_mass', 'eta_lj', 'C', 'met', 'mt_el', 'mass_bj', 'mass_lj', 'el_pt', 'pt_bj']
varlist['mu']  = ['top_mass', 'eta_lj', 'C', 'met', 'mt_mu', 'mass_bj', 'mass_lj', 'mu_pt', 'pt_bj']

def main(args):
	if len(args) > 1:
		if args[1] != "mu" and args[1] != "ele":
			print "please specify lepton channel as an argument {mu|ele}"
			return
		lept = args[1]
		scores = find_ranking(lept, varlist[lept])
		print '{ ',
		for vars in sorted(scores, key=scores.get, reverse=True):
			print vars, ':', scores[vars], '\n  ',
		print '}'
	else:
		print "please specify lepton channel as an argument {mu|ele}"
		return

if __name__ == "__main__":
	main(sys.argv)


