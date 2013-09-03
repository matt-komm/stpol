#!/bin/bash
python $STPOL_DIR/src/unfolded_plot/pseudoexp.py --channel=mu results/unfolding/Aug28/muon/unfolded.root /Users/joosep/Documents/stpol/notes/analysis_notes/notes/AN-12-448/trunk/results/muon/unfolded.root
python $STPOL_DIR/src/unfolded_plot/pseudoexp.py --channel=ele results/unfolding/Aug28/electron/unfolded.root /Users/joosep/Documents/stpol/notes/analysis_notes/notes/AN-12-448/trunk/results/electron/unfolded.root
