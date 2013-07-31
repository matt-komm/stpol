#!/usr/bin/env python
"""An example of the mvalib.prepare API to prepare samples for training."""

import os, shutil
from mvalib.prepare import *
from plots.common.plot_defs import plot_defs

mvaprep = MVAPreparer('../step3_latest')

mvaprep.add_train('background', 'WJets_inclusive')
mvaprep.add_test('background', 'W1Jets_exclusive')
mvaprep.add_test('background', 'W2Jets_exclusive')
mvaprep.add_test('background', 'W3Jets_exclusive')
mvaprep.add_test('background', 'W4Jets_exclusive')

mvaprep.add_test('signal', 'W1Jets_exclusive')
mvaprep.add_test('signal', 'T_t_ToLeptons')
mvaprep.add_test('signal', 'Tbar_t_ToLeptons')
mvaprep.add_train('signal', 'T_t')
mvaprep.add_train('signal', 'Tbar_t')

mvaprep.add_frac('background', 'WW', train_fraction=0.2)
mvaprep.add_frac('background', 'WZ', train_fraction=0.4)
mvaprep.add_frac('background', 'ZZ')

shutil.rmtree('prepared', ignore_errors=True)
os.mkdir('prepared')

mvaprep.write('mu', plot_defs['mva_bdt']['mucut'],
              'prepared/mvaprep_mu.root', step3_ofdir='prepared')
mvaprep.write('ele', plot_defs['mva_bdt']['elecut'],
              'prepared/mvaprep_ele.root', step3_ofdir='prepared')


