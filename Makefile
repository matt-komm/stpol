#ROOTCC=c++ -std=c++11 `root-config --cflags --libs`
ROOTCC=c++ -std=c++0x `root-config --cflags --libs` -lTreePlayer -lboost_program_options-mt

SRCDIR=$(STPOL_DIR)/CMSSW_5_3_11/src/SingleTopPolarization/Analysis/bin/
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
	c++ --std=c++0x -lpython  $(SRC_DIR)/pytest.cc -o bin/pytest
