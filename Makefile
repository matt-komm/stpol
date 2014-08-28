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

test_step2_tchan_comphep_anom_tensor:
	cmsRun $(STEP2CFG) subChannel=TToBENu_anomWtb-Lv2Rt2_LVRT srcPUDistribution=S10 destPUDistribution=data dataRun=RunABCD isComphep=True inputFiles=file:/hdfs/cms/store/user/atiko/TToBENu_anomWtb-Lv2Rt2_LVRT_t-channel_TuneZ2star_8TeV-comphep/tensor/572aa3280a64b07f7208c06b702633e8/output_noSkim_1_1_ga4.root outputFile=tests/step2/tchan/comphep_anom_tensor

test_step2_tchan_comphep_anom_vector:
	cmsRun $(STEP2CFG) subChannel=TToBENu_anomWtb-0100_t-channel srcPUDistribution=S10 destPUDistribution=data dataRun=RunABCD isComphep=True inputFiles=file:/hdfs/cms/store/user/joosep/TToBENu_anomWtb-0100_t-channel_TuneZ2star_8TeV-comphep/Dec3_anom_2b3b43/2a771fe5d008406ebf97c1e21558b199/output_noSkim_1_4_7q1.root outputFile=tests/step2/tchan/comphep_anom_vector

test_step2_tchan_mass:
	cmsRun $(STEP2CFG) inputFiles=file:$(infile_step2_tchan_mass) subChannel=T_t_ToLeptons_mass166_5 srcPUDistribution=S10 destPUDistribution=data dataRun=RunABCD outputFile=tests/step2/tchan/mass.root          

test_step2_tchan_scale:
	cmsRun $(STEP2CFG) inputFiles=file:$(infile_step2_tchan_scale) subChannel=T_t_ToLeptons_scaleup srcPUDistribution=S10 destPUDistribution=data dataRun=RunABCD outputFile=tests/step2/tchan/scale.root  

test_step2_metphi:
	cmsRun step2_csvt_metshift_off.py inputFiles=file:$(infile_step2_tchan_nominal) subChannel=T_t_ToLeptons outputFile=tests/step2/tchan/metphi_off.root
	cmsRun step2_csvt_metshift_on.py inputFiles=file:$(infile_step2_tchan_nominal) subChannel=T_t_ToLeptons outputFile=tests/step2/tchan/metphi_on.root

cmssw_debug:
	cd CMSSW; scram b -j16 USER_CXXFLAGS="-DEDM_ML_DEBUG"

update_an:
	cp results/tables/*.csv notes/notes/AN-14-001/trunk/data/
	cp results/plots/unfolded* notes/notes/AN-14-001/trunk/figures/results/
	cp results/plots/results/* notes/notes/AN-14-001/trunk/figures/results/
	cp results/plots/unfolding/* notes/notes/AN-14-001/trunk/figures/unfolding/
	rm -Rf notes/notes/AN-14-001/trunk/data/fits/*
	cp -R results/fits/aug5/* notes/notes/AN-14-001/trunk/data/fits/
	rm -Rf notes/notes/AN-14-001/trunk/data/hists_for_fit_unfolding/*
	cp -R results/hists/Aug5/merged/* notes/notes/AN-14-001/trunk/data/hists_for_fit_unfolding/
