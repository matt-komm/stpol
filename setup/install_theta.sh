#!/bin/bash

echo "Setting up theta"
cd $STPOL_DIR
svn co https://ekptrac.physik.uni-karlsruhe.de/public/theta/tags/testing theta
cd theta
make
cd $STPOL_DIR
