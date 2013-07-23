#ROOTCC=c++ -std=c++11 `root-config --cflags --libs`
ROOTCC=c++ -std=c++0x `root-config --cflags --libs` -lTreePlayer -I/cvmfs/cms.cern.ch/slc5_amd64_gcc462/external/boost/1.47.0/include -L/cvmfs/cms.cern.ch/slc5_amd64_gcc462/external/boost/1.47.0/lib -lboost_program_options 

SRC_DIR=$(STPOL_DIR)/CMSSW_5_3_11/src/SingleTopPolarization/Analysis/bin
PYTHON_INC_DIR=`python -c "import distutils.sysconfig;print distutils.sysconfig.get_python_inc()"`
test:
	util/test_step1.sh
	util/test_step2.sh

clean:
	rm -Rf testing_step*
	rm *.log

all: wjets_rew pytest

wjets_rew:
	$(ROOTCC) $(SRC_DIR)/WJets_reweighting.cc -o bin/WJets_reweighting
	$(ROOTCC) $(SRC_DIR)/histograms.cc -o bin/histograms

pytest:
	c++ --std=c++0x -I$(PYTHON_INC_DIR) -lboost_python-mt -lpython $(SRC_DIR)/pytest.cc -o bin/pytest
