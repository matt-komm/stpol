CC=g++
CXXFLAGS= -Wall -O2 -g -I./tunfold -L./tunfold -Wl,-rpath=./tunfold -lunfold `root-config --cflags --libs` -lMinuit 

all: unfold calc_asymmetry eigenvalues makehistos bkg_asymmetry findbinning efficiency rebin plotfit pseudodata

unfold: unfold.cc binnings.h utils.hpp

calc_asymmetry: calc_asymmetry.C binnings.h utils.hpp

bkg_asymmetry: bkg_asymmetry.C binnings.h utils.hpp

makehistos: makehistos.C xsec.h binnings.h

findbinning: findbinning.C info.h binnings.h

efficiency: efficiency.C histo.hpp xsec.h info.h binnings.h

rebin: rebin.C binnings.h info.h xsec.h helpers.hpp

plotfit: plotfit.C binnings.h utils.hpp

pseudodata: pseudodata.C binnings.h utils.hpp

clean:
	rm unfold calc_asymmetry bkg_asymmetry makehistos findbinning efficiency rebin plotfit eigenvalues pseudodata
