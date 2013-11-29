
#########
# STEP1 #
#########

CFG1=$(CMSSW_BASE)/src/SingleTopPolarization/Analysis/python/runconfs/step1/step1.py
OPTS1=doSkimming=False doDebug=False
SYNC_DIR=`pwd`

step1: step1_inclusive step1_exclusive

step1_inclusive:
	cmsRun $(CFG1) $(OPTS1) inputFiles_load=$(SYNC_DIR)/inclusive/files.txt outputFile=$(SYNC_DIR)/inclusive/step1.root &> $(SYNC_DIR)/inclusive/log_step1.txt

step1_exclusive:
	cmsRun $(CFG1) $(OPTS1) inputFiles_load=$(SYNC_DIR)/exclusive/files.txt outputFile=$(SYNC_DIR)/exclusive/step1.root &> $(SYNC_DIR)/exclusive/log_step1.txt


#########
# STEP2 #
#########

CFG2=$(CMSSW_BASE)/src/SingleTopPolarization/Analysis/python/runconfs/step2/step2.py
OPTS2=doDebug=True subChannel=T_t

step2: step2_inclusive

step2_inclusive:
	cmsRun $(CFG2) inputFiles=file:$(SYNC_DIR)/inclusive/step1_noSkim.root $(OPTS2) outputFile=$(SYNC_DIR)/inclusive/step2.root &> $(SYNC_DIR)/inclusive/log_step2.txt

#########
# STEP3 #
#########
STEP3CMD_SKIM=STPOL_NOSKIM=1 /home/joosep/singletop/stpol2/src/skim/skim.jl
STEP3CMD_HADD=/home/joosep/singletop/stpol2/src/skim/hadd.jl
step3: step3_inclusive

step3_inclusive:
	$(STEP3CMD_SKIM) inclusive/step3 inclusive/step2.root
	find inclusive -name step3.root > inclusive/step3.txt
	$(STEP3CMD_HADD) inclusive/step3.txt inclusive/step3 
