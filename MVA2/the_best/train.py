import MVA2.common
import ROOT

train = MVA2.common.MVA_trainer('prepared.root', ofName = 'trained.root', jobname='analysis')
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


train.book_method(ROOT.TMVA.Types.kBDT, "BDT", "!H:!V:\
NTrees=100:\
")
train.book_method(ROOT.TMVA.Types.kLikelihood, "Likelihood", "!H:!V:")

train.get_factory().TrainAllMethods()
train.evaluate()
train.pack()
