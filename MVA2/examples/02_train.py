#!/usr/bin/env python
"""An example of training MVAs with mvalib.train.

The script assumes that 01_prepare.py has run and prepared the samples.

"""

from mvalib.train import *

def trainMVA(fName, jobname):
	print '=== Training `{0}` based on `{1}`'.format(jobname, fName)
	train = MVATrainer(fName, jobname=jobname)
	train.add_variable('eta_lj')
	train.add_variable('top_mass')

	train.book_method(mvatypes.kMLP, 'MLP', '!H:!V:VarTransform=N:HiddenLayers=2:TrainingMethod=BFGS:NCycles=2')
	train.book_method(mvatypes.kBDT, 'naiveBDT', '')
	train.book_method(mvatypes.kBDT, 'BDT', '!H:!V:NTrees=20:nEventsMin=20:MaxDepth=2:BoostType=AdaBoost:SeparationType=GiniIndex:nCuts=10:PruneMethod=NoPruning')

	train.get_factory().TrainAllMethods()
	train.evaluate()
	train.pack()
	train.finish()

if __name__ == '__main__':
	trainMVA('prepared/mvaprep_mu.root', 'exmu')
	trainMVA('prepared/mvaprep_ele.root', 'exele')
