#!/bin/bash
python $STPOL_DIR/src/unfolded_plot/pseudoexp.py --channel=mu results/unfolding/Aug28/muon/unfolded.root results/unfolding/Aug28/muon/unfolded_data.root
python $STPOL_DIR/src/unfolded_plot/pseudoexp.py --channel=ele results/unfolding/Aug28/electron/unfolded.root results/unfolding/Aug28/electron/unfolded_data.root