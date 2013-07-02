#!/bin/sh

make
./rebin
./efficiency
./makehistos
hadd -f histos/data.root histos/input/*.root
./pseudodata

