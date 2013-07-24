import sys
import ROOT
import MVA2.common
from plots.common import cuts
import numpy as np

qs = np.linspace(0.02, 1.02, 50)
Ns = np.logspace(0, 3.5, 100)

lept = "mu"

sigs = [
	"T_t_ToLeptons",
	"Tbar_t_ToLeptons",
]

bkgs = [
	"W1Jets_exclusive",
	"W2Jets_exclusive",
	"W3Jets_exclusive",
	"W4Jets_exclusive",
]

for q in qs:
	sys.stdout.write('#')
sys.stdout.write('\n'); sys.stdout.flush()
for q in qs:
	MVA2.common.prepare_files(sigs, bkgs, lept = lept, ofname = "prepared/{0:.2f}.root".format(q), default_ratio = q)
	sys.stdout.write('.'); sys.stdout.flush()
sys.stdout.write('\n'); sys.stdout.flush()




