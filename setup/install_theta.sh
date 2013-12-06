#!/bin/bash

if [ -z "$STPOL_DIR" ]; then
    STPOL_DIR=`pwd` 
fi  

echo "Setting up theta"
mkdir -p $STPOL_DIR/local
cd $STPOL_DIR/local
svn co https://ekptrac.physik.uni-karlsruhe.de/public/theta/tags/testing theta
cd theta
make -j16
cd $STPOL_DIR
