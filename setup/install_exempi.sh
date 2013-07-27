#!/bin/bash
#WIll install EXEMPI, but now working at the moment (ld -lexempi fails regardless of fiddling with the LD_LIBRARY_PATH)
cd $STPOL_DIR/local
wget http://libopenraw.freedesktop.org/download/exempi-2.2.1.tar.bz2
tar xf exempi-2.2.1.tar.bz2
cd exempi-2.2.1
./configure --prefix=$STPOL_DIR/local
make -j16
make install
