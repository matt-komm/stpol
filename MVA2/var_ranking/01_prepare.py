import shutil
import os

import ROOT

from mvalib.prepare import MVAPreparer
from mvalib.train import MVATrainer
from plots.common.cuts import Cuts

cut={}
cut["ele"] = str(Cuts.n_jets(2)*Cuts.n_tags(1)*Cuts.lepton_veto*Cuts.pt_jet*Cuts.rms_lj*Cuts.met*Cuts.one_electron)
cut["mu"] = str(Cuts.n_jets(2)*Cuts.n_tags(1)*Cuts.lepton_veto*Cuts.pt_jet*Cuts.rms_lj*Cuts.mt_mu*Cuts.one_muon)

prep = MVAPreparer("../step3_latest")

#signal
prep.add_train('signal', 'T_t')
prep.add_train('signal', 'Tbar_t')
prep.add_test('signal', 'T_t_ToLeptons')
prep.add_test('signal', 'Tbar_t_ToLeptons')

#WJets
prep.add_train('background', 'WJets_inclusive')
prep.add_test('background', 'W1Jets_exclusive')
prep.add_test('background', 'W2Jets_exclusive')
prep.add_test('background', 'W3Jets_exclusive')
prep.add_test('background', 'W4Jets_exclusive')

#ttbar
prep.add_train('background', 'TTJets_MassiveBinDECAY')
prep.add_test('background', 'TTJets_FullLept')
prep.add_test('background', 'TTJets_SemiLept')

shutil.rmtree('trees', ignore_errors=True); os.mkdir('trees')

prep.write("ele", cut["ele"], "trees/prepared_ele.root", step3_ofdir="trees")
prep.write("mu",  cut["mu"],  "trees/prepared_mu.root",  step3_ofdir="trees")
