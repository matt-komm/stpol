import subprocess
from plots.common.utils import *
from plots.common.sample import get_paths
import glob
from subprocess import check_call
from SingleTopPolarization.Analysis.sample_types import *

if __name__=="__main__":


	path = get_paths()
	print path.keys()
	data_repro = "Jul15"
	fnames = glob.glob(path[data_repro]["mc"]["mu"]["nominal"]["iso"] + "/*.root")
	fnames += glob.glob(path[data_repro]["data"]["mu"]["NONE"]["iso"] + "/*.root")

	ofdir = "hists/"

	cuts = [
		("SR", "n_muons==1 && n_eles==0 && n_veto_mu==0 && n_jets>0 && n_veto_ele==0 && rms_lj<0.025 && abs(eta_lj)>2.5 && top_mass<220 && top_mass>130 && mt_mu>50"),
		("SB", "n_muons==1 && n_eles==0 && n_veto_mu==0 && n_jets>0 && n_veto_ele==0 && rms_lj<0.025"),
	]

	weight = "pu_weight*b_weight_nominal*muon_IDWeight*muon_IsoWeight"
	for fn in fnames:
		sn = fn.split("/")[-1]
		of = ofdir + sn
		args = []
		if is_wjets(sn):
			args += ["--doWJetsMadgraphWeight=true"]
		if "sherpa" in sn:
			args += ["--doWJetsSherpaWeight=true"]

		if not is_mc(sn):
			args += ["--isMC=false"]


		for cut_name, cut_str in cuts:
			ofdir_cut = "/".join([ofdir, cut_name]) + "/"
			mkdir_p(ofdir_cut)
			cmd = ["bin/histograms", "--infile="+fn, "--outfile=" + ofdir_cut + sn] + args + ["--cut=%s" % cut_str.replace(" ", "")]
			print " ".join(cmd)
			check_call(cmd)