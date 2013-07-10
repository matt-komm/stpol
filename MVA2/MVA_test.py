import ROOT
from plots.common import cross_sections
from plots.common import cuts
import common


train = common.MVA_trainer()
train.add_signal("T_t_ToLeptons")
train.add_signal("Tbar_t_ToLeptons")
train.add_background("T_tW")
train.add_background("Tbar_tW")
train.add_background("WJets_inclusive")
train.add_variable("eta_lj")
train.add_variable("top_mass")

train.prepare()

train.get_factory().PrepareTrainingAndTestTree(ROOT.TCut(), "")

train.book_method(ROOT.TMVA.Types.kMLP, "MLP", "!H:!V:VarTransform=N:HiddenLayers=10:TrainingMethod=BFGS:NCycles=10")

train.get_factory().TrainAllMethods()
train.get_factory().TestAllMethods()
train.get_factory().EvaluateAllMethods()

train.pack_and_finish()
