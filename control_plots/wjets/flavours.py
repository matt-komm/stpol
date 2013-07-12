import ROOT
from plots.common.sample import Sample
from plots.common.cuts import Cuts
from root_numpy import tree2rec
import os

basedir = os.environ["STPOL_DIR"] + "/data"
datadirs = dict()
datadirs["iso"] = "/".join((basedir, "out_step3_joosep_11_07_19_44", "mu" ,"iso", "nominal"))

def get_hf_frac(name, cut):

	samp = Sample.fromFile(datadirs["iso"] + "/" + name)
	arr = tree2rec(samp.tree, ["gen_flavour_bj", "gen_flavour_lj"], str(cut))

	counts = dict()
	counts["WbX"] = 0.0
	counts["Wbb"] = 0.0
	counts["WXX"] = 0.0
	for i in arr:
		flavours = [abs(i["gen_flavour_bj"]), abs(i["gen_flavour_lj"])]
		if 5 in flavours:
			counts["WbX"] += 1.0
		if flavours[0]==5 and flavours[1]==5:
			counts["Wbb"] += 1.0
		counts["WXX"] += 1.0
	return counts["WbX"] / counts["WXX"]

if __name__=="__main__":

	cut = Cuts.final(2,0)
	samps = [
		"W1Jets_exclusive.root", "W2Jets_exclusive.root", "W3Jets_exclusive.root", "W4Jets_exclusive.root",
		#"WJets_sherpa_nominal.root",
		"WJets_inclusive.root",
		#"TTJets_MassiveBinDECAY.root",
		#"T_t_ToLeptons.root",
	]
	for s in samps:
		print s, get_hf_frac(s, cut)
