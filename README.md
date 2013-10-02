Single top polarization analysis
=====

##Recent updates

Oct2: Access code for *step2* edm-ntuples is in ``src/ntuples``. To install it, do

> $ cd stpol

> $ source setenv.sh

> $ git pull; git submodule init; git submodule update --remote --recursive

> $ cd src/ntuple; make setup; make

#SETUP

### Cloning the repository

For read-only access you can use
> git clone git://github.com/HEP-KBFI/stpol.git

If you also wish to commit, you'll have to have a github account and be added to the group, then you can use
> git clone git@github.com:HEP-KBFI/stpol.git

### Setting up the environment

> source /cvmfs/cms.cern.ch/cmsset_default.sh

or by using the following command

> source setenv.sh

### Create the workspace (lite)

If you only need to install the python dependencies without CMSSW, you can executel the following

> ./setup/install_pylibs.sh

### Create the workspace (full)

Run the following to create the CMSSW directory, link the SingleTopPolarization source code folder to it and compile everything
> source setup.sh

### Explanation of various subdirectories

* ``src`` contains various submodules of this analysis that represent different analysis tasks.
* ``src/ntuples`` contains the libraries related to reading the *EDM*-ntuple format that is the primary persistent format of this analysis.
* ``CMSSW_5_3_11`` contains the base framework setup that is used to run the PFBRECO steps and the C++-based analysis.
* ``crabs`` contains the files related to submitting grid jobs for PFBRECO.
* ``datasets`` contains the metadata for the input datasets for this analysis.










---
### Anything below needs to be updated
---
Note, your showtags output after the setup should be the following:          
``` bash
	V00-02-10      CMGTools/External                                
	V00-01-03      CommonTools/CandAlgos                            
	V00-03-16      CommonTools/ParticleFlow                         
	V00-03-24      CommonTools/RecoAlgos                            
	V00-00-14      CommonTools/RecoUtils                            
	V00-02-07      CommonTools/UtilAlgos                            
	V00-04-04      CommonTools/Utils                                
	V15-03-04      DataFormats/ParticleFlowCandidate                
	V06-05-06-05   DataFormats/PatCandidates                        
	V00-02-14      DataFormats/StdDictionaries                      
	V10-02-02      DataFormats/TrackReco                            
	V02-00-04      DataFormats/VertexReco                           
	V00-00-31      EGamma/EGammaAnalysisTools                       
	V00-00-70      FWCore/GuiBrowsers                               
	V08-09-50      PhysicsTools/PatAlgos                            
	V03-09-26      PhysicsTools/PatUtils                            
	V04-01-09      RecoLuminosity/LumiDB                            
	NoTag          RecoMET/METFilters                               
	V15-02-05-01   RecoParticleFlow/PFProducer                      
	NoCVS          SingleTopPolarization/Analysis                   
	NoCVS          SingleTopPolarization/BTagSystematicsWeightProducer 
	NoCVS          SingleTopPolarization/CandTransverseMassProducer 
	NoCVS          SingleTopPolarization/CandViewTreemakerAnalyzer  
	NoCVS          SingleTopPolarization/CleanNoPUJetProducer       
	NoCVS          SingleTopPolarization/CollectionSizeProducer     
	NoCVS          SingleTopPolarization/CosThetaProducer           
	NoCVS          SingleTopPolarization/DeltaRProducer             
	NoCVS          SingleTopPolarization/EfficiencyAnalyzer         
	NoCVS          SingleTopPolarization/ElectronIDProducer         
	NoCVS          SingleTopPolarization/EventDoubleFilter          
	NoCVS          SingleTopPolarization/EventIDAnalyzer            
	NoCVS          SingleTopPolarization/EventIDProducer            
	NoCVS          SingleTopPolarization/FlavourAnalyzer            
	NoCVS          SingleTopPolarization/GenericCollectionCombiner  
	NoCVS          SingleTopPolarization/GenericOwnVectorAnalyzer   
	NoCVS          SingleTopPolarization/GenericPointerCombiner     
	NoCVS          SingleTopPolarization/GenParticleSelector        
	NoCVS          SingleTopPolarization/GenParticleSelectorCompHep 
	NoCVS          SingleTopPolarization/JetMCSmearProducer         
	NoCVS          SingleTopPolarization/LeptonIsolationProducer    
	NoCVS          SingleTopPolarization/MuonEfficiencyProducer     
	NoCVS          SingleTopPolarization/MuonIDProducer             
	NoCVS          SingleTopPolarization/ParticleComparer           
	NoCVS          SingleTopPolarization/PatObjectOwnRefProducer    
	NoCVS          SingleTopPolarization/PDFweightsProducer         
	NoCVS          SingleTopPolarization/PUWeightProducer           
	NoCVS          SingleTopPolarization/RecoFilter                 
	NoCVS          SingleTopPolarization/ReconstructedNeutrinoProducer 
	NoCVS          SingleTopPolarization/SimpleCompositeCandProducer 
	NoCVS          SingleTopPolarization/SimpleEventAnalyzer        
	NoCVS          SingleTopPolarization/TestProd                   
	NoCVS          SingleTopPolarization/TransferMatrixCreator      
	NoTag          TopQuarkAnalysis/SingleTop                       
```
---

#ANALYSIS PATHWAY

The generic analysis pathway is as follows, all the relevant *.py files are in $CMSSW_BASE/src/SingleTopPolarization/Analysis/python/:

0. *selection_step1_cfg.py* for initial event skimming and slimming (both optional), PF2PAT sequence and object ID
1. *selection_step2_cfg.py* for generic single-top specific event selection and reconstruction according 1 lepton, MET, N-Jet and M-tag.
2. *step3_eventLoop_cfg.py* for projecting out the relevant variables from the step2 trees

For convenience, the steps have been wrapped as methods that are called from the files *runconfs/step1_newCmdLine_cfg.py* and *runconfs/step2_newCmdLine_cfg.py*.

#SYNC INPUT FILES

t-channel (/T_t-channel_TuneZ2star_8TeV-powheg-tauola/Summer12-PU_S7_START52_V9-v1/AODSIM)

>/hdfs/local/stpol/sync2012/FCE664EC-E79B-E111-8B06-00266CF2507C.root (1 runs, 18 lumis, 5279 events, 2261976796 bytes)

t-channel (/T_t-channel_TuneZ2star_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM)

>/hdfs/local/stpol/sync2012/FEFF01BD-87DC-E111-BC9E-003048678F8E.root (1 runs, 40 lumis, 11789 events, 4271759218 bytes)

#DEBUGGING

Compile the code using the following command to enable LogDebug and related debugging symbols
>scram b -j8 USER_CXXFLAGS="-DEDM_ML_DEBUG"

Check for memory errors using valgrind:

>valgrind --tool=memcheck `cmsvgsupp` --leak-check=yes --show-reachable=yes --num-callers=20 --track-fds=yes cmsRun your_cfg.py >& vglog.out &

The most important memory errors are in the end of vglog.out

#RUNNING

##Sync
https://twiki.cern.ch/twiki/bin/view/CMS/SyncSingleTopLeptonJets2012
>cmsRun runconfs/step1_sync_cfg.py inputFiles=/store/mc/Summer12_DR53X/T_t-channel_TuneZ2star_8TeV-powheg-tauola/AODSIM/PU_S10_START53_V7A-v1/0000/0059C6F3-7CDC-E111-B4CB-001A92811726.root outputFile=sync_step1/sync_T_t_lepIso02_newIso.root &> log1

##CRAB
To create the crab.cfg files to run the PAT sequences (step1)
>python $CMSSW_BASE/../util/datasets.py -t your_tag -T $CMSSW_BASE/../crabs/crab_Data_step1.cfg -d S1D -o crabs/step1_Data 

###To run the met uncertainty precalculation (step1B)
>python $CMSSW_BASE/../util/datasets.py -t stpol_step1B -T /home/joosep/singletop/stpol/crabs/crab_MC_step1B_local.cfg -d S1B_MC -o crabs/step1B_MC

To create the crab.cfg files to run over the final analysis (step2) 
>python $CMSSW_BASE/../util/datasets.py -t stpol_step2_Iso -T $CMSSW_BASE/../crabs/crab_MC_step2_local_Iso.cfg -d S2_MC -o crabs/step2_MC_Iso 

>python $CMSSW_BASE/../util/datasets.py -t stpol_step2_antiIso -T $CMSSW_BASE/../crabs/crab_MC_step2_local_antiIso.cfg -d S2_MC -o crabs/step2_MC_antiIso 

>python $CMSSW_BASE/../util/datasets.py -t stpol_step2_Iso -T $CMSSW_BASE/../crabs/crab_Data_step2_Iso.cfg -d S2_D -o crabs/step2_Data_Iso

>python $CMSSW_BASE/../util/datasets.py -t stpol_step2_antiIso -T $CMSSW_BASE/../crabs/crab_Data_step2_antiIso.cfg -d S2_D -o crabs/step2_Data_antiIso

###Using lumiCalc2.py
To calculate the integrated luminosity from crab jobs, do the following
>crab -c YOUR_DIR -report
>lumiCalc2.py --without-checkforupdate -i YOUR_DIR/res/lumiSummary.json overview

#Step2 output

The canonical step2(iso) output is currently in *fileList_Step2/*,
but note that the b-tag weight is currently not yet validated

#Step3 code
The code is an FWLite loop, which is available in *CMSSW_5_3_8/src/SingleTopPolarization/Analysis/bin/Step3_EventLoop.cpp*
and can be compiled by either setting up *CMSSW_5_3_8* using (make sure you have no uncommitted changes in your working directory)

>setup.sh

and compiling the code, or moving the code and *BuildFile.xml* to the relevant place in *CMSSW_5_3_7_patch4*.
You should try to take the loop as an example and try to implement your own analysis code based on that. 
The step3 code is steered using the python config file *runconfs/step3_eventloop_base_nocuts.py* where you can turn on/off basic cuts:

1. lepton
2. M_T(W)/MET
3. nJets
4. nTags
5. top mass window

If you need more variables in the trees, you should add them to the
*process.finalVars* PSet and also in the code into the *MiscVars* class. If you are adding a large separate group of variables,
it may make more sense to create a new class for these, which can be turned on/off via the config file.
You should strive to use as strict cuts as is possible for your analysis and as few variables as is possible, in order to not
be in the same situation as earlier, when running over the full step2 trees.

For local running, the python config expects the list of input file names over stdin:

>cat fileList_Step2/T_t.txt | CMSSW_5_3_8/bin/slc5_amd64_gcc462/Step3_EventLoop runconfs/step3_eventLoop_cfg.py

For batch running, the scripts in *analysis_step3* may be useful, in particular

>analysis_step3/run_step3_eventloop.sh list_of_input_files.txt /path/to/output_directory conf.py cmdline args
to simply run the code and
>analysis_step3/slurm_sub_step3.sh list_of_input_files.txt /path/to/output_directory conf.py cmdline args
to submit many jobs based on splitting the list of files.

##Analyzing step3 output
You can use
>analysis_step3/check_step3_output.sh
to list the number of expected tasks(number of split tasks), started tasks, successful tasks and the tasks with an error.

##Resubmitting failed step3 tasks
You can resubmit failed step3 jobs by going to the relevant output directory, deleting the offending .root and .out files and calling either
>eval `cat job`
to resubmit the whole job (all split files) or
>eval `cat task_x?????`
to resubmit a particular task. Make sure you have not changed the config files in the mean time.

A convenient script to resubmit the task is
>analysis_step3/resubmit_failed_task.sh /path/to/slurm.out

##Workflow for creating histograms for unfolding
###1. QCD estimation
Located in $STPOL_DIR/qcd_estimation, must be run as > $STPOL_DIR/theta/utils2/theta-auto.py get_qcd_yield.py

Produces QCD fit by taking QCD shape from anti-isolated data and other processes from MC. Specific cuts are defined in FitConfig.py with on-the-fly modifications for different cut regions.

Fit is done on 3 components: QCD, W+Jets and all other MC, on the MTW variable for muons and MET for electrons.

Fit results are saved in the directory "fitted" for all possible MTW/MET cut values. 

Separate files are created for scale factors to apply to template taken from anti-isolated region whether or not anti-isolated MC is subtracted from the templated.

The fit itself uses the template with MC subtraction.

Fit plots are produced in the 'fit_plots' directory while the fitted distributions are saved 'fits' and templates in 'templates'

Command line parameters:

  '--channel' - "mu" or "ele"
  
  '--cut' - list of cut regions to perform the QCD estimation. Most important ones:
  
      '2j1t' - pre-MVA cut, always applies when MVA used from fit onwards
      
      'final__2j1t' - final selection, cut-based
      
      'fit_2j1t' - for cut-based fit__2j1t
      
      If no key is specified, QCD estimation will be done for all possible cases
      
  '--path' - where to take step3 output from
  
  '--noSystematics' - do not take into account shape systematics of JES, JER and UnclusteredEn in the estimation
  
  '--doSystematicCuts' - perform QCD estimation for a set of special cuts with varied anti-isolated region which are defined in systematics.py
  
  Other files of interest:
  
  init_data.py: definitions of datasets and files - TODO: update when new step2 add new files for data
  
  FitConfig.py: defines the cuts used in the fit, for different iso regions, etc.
  
  plots.common.cross_sections.lumi_iso and .lumi_antiiso are used for luminosities TODO: update when new step2 data arrives
  
  
###2. Creation of histograms to fit
The script to do this is located in $STPOL_DIR/final_fit/makehistos.py

NB! QCD estimation has to be run before as the script takes results straight from qcd_estimation/fitted

For MVA fitting the fit '2j1t' is needed and for eta_j' 'fit_2j1t'

The script creates histograms named in theta format for 3 components - signal ('tchan'), W/Z+jets with WW ('wzjets') and Top processes (ttbar, tW-channel, s-channel) plus QCD ('other') for all the systematic variations

The systematics themselves are defined in plots.common/make_systematics_histos.py (sorry, poorly written code) and are divided into 3 groups 
	1. having separate files for each dataset (En, Res, UnclusteredEn);
  	2. having separate files, but applying only to a few datasets
  	3. altering weights.

Each group is treated differently. 

If tou want to add a new systematic, it is added to this file (or uncomment one of the premade ones which didn't have datasets available before).

TODO: add pileup, ttbar and PDF uncertainties when available and tchan_scale once new data processing completes

The loading of the samples is done in plots.common.load_samples.py (also messy, sorry about that). Adding a new weight-based systematic should require no change in this file, however when adding a systematics that
deals with separate files, then these should be processed there.

Possible command-line arguments are the following:

'--channel', '--path' - as previously

'--var' - variable of the histograms, possible choices: ["eta_lj", "C", "mva_BDT", "mva_BDT_with_top_mass_eta_lj_C_mu_pt_mt_mu_met_mass_bj_pt_bj_mass_lj", "mva_BDT_with_top_mass_C_eta_lj_el_pt_mt_el_pt_bj_mass_bj_met_mass_lj"],

'--coupling' - by default we are using the powheg samples for signal. Here we can use comphep or anomalous couplings instead. choices=["powheg", "comphep", "anomWtb-0100", "anomWtb-unphys"], default="powheg"]

'--asymmetry' - reweigh the generated asymmetry value to something else. Used for linearity tests and estimating uncertainties if the measured result largely differs from the generated one

'--mtmetcut' - use an alternative value for MTW/MET cut, used for cross-checks

### 3. Fitting
The script to do this is located in $STPOL_DIR/final_fit/final_fit.py

$STPOL_DIR/final_fit/compare_template_shapes.py compares the shapes of templates with different systematics and prints out the KS values for non-compatible systematics.

The systematics which match in shape with the nominal should not be used for the fit as the fit might not converge. The are absorbed in the rate uncertainties.

The fit parameters are specified in fit.py

The default shape uncertainties are ["__En", "Res", "ttbar_scale", "ttbar_matching", "iso"]  - other do not change the shape

As a default, unconstrained prior rate uncertaintes are applied for signal and wzjets while "other" (top+qcd) gets a 20% gaussian uncertainty.

By default, the output file will also contain the correlation between ("wzjets", "other"). Others can be added as needed.

The correlation between all parameters in plotted in plots/[fit_name]/corr.pdf

### 4. Creation of histograms for unfolding
The script to do this is located in $STPOL_DIR/unfold/prepare_unfolding.py

The main amount of work goes to creating the same systematic histograms as makehistos.py, just that now they're for cos_theta and with a cut on MVA (or final cut-based selection)

Also created are histograms for generated and reconstructed signal events, selection efficiency of those and a transfer matrix needed for the unfolding.

Currently, 6 bins are used for generated events and 12 for reconstructed. This (6<12) is needed for the unfolding to work properly (and we don't 0 in the middle of any bin)

Command-line arguments are mostly the same as for makehistos.py, except for:

'--eta' if you want to fit on eta

'--mva_var' instead of '--var' specifies variable if using MVA ('--eta' not specified)

'--cut' the cut on MVA as float (MVA > [value specified])

> ./makeUnfoldingHistos.sh 
is used to run a scan over MVA cut values producing histograms for each
