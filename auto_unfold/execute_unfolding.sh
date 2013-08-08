#!/bin/bash
export LD_LIBRARY_PATH=../../unfold/tunfold:$LD_LIBRARY_PATH
$STPOL_DIR/unfold/unfoldPE $@
