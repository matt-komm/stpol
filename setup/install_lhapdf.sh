#!/bin/bash
echo "Installing LHAPDF"
DIR=$STPOL_DIR/local
mkdir -p $DIR
cd $DIR
rm -Rf lhapdf-5.8.9*
wget http://www.hepforge.org/archive/lhapdf/lhapdf-5.8.9.tar.gz
tar xf lhapdf-5.8.9.tar.gz
cd lhapdf-5.8.9
./configure --disable-pyext --with-max-num-pdfsets=5 --prefix=$DIR
make -j16
make install
cd $DIR/share/lhapdf

pdfs=( NNPDF21_100 CT10 MSTW2008nlo68cl cteq66 MSTW2008nlo68cl )
for p in "${pdfs[@]}" 
do
    lhapdf-getdata $p
done

#Removing the 'external' directory manually is necessary to prompt a recreation of the symlinks
echo "LHAPDF installed, you may want to link it to CMSSW by doing 'cd $CMSSW_BASE;rm -Rf external;scram b clean;scram setup lhapdffull;scram b -j20'"
