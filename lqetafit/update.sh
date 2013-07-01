#!/bin/bash

make
rm histos/*
./makehistos
hadd -f histos/lqeta.root histos/*.root
./pseudodata
#hadd -f histos/light.root histos/*_light.root
#hadd -f histos/heavy.root histos/*_heavy.root
