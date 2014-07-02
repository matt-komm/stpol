#!/bin/bash
echo "Installing LHAPDF"
DIR=$STPOL_DIR/local
mkdir -p $DIR
cd $DIR
rm -Rf lhapdf-5.9.1*
wget http://www.hepforge.org/archive/lhapdf/lhapdf-5.9.1.tar.gz --no-check-certificate
tar xf lhapdf-5.9.1.tar.gz
cd lhapdf-5.9.1
./configure --disable-pyext --with-max-num-pdfsets=5 --prefix=$DIR
make -j16
make install
cd $DIR/share/lhapdf

pdfs=( NNPDF21_100 CT10 MSTW2008nlo68cl cteq66 CT10as cteq66alphas MSTW2008CPdeutnlo68cl MSTW2008nlo68cl_asmz+68cl MSTW2008nlo68cl_asmz-68cl NNPDF23_nlo_as_0119 NNPDF23_nlo_as_0116 NNPDF23_nlo_as_0117 NNPDF23_nlo_as_0118 NNPDF23_nlo_as_0120 NNPDF23_nlo_as_0121 NNPDF23_nlo_as_0122 )
for p in "${pdfs[@]}" 
do
    $DIR/lhapdf-5.9.1/bin/lhapdf-getdata $p
done

#Removing the 'external' directory manually is necessary to prompt a recreation of the symlinks
echo "LHAPDF installed, you may want to link it to CMSSW by doing 'cd $CMSSW_BASE;rm -Rf external;scram b clean;scram setup lhapdffull;scram b -j20'"
