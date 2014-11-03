#Does primary event skimming and PFBRECO
#Author: Joosep Pata joosep.pata@cern.ch
#many modifucations taken from Andrey Popovs code

#from Configuration.StandardSequences.Geometry_cff import *
from Configuration.Geometry.GeometryIdeal_cff import *
from Configuration.StandardSequences.MagneticField_cff import *
from Configuration.StandardSequences.FrontierConditions_GlobalTag_cff import *
import FWCore.ParameterSet.Config as cms

## import skeleton process
from PhysicsTools.PatAlgos.tools.coreTools import *
from PhysicsTools.PatAlgos.tools.pfTools import *

from SingleTopPolarization.Analysis.eventCounting import *

from PhysicsTools.PatAlgos.selectionLayer1.jetSelector_cfi import *

from FWCore.ParameterSet.VarParsing import VarParsing
from SingleTopPolarization.Analysis.config_step2_cfg import Config

def SingleTopStep1(
    process,
    ):

    options = VarParsing('analysis')
    options.register ('isMC', True,
        VarParsing.multiplicity.singleton,
        VarParsing.varType.bool,
        "Run on MC"
    )
    options.register ('doDebug', False,
        VarParsing.multiplicity.singleton,
        VarParsing.varType.bool,
        "Run in debugging mode"
    )
    options.register ('doSkimming', True,
        VarParsing.multiplicity.singleton,
        VarParsing.varType.bool,
        "Preselect events"
    )
    options.register ('doSlimming', True,
        VarParsing.multiplicity.singleton,
        VarParsing.varType.bool,
        "Drop unnecessary collections"
    )
    options.register ('runOnFastSim', False,
        VarParsing.multiplicity.singleton,
        VarParsing.varType.bool,
        "FastSim-specific processing"
    )

    options.register ('doSync', False,
        VarParsing.multiplicity.singleton,
        VarParsing.varType.bool,
        "Synchronization exercise"
    )

    #Tag from https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideFrontierConditions?redirectedfrom=CMS.SWGuideFrontierConditions#2012_MC_production
    #Latest for "53Y Releases (MC)"
    options.register ('globalTag', Config.globalTagMC,
        VarParsing.multiplicity.singleton,
        VarParsing.varType.string,
        "Global tag"
    )
    options.parseArguments()

    if len(options.inputFiles)==0:
            options.inputFiles = cms.untracked.vstring(['/store/relval/CMSSW_5_3_6-START53_V14/RelValProdTTbar/AODSIM/v2/00000/76ED0FA6-1E2A-E211-B8F1-001A92971B72.root'])
    process.source.fileNames = cms.untracked.vstring(options.inputFiles)
    process.maxEvents = cms.untracked.PSet(
        input = cms.untracked.int32(options.maxEvents)
    )
    process.out.fileName = cms.untracked.string(options.outputFile)
    process.options = cms.untracked.PSet(wantSummary=cms.untracked.bool(options.doDebug))

    if options.doDebug:
        process.load("FWCore.MessageLogger.MessageLogger_cfi")
        process.MessageLogger = cms.Service("MessageLogger",
            destinations=cms.untracked.vstring('cout', 'debug'),
            debugModules=cms.untracked.vstring('*'),
            cout=cms.untracked.PSet(threshold=cms.untracked.string('INFO')),
            debug=cms.untracked.PSet(threshold=cms.untracked.string('DEBUG')),
        )
    else:
        process.load("FWCore.MessageService.MessageLogger_cfi")

    #https://twiki.cern.ch/twiki/bin/viewauth/CMS/IntroToJEC
    #https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookJetEnergyCorrections#JetEnCor2012Summer13
    postfix = ""
    jetCorr = ['L1FastJet', 'L2Relative', 'L3Absolute']
    if not options.isMC:
            jetCorr += ['L2L3Residual']
    print options

    usePF2PAT(process, runPF2PAT=True, jetAlgo='AK5', runOnMC=options.isMC, postfix=postfix,
        jetCorrections=('AK5PFchs', jetCorr),
        pvCollection=cms.InputTag('goodOfflinePrimaryVertices'),
        #typeIMetCorrections = True
        typeIMetCorrections = False #Type1 MET now applied later using runMETUncertainties
    )

    # https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookJetEnergyCorrections#JetEnCorPFnoPU2012
    process.pfPileUp.Enable = True
    process.pfPileUp.checkClosestZVertex = False

    #-------------------------------------------------
    # selection step 2: vertex filter
    #-------------------------------------------------

    # https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookJetEnergyCorrections#JetEnCorPFnoPU2012
    # https://twiki.cern.ch/twiki/bin/viewauth/CMS/TWikiTopRefEventSel#Cleaning_Filters
    #process.goodOfflinePrimaryVertices = cms.EDFilter(
    #    "PrimaryVertexObjectFilter"
    #, filterParams = cms.PSet(
    #        minNdof = cms.double(4.0)
    #    , maxZ = cms.double(24.0)
    #    , maxRho = cms.double(2.0)
    #    )
    #, filter = cms.bool(True)
    #, src = cms.InputTag('offlinePrimaryVertices')
    #)

    process.goodOfflinePrimaryVertices = cms.EDFilter("FirstVertexFilter",
        src = cms.InputTag("offlinePrimaryVertices"),
        cut = cms.string('!isFake & ndof >= 4. & abs(z) < 24. & position.Rho < 2.')
    )

    from EventFilters_cff import ApplyEventFilters
    ApplyEventFilters(process, runOnFastSim=options.runOnFastSim)
    #-------------------------------------------------
    # Muons
    #-------------------------------------------------

    #process.selectedPatMuons.cut = "pt>10 && abs(eta)<3.0"

    # Enable delta-beta correction for the muon isolation and set the recommended cut [1]
    # [1] https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideMuonId?rev=46#Muon_Isolation
    process.pfIsolatedMuons.doDeltaBetaCorrection = True
    process.pfIsolatedMuons.deltaBetaFactor = -0.5
    process.pfIsolatedMuons.isolationCut = 0.2

    #process.pfSelectedMuons.cut = 'abs(eta)<2.5 && pt>10.'
    process.pfSelectedMuons.cut = '(pt > 10.) && (abs(eta) < 2.5) && (muonRef.isAvailable) && (muonRef.isPFMuon) && (muonRef.isGlobalMuon || isTrackerMuon)'
    process.patMuons.embedTrack = True
    process.patMuons.usePV = False
    #process.selectedPatMuons.cut = "(abs(eta) < 2.5) && (pt > 10.0) && ((chargedHadronIso+max(0.,neutralHadronIso+photonIso-0.50*puChargedHadronIso))/pt < 0.20) && (isPFMuon && (isGlobalMuon || isTrackerMu)"

    # Release cuts on compatibility with the first primary vertex (similar to electrons)
    process.pfMuonsFromVertex.d0Cut = 9999.
    process.pfMuonsFromVertex.d0SigCut = 9999.
    process.pfMuonsFromVertex.dzCut = 9999.
    process.pfMuonsFromVertex.dzSigCut = 9999.

    process.patMuons.pfMuonSource = cms.InputTag("pfIsolatedMuons")
    process.muonMatch.src = cms.InputTag("pfIsolatedMuons")

    process.muonMatchAll = process.muonMatch.clone(
        src = cms.InputTag("pfMuons")
    )
    process.patMuonsAll = process.patMuons.clone(
        pfMuonSource = cms.InputTag("pfMuons"),
        genParticleMatch = cms.InputTag("muonMatchAll"),
    )
    process.selectedPatMuonsAll = process.selectedPatMuons.clone(
        src = cms.InputTag("patMuonsAll"),
    )

    # muon ID production (essentially track count embedding) must be here
    # because tracks get dropped from the collection after this step, resulting
    # in null ptrs.
    process.muonsWithID = cms.EDProducer(
        'MuonIDProducer',
        muonSrc = cms.InputTag("selectedPatMuons"),
        primaryVertexSource = cms.InputTag("goodOfflinePrimaryVertices")
    )
    process.muonsWithIDAll = process.muonsWithID.clone(
        muonSrc = cms.InputTag("selectedPatMuonsAll")
    )
    process.muonSequence = cms.Sequence()
    if options.isMC:
        process.muonSequence += process.muonMatchAll
    process.muonSequence += (
        process.patMuonsAll *
        process.selectedPatMuonsAll *
        process.muonsWithIDAll
    )

    #-------------------------------------------------
    # Electrons
    # Implemented as in https://indico.cern.ch/getFile.py/access?contribId=1&resId=0&materialId=slides&confId=208765
    #-------------------------------------------------

    #From EgammaAnalysis/ElectronTools/test/patTuple_electronId_cfg.py
    process.load('EgammaAnalysis.ElectronTools.electronIdMVAProducer_cfi')
    process.load('EgammaAnalysis.ElectronTools.electronIsolatorFromEffectiveArea_cfi')
    process.mvaID = cms.Sequence(    process.mvaTrigV0 + process.mvaTrigNoIPV0 + process.mvaNonTrigV0 )
    process.patElectrons.electronIDSources = cms.PSet(
        mvaTrigV0 = cms.InputTag("mvaTrigV0"),
        mvaNonTrigV0 = cms.InputTag("mvaNonTrigV0"),
        mvaTrigNoIPV0 = cms.InputTag("mvaTrigNoIPV0"),
    )
    process.patPF2PATSequence.replace(process.patElectrons, process.mvaID * process.patElectrons)
    #process.selectedPatElectrons.cut = "pt>20 && abs(eta)<3.0"

    process.electronsWithID = cms.EDProducer(
        'ElectronIDProducer',
        electronSrc = cms.InputTag("selectedPatElectrons"),
        primaryVertexSource = cms.InputTag("goodOfflinePrimaryVertices")
    )

    process.pfElectrons.isolationValueMapsCharged = cms.VInputTag(cms.InputTag("elPFIsoValueCharged03PFId"))
    process.pfElectrons.isolationValueMapsNeutral = cms.VInputTag(cms.InputTag("elPFIsoValueNeutral03PFId"), cms.InputTag("elPFIsoValueGamma03PFId"))
    process.pfElectrons.isolationValueMapsNeutral = cms.VInputTag(cms.InputTag("elPFIsoValueNeutral03PFId"), cms.InputTag("elPFIsoValueGamma03PFId"))

    process.patElectrons.isolationValues.pfNeutralHadrons = cms.InputTag("elPFIsoValueNeutral03PFId")
    process.patElectrons.isolationValues.pfChargedAll = cms.InputTag("elPFIsoValueChargedAll03PFId")
    process.patElectrons.isolationValues.pfPUChargedHadrons = cms.InputTag("elPFIsoValuePU03PFId")
    process.patElectrons.isolationValues.pfPhotons = cms.InputTag("elPFIsoValueGamma03PFId")
    process.patElectrons.isolationValues.pfChargedHadrons = cms.InputTag("elPFIsoValueCharged03PFId")

    process.pfIsolatedElectrons.isolationValueMapsCharged = cms.VInputTag(cms.InputTag("elPFIsoValueCharged03PFId"))
    process.pfIsolatedElectrons.deltaBetaIsolationValueMap = cms.InputTag('elPFIsoValueEA03')
    # Define a module to produce a value map with rho correction of electron isolation. The
    # configuration fragment is copied from [1] because it is not included in the current tag of
    # UserCode/EGamma/EGammaAnalysisTools. General outline of configuration is inspired by [2].
    # [1] http://cmssw.cvs.cern.ch/cgi-bin/cmssw.cgi/UserCode/EGamma/EGammaAnalysisTools/python/electronIsolatorFromEffectiveArea_cfi.py?hideattic=0&revision=1.1.2.2&view=markup
    # [2] https://twiki.cern.ch/twiki/bin/viewauth/CMS/TwikiTopRefHermeticTopProjections?rev=4#Electrons
    #
    # In both real data and simulation an effective area derived from real data (2012 HCP dataset)
    # is applied. Possible difference between data and simulation is belived to be small [3-4]
    # [3] https://hypernews.cern.ch/HyperNews/CMS/get/top/1607.html
    # [4] https://hypernews.cern.ch/HyperNews/CMS/get/egamma/1263/1/2/1.html
    process.elPFIsoValueEA03 = cms.EDFilter('ElectronIsolatorFromEffectiveArea',
        gsfElectrons = cms.InputTag('gsfElectrons'),
        pfElectrons = cms.InputTag('pfSelectedElectrons'),
        rhoIso = cms.InputTag('kt6PFJets', 'rho'),
        EffectiveAreaType = cms.string('kEleGammaAndNeutralHadronIso03'),
        EffectiveAreaTarget = cms.string('kEleEAData2012'))
    process.patPF2PATSequence.replace(
        process.pfIsolatedElectrons,
        process.elPFIsoValueEA03 * process.pfIsolatedElectrons
    )
    process.pfIsolatedElectrons.isolationValueMapsNeutral = cms.VInputTag(cms.InputTag("elPFIsoValueNeutral03PFId"), cms.InputTag("elPFIsoValueGamma03PFId"))

    #process.pfIdentifiedElectrons = cms.EDFilter("ElectronIDPFCandidateSelector",
    #    recoGsfElectrons = cms.InputTag("gsfElectrons"),
    #    electronIdMap = cms.InputTag("mvaTrigV0"),
    #    electronIdCut = cms.double(0.0),
    #    src = cms.InputTag("pfSelectedElectrons")
    #)
    #process.pfSelectedElectrons.src = 'pfIdentifiedElectrons'
    #process.pfSelectedElectrons.cut = 'abs(eta)<2.5 && pt>20. && gsfTrackRef.isNonnull && gsfTrackRef.trackerExpectedHitsInner.numberOfLostHits<2'

    # Adjust parameters for the rho correction [1]. The cut on the isolation value is set in
    # accordance with [2]
    # [1] https://twiki.cern.ch/twiki/bin/viewauth/CMS/TwikiTopRefHermeticTopProjections?rev=4#Electrons
    # [2] https://twiki.cern.ch/twiki/bin/view/CMS/TWikiTopRefEventSel?rev=178#Veto
    process.pfIsolatedElectrons.doDeltaBetaCorrection = True
    process.pfIsolatedElectrons.deltaBetaFactor = -1.
    process.pfIsolatedElectrons.isolationCut = 0.15

    process.patPF2PATSequence.replace(
        process.pfSelectedElectrons,
        process.mvaTrigV0 +
        #process.pfIdentifiedElectrons +
        process.pfSelectedElectrons +
        process.elPFIsoValueEA03
    )

    process.patElectrons.isolationValues.user = cms.VInputTag(cms.InputTag("elPFIsoValueEA03"))
    process.patElectrons.electronIDSources = cms.PSet( mvaTrigV0 = cms.InputTag("mvaTrigV0"))

    # Release cuts on compatibility with the first primary vertex, as recommended in [1]
    # [1] https://hypernews.cern.ch/HyperNews/CMS/get/egamma-elecid/72/1.html
    process.pfElectronsFromVertex.d0Cut = 9999.
    process.pfElectronsFromVertex.d0SigCut = 9999.
    process.pfElectronsFromVertex.dzCut = 9999.
    process.pfElectronsFromVertex.dzSigCut = 9999.

    # Apply remaining cuts that define veto electrons as required in [1]. It is implemented via an
    # additional module and not in pfSelectedElectrons, becase all the isolation maps are associated
    # with the latter collection, and they will be needed also for a looser electron selection
    # [1] https://twiki.cern.ch/twiki/bin/view/CMS/TWikiTopRefEventSel?rev=178#Veto
    process.pfElectronsForTopProjection = process.pfSelectedElectrons.clone(
        src = "pfIsolatedElectrons",
        cut = "pt > 20. && abs(eta) < 2.5")
    process.pfNoElectron.topCollection = 'pfElectronsForTopProjection'

    process.patPF2PATSequence.replace(process.pfIsolatedElectrons,
        process.pfIsolatedElectrons * process.pfElectronsForTopProjection)

    #process.selectedPatElectrons.cut = "(abs(eta)<2.5) && (pt>20.) && ((chargedHadronIso + max(0.0, neutralHadronIso + photonIso - 1.0*userIsolation('User1Iso')))/pt < 0.15) && (electronID('mvaTrigV0') > 0.00)"

    process.patElectronsAll = process.patElectrons.clone(
        pfElectronSource=cms.InputTag("pfElectrons")
    )
    process.selectedPatElectronsAll = process.selectedPatElectrons.clone(
        src=cms.InputTag("patElectronsAll")
    )
    process.electronsWithIDAll = process.electronsWithID.clone(
        electronSrc = cms.InputTag("selectedPatElectronsAll")
    )

    process.electronSequence = cms.Sequence(
        process.patElectronsAll *
        process.selectedPatElectronsAll *
        process.electronsWithIDAll
    )

    #---------------------------------------------
    # Trigger matching
    #---------------------------------------------

    process.load('PhysicsTools.PatAlgos.triggerLayer1.triggerProducer_cfi')
    process.load('PhysicsTools.PatAlgos.triggerLayer1.triggerEventProducer_cfi')

    process.patTriggerSequence = cms.Sequence(
        process.patTrigger *
        process.patTriggerEvent
    )

    #-------------------------------------------------
    # Jets
    # MET corrections as https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookMetAnalysis#Type_I_0_with_PAT
    #-------------------------------------------------

    #Taus are NOT removed from jets
    process.pfNoTau.enable = False

    # From Andrey's code
    # Jet identification criteria as recommended in [1-2]. The fraction of neutral-hadron and
    # HF-hadron energy is defined below differently from the formula in [2]. However, the formula
    # is written for uncorrected jets, while JEC-corrected ones are used below. One can rescale the
    # jet energy in the formula, but the expression below yields the same result. All accessors to
    # energy fractions from PAT jets account for the effect of JEC
    # [1] https://twiki.cern.ch/twiki/bin/viewauth/CMS/JetID
    # [2] https://hypernews.cern.ch/HyperNews/CMS/get/JetMET/1429.html
    jetQualityCut = "numberOfDaughters > 1 & (neutralHadronEnergyFraction + HFHadronEnergyFraction) < 0.99 & neutralEmEnergyFraction < 0.99 & (abs(eta) < 2.4 & chargedEmEnergyFraction < 0.99 & chargedHadronEnergyFraction > 0. & chargedMultiplicity > 0 | abs(eta) >= 2.4)"

    # Apply the jet ID defined above to selected pat jets. It will be inherited by all the jet
    # collections considered in the analysis, including those produced by the MET uncertainty tool.
    # The latter is reasonable as we do not want to apply JEC variation, for instance, to fake jets
    process.selectedPatJets.cut = jetQualityCut

    process.load("CMGTools.External.pujetidsequence_cff")
    process.patPF2PATSequence += process.puJetIdSqeuence

    #-------------------------------------------------
    # MET uncertainty step
    #-------------------------------------------------
    #Embed the reference to the original jet in the jets, which is constant during the propagation
    process.patJetsWithOwnRef = cms.EDProducer('PatObjectOwnRefProducer<pat::Jet>',
            src=cms.InputTag("selectedPatJets")
    )

    #Note: this module causes a large memory increase when crossing the file boundary
    #Reason - unknown, solution: limit processing to ~1 file.
    from PhysicsTools.PatUtils.tools.metUncertaintyTools import runMEtUncertainties
    #for type 0

    process.load('JetMETCorrections.Type1MET.pfMETsysShiftCorrections_cfi')
    if options.isMC:
            corrpars = process.pfMEtSysShiftCorrParameters_2012runABCDvsNvtx_mc
    else:
            corrpars = process.pfMEtSysShiftCorrParameters_2012runABCDvsNvtx_data

    runMEtUncertainties(process,
             electronCollection=cms.InputTag("electronsWithID"),
             photonCollection=None,
             muonCollection=cms.InputTag("muonsWithID"),
             tauCollection="", # "" means emtpy, None means cleanPatTaus
             jetCollection=cms.InputTag("patJetsWithOwnRef"),
             jetCorrLabel="L3Absolute" if options.isMC else "L2L3Residual",
             doSmearJets=options.isMC and not options.doSync,
             #doSmearJets=False,
             jetCorrPayloadName="AK5PFchs",
             addToPatDefaultSequence=False,
             doApplyType0corr=True,
             doApplySysShiftCorr = True,
             makeType1corrPFMEt = True, makeType1p2corrPFMEt = False,
             sysShiftCorrParameter = corrpars
    )

    #process.selectedVerticesForMEtCorr.src = cms.InputTag("goodOfflinePrimaryVertices")

    process.metUncertaintySequence.replace(process.patType1CorrectedPFMet,
        process.type0PFMEtCorrection + process.patPFMETtype0Corr + process.pfMEtSysShiftCorrSequence + process.patType1CorrectedPFMet
    )

    #Switch off checking for overlaps between leptons and jets
    #process.patJetsWithOwnRefNotOverlappingWithLeptonsForMEtUncertainty.checkOverlaps = cms.PSet()
    #process.patJetsNotOverlappingWithLeptonsForMEtUncertainty.checkOverlaps = cms.PSet()

    process.stpolMetUncertaintySequence = cms.Sequence(
            process.metUncertaintySequence
    )

    if not options.doSlimming or options.doDebug:
            process.out.outputCommands = cms.untracked.vstring('keep *')
    else:
            process.out.outputCommands = cms.untracked.vstring([
                    'drop *',

                    'keep edmMergeableCounter_*_*_*', # Keep the lumi-block counter information
                    'keep edmTriggerResults_TriggerResults__*', #Keep the trigger results
                    'keep *_genParticles__*', #keep all the genParticles
                    #'keep recoVertexs_offlinePrimaryVertices__*', #keep the offline PV-s
                    'keep recoVertexs_goodOfflinePrimaryVertices__*', #keep the offline PV-s

                    # Trigger
                    'keep *_patTrigger_*_*',
                    'keep *_patTriggerEvent_*_*',

                    # Jets
                    'keep patJets_*__*',
                    'keep double_*_rho_*', #For rho-corr rel iso
                    'keep recoGenJets_selectedPatJets_genJets_*', #For Jet MC smearing we need to keep the genJets
                    "keep *_puJetId_*_*", # input variables
                    "keep *_puJetMva_*_*", # final MVAs and working point flags
                    'keep *_jetClones__*',

                    # Muons
                    'keep *_muons__*', #reco muons
                    'keep patMuons_muonsWithID__*',
                    'keep patMuons_muonsWithIDAll__*',
                    'keep *_muonClones__*',

                    # Electrons
                    'keep patElectrons_electronsWithID__*',
                    'keep patElectrons_electronsWithIDAll__*',
                    'keep *_electronClones__*',

                    # METs
                    'keep patMETs_*__*',

                    #ECAL laser corr filter
                    'keep bool_ecalLaserCorrFilter__*',

                    #For flavour analyzer
                    'keep GenEventInfoProduct_generator__*',

                    #PU info
                    'keep PileupSummaryInfos_addPileupInfo__*',

                    ##PFCandidates
                    #'keep recoPFCandidates_*_pfCandidates_PAT',
                    #'keep recoPFMETs_pfMET__*',
                    #'keep recoPFMETs_pfMet__*',
                    #'keep recoGenMETs_genMetTrue__*',
                    #'keep recoPFCandidates_particleFlow__*',
                    #'keep recoConversions_allConversions__*',
                    #'keep recoVertexCompositeCandidates_generalV0Candidates_*_*',
                    #'keep recoTracks_generalTracks__*',
                    #'keep recoBeamSpot_offlineBeamSpot__*',
                    #'keep recoMuons_muons__*',

                    'keep int_*__PAT',
                    'keep ints_*__PAT',
                    'keep double_*__PAT',
                    'keep doubles_*__PAT',
                    'keep float_*__PAT',
                    'keep floats_*__PAT',
            ])

    process.out.SelectEvents = cms.untracked.PSet(
        SelectEvents = cms.vstring(
            ["singleTopPathStep1Mu", "singleTopPathStep1Ele"] if options.doSkimming else ["*"]
        )
    )

    #-------------------------------------------------
    # Paths
    #-------------------------------------------------

    process.goodOfflinePVCount = cms.EDProducer(
            "CollectionSizeProducer<reco::Vertex>",
            src = cms.InputTag("goodOfflinePrimaryVertices")
    )

    process.preCalcSequences = cms.Sequence(
        process.patJetsWithOwnRef *
        process.goodOfflinePVCount
    )

    process.patPF2PATSequence.insert(process.patPF2PATSequence.index(process.selectedPatMuons) + 1, process.muonsWithID)
    process.patPF2PATSequence.insert(process.patPF2PATSequence.index(process.selectedPatElectrons) + 1, process.electronsWithID)

    #Need separate paths because of skimming
    process.singleTopSequence = cms.Sequence(
            process.goodOfflinePrimaryVertices
            * process.eventFiltersSequence
            * process.patPF2PATSequence
    )

    process.GlobalTag.globaltag = cms.string(options.globalTag)

    process.singleTopSequence += process.preCalcSequences
    process.singleTopSequence += process.stpolMetUncertaintySequence
    process.singleTopSequence += process.patTriggerSequence
    process.singleTopSequence += process.muonSequence
    process.singleTopSequence += process.electronSequence

    if options.isMC:
        #https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideBTagJetProbabilityCalibration?redirectedfrom=CMS.SWGuideBTagJetProbabilityCalibration#Calibration_in_53x_Data_and_MC
        process.GlobalTag.toGet = cms.VPSet(
            cms.PSet(record = cms.string("BTagTrackProbability2DRcd"),
            tag = cms.string("TrackProbabilityCalibration_2D_MC53X_v2"),
            connect = cms.untracked.string("frontier://FrontierPrep/CMS_COND_BTAU")),
            cms.PSet(record = cms.string("BTagTrackProbability3DRcd"),
            tag = cms.string("TrackProbabilityCalibration_3D_MC53X_v2"),
            connect = cms.untracked.string("frontier://FrontierPrep/CMS_COND_BTAU"))
        )
    else:
        #https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideBTagJetProbabilityCalibration?redirectedfrom=CMS.SWGuideBTagJetProbabilityCalibration#Calibration_in_53x_Data_and_MC
        process.GlobalTag.toGet = cms.VPSet(
            cms.PSet(record = cms.string("BTagTrackProbability2DRcd"),
            tag = cms.string("TrackProbabilityCalibration_2D_Data53X_v2"),
            connect = cms.untracked.string("frontier://FrontierPrep/CMS_COND_BTAU")),
            cms.PSet(record = cms.string("BTagTrackProbability3DRcd"),
            tag = cms.string("TrackProbabilityCalibration_3D_Data53X_v2"),
            connect = cms.untracked.string("frontier://FrontierPrep/CMS_COND_BTAU"))
        )

        #Filters added by a separate method
        #process.load('RecoMET.METFilters.ecalLaserCorrFilter_cfi')
        #process.ecalLaserCorrFilter.taggingMode=True

        # https://twiki.cern.ch/twiki/bin/viewauth/CMS/TWikiTopRefEventSel#Cleaning_Filters
        #process.scrapingFilter = cms.EDFilter("FilterOutScraping"
        #    , applyfilter = cms.untracked.bool(True)
        #    , debugOn = cms.untracked.bool(False)
        #    , numtrack = cms.untracked.uint32(10)
        #    , thresh = cms.untracked.double(0.25)
        #)

        #process.singleTopSequence += process.scrapingFilter
        #process.singleTopSequence += process.ecalLaserCorrFilter

    if options.doSkimming:
        process.out.fileName.setValue(process.out.fileName.value().replace(".root", "_Skim.root"))
    else:
        process.out.fileName.setValue(process.out.fileName.value().replace(".root", "_noSkim.root"))

    process.singleTopPathStep1Mu = cms.Path(process.singleTopSequence)
    process.singleTopPathStep1Ele = cms.Path(process.singleTopSequence)

    #process.chsalgos[0].tmvaWeights = cms.string('CMGTools/External/data/TMVAClassificationCategory_JetID_53X_chs_Dec2012.weights.xml')
    #process.chsalgos_5x[0].tmvaWeights = cms.string('CMGTools/External/data/TMVAClassificationCategory_JetID_53X_chs_Dec2012.weights.xml')

    #-----------------------------------------------
    # Skimming
    #-----------------------------------------------

    #Throw away events before particle flow?
    if options.doSkimming:
        from SingleTopPolarization.Analysis.eventSkimming_cfg import skimFilters
        skimFilters(process)
        process.singleTopPathStep1Mu.insert(0, process.muonSkim)
        process.singleTopPathStep1Ele.insert(0, process.electronSkim)

    #-----------------------------------------------
    # Skim efficiency counters
    #-----------------------------------------------

    #count all processed events
    countProcessed(process)

    #count events passing mu and ele paths
    countInSequence(process, process.singleTopPathStep1Mu)
    countInSequence(process, process.singleTopPathStep1Ele)

    if not options.doSlimming:
        process.out.fileName.setValue(process.out.fileName.value().replace(".root", "_noSlim.root"))

    return process
