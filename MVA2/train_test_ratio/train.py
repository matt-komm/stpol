import sys
import ROOT
import MVA2.common
from plots.common import cuts
import numpy as np

qs = np.linspace(0.02, .98, 49)
Ns = np.logspace(0, 3.5, 100)

def train(q, Ns):
	train = MVA2.common.MVA_trainer("prepared/{0:.2f}.root".format(q), ofName = "trained/{0:.2f}.root".format(q), jobname="BDT_{0:.2f}".format(q))
	train.add_variable("mt_mu")
	train.add_variable("top_mass")
	train.add_variable("eta_lj")
	train.add_variable("bdiscr_bj")
	train.add_variable("bdiscr_lj")
	train.add_variable("eta_bj")
	train.add_variable("eta_lj")
	train.add_variable("met")
	train.add_variable("mu_iso")
	train.add_variable("rms_lj")

	for N in Ns:
		train.book_method(ROOT.TMVA.Types.kBDT, '{0:.2f}_BDT_{1}'.format(q, N), "!H:!V:NTrees={0:d}".format(int(N)))

	train.get_factory().TrainAllMethods()
	train.evaluate()
	train.pack()

if __name__ == "__main__":
	for q in qs:
		train(q, Ns)
