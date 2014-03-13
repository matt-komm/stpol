test: test_step2

STEP1CFG=$(CMSSW_BASE)/src/SingleTopPolarization/Analysis/python/runconfs/step1/step1.py
STEP2CFG=$(CMSSW_BASE)/src/SingleTopPolarization/Analysis/python/runconfs/step2/step2.py maxEvents=10000

#step1
infile_step1_tchan_nominal=/hdfs/cms/store/mc/Summer12_DR53X/TToLeptons_t-channel_8TeV-powheg-tauola/AODSIM/PU_S10_START53_V7A-v1/0000/0034258A-D7DE-E111-BEE3-00261834B529.root
#step2
infile_step2_tchan_nominal=/hdfs/cms/store/user/joosep/TToLeptons_t-channel_8TeV-powheg-tauola/Jul8_51f69b/e6cee8f160cb239f414a74aa40d88ea9/output_noSkim_1_1_YzB.root
infile_step2_tchan_mass=/hdfs/cms/store/user/jpata/TToLeptons_t-channel_mass166_5_8TeV-powheg-tauola/Jul8_51f69b/e6cee8f160cb239f414a74aa40d88ea9/output_noSkim_1_2_NRF.root
infile_step2_tchan_scale=/hdfs/cms/store/user/jpata/TToLeptons_t-channel_scaleup_8TeV-powheg-tauola/Jul8_51f69b/e6cee8f160cb239f414a74aa40d88ea9/output_noSkim_1_12_Cq2.root


test_step1: test_step1_tchan_nominal

test_step1_tchan_nominal:
	cmsRun $(STEP1CFG) inputFiles=file:$(infile_step1_tchan_nominal) maxEvents=100


test_step2: test_step2_tchan_nominal test_step2_tchan_mass test_step2_tchan_scale

test_step2_tchan_nominal:
	cmsRun $(STEP2CFG) inputFiles=file:$(infile_step2_tchan_nominal) subChannel=T_t_ToLeptons srcPUDistribution=S10 destPUDistribution=data dataRun=RunABCD outputFile=tests/step2/tchan/nominal.root

test_step2_tchan_mass:
	cmsRun $(STEP2CFG) inputFiles=file:$(infile_step2_tchan_mass) subChannel=T_t_ToLeptons_mass166_5 srcPUDistribution=S10 destPUDistribution=data dataRun=RunABCD outputFile=tests/step2/tchan/mass.root          

test_step2_tchan_scale:
	cmsRun $(STEP2CFG) inputFiles=file:$(infile_step2_tchan_scale) subChannel=T_t_ToLeptons_scaleup srcPUDistribution=S10 destPUDistribution=data dataRun=RunABCD outputFile=tests/step2/tchan/scale.root  

###   all: update step2_ntuple
###   .PHONY: setup
###   
###   setup:
###   	./setup.sh
###   
###   update:
###   	git pull
###   	git submodule init
###   	git submodule update --remote --recursive
###   
###   step2_ntuple:
###   	cd src/ntuple; make
###   
###   test:
###   	cd src/ntuple;make test
###   ##ROOTCC=c++ -std=c++11 `root-config --cflags --libs`
###   #ROOTCC=c++ -std=c++0x `root-config --cflags --libs` -lTreePlayer
###   #
###   #BOOSTLIBS=-I/cvmfs/cms.cern.ch/slc5_amd64_gcc462/external/boost/1.47.0/include -L/cvmfs/cms.cern.ch/slc5_amd64_gcc462/external/boost/1.47.0/lib -I/Users/joosep/CMSSW/osx107_amd64_gcc462/external/boost/1.47.0-cms/include -L/Users/joosep/CMSSW/osx107_amd64_gcc462/external/boost/1.47.0-cms/lib -lboost_program_options
###   ##BOOSTLIBS=-lboost_program_options-m#ut
###   #
###   #SRC_DIR=$(STPOL_DIR)/CMSSW_5_3_11/src/SingleTopPolarization/Analysis/bin
###   #
###   #all: example
###   #
###   #example:
###   #	cd CMSSW*/src/SingleTopPolarization/Analysis/bin; touch BuildFile.xml; scram b -j 2
###   #
###   #wjets_rew:
###   #	mkdir -p $(STPOL_DIR)/bin
###   #	$(ROOTCC) $(BOOSTLIBS) $(SRC_DIR)/WJets_reweighting.cc -o bin/WJets_reweighting
###   #	#FIXME: compile using CMSSW-only libs
###   #	#$(ROOTCC) $(BOOSTLIBS) $(SRC_DIR)/histograms.cc -o bin/histograms
###   #
###   #.PHONY : test
###   #test:
###   #	./tests/step2.py
