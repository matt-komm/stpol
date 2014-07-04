#!/bin/bash
export LD_LIBRARY_PATH=$STPOL_DIR/unfold/RooUnfold-1.1.1:$STPOL_DIR/unfold/tunfold17.3:$LD_LIBRARY_PATH
$STPOL_DIR/unfold/unfoldPE $@ | tee unfolding.log
