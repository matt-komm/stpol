CC=g++
CXXFLAGS= -Wall -O2 -g `root-config --cflags --libs`

all: makehistos read plotfit pseudodata makehistos2

makehistos: makehistos.C xsec.h
makehistos2: makehistos2.C xsec.h
