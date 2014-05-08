#!/bin/bash
HDIR=/Users/joosep/Documents/stpol/notes/analysis_notes/notes/AN-12-448/trunk/results/
python $STPOL_DIR/src/unfolded_plot/pseudoexp.py --channel=mu $HDIR/muon/unfolded_pseudo.root $HDIR/muon/unfolded_data.root
python $STPOL_DIR/src/unfolded_plot/pseudoexp.py --channel=ele $HDIR/electron/unfolded_pseudo.root $HDIR/electron/unfolded_data.root
