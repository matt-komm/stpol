import ROOT
from plots.common import cross_sections
from plots.common import cuts
import common


train = common.MVA_trainer('prepared.root', jobname='quicktest')
train.add_variable("eta_lj")
train.add_variable("top_mass")
#train.prepare()

#train.get_factory().PrepareTrainingAndTestTree(ROOT.TCut(), '')

train.book_method(ROOT.TMVA.Types.kMLP, "MLP", "!H:!V:VarTransform=N:HiddenLayers=2:TrainingMethod=BFGS:NCycles=2")
train.book_method(ROOT.TMVA.Types.kBDT, "BDT", "!H:!V:NTrees=20:nEventsMin=20:MaxDepth=2:BoostType=AdaBoost:SeparationType=GiniIndex:nCuts=10:PruneMethod=NoPruning")

train.get_factory().TrainAllMethods()

train.evaluate()
#train.pack()
#train.finish()
