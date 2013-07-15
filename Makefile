test:
	util/test_step1.sh
	util/test_step2.sh

clean:
	rm -Rf testing_step*
	rm *.log

code:
	c++ -std=c++0x `root-config --cflags --libs` $(STPOL_DIR)/CMSSW_5_3_11/src/SingleTopPolarization/Analysis/bin/WJets_reweighting.cc -o bin/WJets_reweighting
