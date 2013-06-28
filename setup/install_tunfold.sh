#!/bin/bash

echo "Setting up TUnfold in $STPOL_DIR/unfold/tunfold"
cd $STPOL_DIR
cd unfold
mkdir tunfold
cd tunfold
wget --no-check-certificate http://www.desy.de/~sschmitt/TUnfold/TUnfold_V17.2beta1.tgz
tar xf TUnfold_V17.2beta1.tgz
make lib
make bin
cd $STPOL_DIR
