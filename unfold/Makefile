CC=g++
CXXFLAGS= -Wall -O2 -g -I./tunfold17.3 -L./tunfold17.3 -Wl,-rpath=./tunfold17.3 -lunfold `root-config --cflags --libs` -lMinuit -lXMLIO -lXMLParser
LDFLAGS=-L./tunfold17.3 -Wl,-rpath=./tunfold17.3 -lunfold -lMinuit

all: unfoldPE

unfoldPE: unfoldPE.cc
	g++ -o unfoldPE $(CXXFLAGS) $(LDFLAGS) unfoldPE.cc


