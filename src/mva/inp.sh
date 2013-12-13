#!/bin/bash
#generated file lists

find skims/$1/tchan -name "*.root" > input/$2/sig.txt
find skims/$1/ttjets -name "*.root" > input/$2/bg.txt
find skims/$1/wjets -name "*.root" >> input/$2/bg.txt
