#ROOTCC=c++ -std=c++11 `root-config --cflags --libs`
ROOTCC=c++ -std=c++0x `root-config --cflags --libs`

test:
	util/test_step1.sh
	util/test_step2.sh

clean:
	rm -Rf testing_step*
	rm *.log

code:
	$(ROOTCC) $(STPOL_DIR)/CMSSW_5_3_11/src/SingleTopPolarization/Analysis/bin/WJets_reweighting.cc -o bin/WJets_reweighting
	$(ROOTCC) $(STPOL_DIR)/CMSSW_5_3_11/src/SingleTopPolarization/Analysis/bin/histograms.cc -o bin/histograms
