import subprocess
from plots.common.utils import *
from plots.common.sample import get_paths
import glob
from subprocess import check_call
from SingleTopPolarization.Analysis.sample_types import *
from rootpy.extern.progressbar import *


widgets = [Percentage(), ' ', Bar(marker=RotatingMarker()), ' ', ETA()]


if __name__=="__main__":
	import logging
	logging.basicConfig(level=logging.INFO)
	path = get_paths()
	print path.keys()
	data_repro = "Jul15"
	fnames = dict()
	fnames["mu/mc/iso/"] = glob.glob(path[data_repro]["mc"]["mu"]["nominal"]["iso"] + "/*.root")
	fnames["mu/data/iso/"] = glob.glob(path[data_repro]["data"]["mu"]["NONE"]["iso"] + "/*.root")
	fnames["mu/data/antiiso/"] = glob.glob(path[data_repro]["data"]["mu"]["NONE"]["antiiso"] + "/*.root")
	pbar = ProgressBar(
		widgets=["Projecting histograms"] + widgets,
		maxval=sum([len(fnames[k]) for k in fnames.keys()])
	).start()

	ofdir = "hists/"

	cuts = [
		("SR", "n_muons==1 && n_eles==0 && n_veto_mu==0 && n_jets>0 && n_veto_ele==0 && rms_lj<0.025 && abs(eta_lj)>2.5 && top_mass<220 && top_mass>130 && mt_mu>50"),
		("SB", "n_muons==1 && n_eles==0 && n_veto_mu==0 && n_jets>0 && n_veto_ele==0 && rms_lj<0.025 && mt_mu>50"),

		("cut0", "n_muons==1 && n_eles==0 && n_veto_mu==0 && n_jets>0 && n_veto_ele==0 && rms_lj<0.025"),
		("cut1", "n_muons==1 && n_eles==0 && n_veto_mu==0 && n_jets>0 && n_veto_ele==0 && rms_lj<0.025 && mt_mu>50"),
		
		("cut1_qcd", "n_muons==1 && n_eles==0 && n_veto_mu==0 && n_jets>0 && n_veto_ele==0 && rms_lj<0.025 && mt_mu>50 && deltaR_bj>0.3 && deltaR_lj>0.3 && mu_iso>0.3 && mu_iso<0.5"),

		("cut2", "n_muons==1 && n_eles==0 && n_veto_mu==0 && n_jets>0 && n_veto_ele==0 && rms_lj<0.025 && mt_mu>50 && top_mass<220 && top_mass>130"),
		("cut2_SB", "n_muons==1 && n_eles==0 && n_veto_mu==0 && n_jets>0 && n_veto_ele==0 && rms_lj<0.025 && mt_mu>50 && top_mass>220 && top_mass<130"),
		("cut3", "n_muons==1 && n_eles==0 && n_veto_mu==0 && n_jets>0 && n_veto_ele==0 && rms_lj<0.025 && mt_mu>50 && top_mass<220 && top_mass>130 && abs(eta_lj)>2.5"),
	]

	weight = "pu_weight*b_weight_nominal*muon_IDWeight*muon_IsoWeight"

	log = open("WJets_make_histograms.log", "w")
	nFiles = 0
	for key, fnames in fnames.items():
		for fn in fnames:
			nFiles += 1
			pbar.update(nFiles)
			sn = get_sample_name(fn)

			of = ofdir + key
			args = []
			if is_wjets(sn):
				args += ["--doWJetsMadgraphWeight=true"]
			if "sherpa" in sn:
				args += ["--doWJetsSherpaWeight=true"]

			if not is_mc(sn):
				args += ["--isMC=false"]


			for cut_name, cut_str in cuts:
				ofdir_cut = "/".join([of, cut_name]) + "/"
				mkdir_p(ofdir_cut)
				cmd = ["bin/histograms", "--infile="+fn, "--outfile=" + ofdir_cut + sn + ".root"] + args + ["--cut=%s" % cut_str.replace(" ", "")]
				check_call(cmd, stdout=log, stderr=log)
	pbar.finish()

	log.close()
