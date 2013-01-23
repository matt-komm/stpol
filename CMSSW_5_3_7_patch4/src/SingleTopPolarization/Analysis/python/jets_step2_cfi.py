import FWCore.ParameterSet.Config as cms
from SingleTopPolarization.Analysis.calibrations_cfg import Calibrations

def JetSetup(process, conf):

#    if cutJets:
#        print "CUT\tJets: Using %d jets, %d tags" % (nJets, nBTags)
#    else:
#        print "CUT\tJets: keeping all events with >=1 jet and >=0 btag"
#
#    if conf.isMC:
#        jetCut = 'userFloat("pt_smear") > %f' % conf.Jets.ptCut
#    else:

    jetCut = 'pt > %f' % conf.Jets.ptCut

    jetCut += ' && abs(eta) < %f' % conf.Jets.etaCut
    jetCut += ' && numberOfDaughters > 1'
    jetCut += ' && neutralHadronEnergyFraction < 0.99'
    jetCut += ' && neutralEmEnergyFraction < 0.99'
    jetCut += ' && (chargedEmEnergyFraction < 0.99 || abs(eta) >= 2.4)'
    jetCut += ' && (chargedHadronEnergyFraction > 0. || abs(eta) >= 2.4)'
    jetCut += ' && (chargedMultiplicity > 0 || abs(eta) >= 2.4)'

#    process.skimJets = cms.EDFilter("CandViewSelector",
#        src=cms.InputTag(conf.Jets.source),
#        cut=cms.string('pt>15')
#    )

    if(conf.Jets.source == "selectedPatJets"):
        process.noPUJets = cms.EDProducer('CleanNoPUJetProducer',
            jetSrc = cms.InputTag(conf.Jets.source),
            PUidMVA = cms.InputTag("puJetMva", "fullDiscriminant", "PAT"),
            PUidFlag = cms.InputTag("puJetMva", "fullId", "PAT"),
            PUidVars = cms.InputTag("puJetId", "", "PAT"),
        )


#    if conf.isMC:
#        process.smearedJets = cms.EDProducer('JetMCSmearProducer',
#            src=cms.InputTag("noPUJets"),
#            reportMissingGenJet=cms.untracked.bool(conf.doDebug)
#        )

    bTagCutStr = 'bDiscriminator("%s") >= %f' % (conf.Jets.bTagDiscriminant, conf.Jets.BTagWorkingPointVal())

    process.goodJets = cms.EDFilter("CandViewSelector",
        src=cms.InputTag("noPUJets" if conf.Jets.source == "selectedPatJets" else conf.Jets.source),
        cut=cms.string(jetCut)
    )

    #B-tagging efficiencies

    #B-jet b-tagging efficiency
    process.trueBJets = cms.EDFilter("CandViewSelector",
        src=cms.InputTag("goodJets"),
        cut=cms.string("abs(partonFlavour()) == 5")
    )
    process.btaggedTrueBJets = cms.EDFilter(
        "CandViewSelector",
        src=cms.InputTag("trueBJets"),
        cut=cms.string(bTagCutStr)
    )
    process.trueBJetCount = cms.EDProducer(
        "CollectionSizeProducer<reco::Candidate>",
        src = cms.InputTag("trueBJets")
    )
    process.btaggedTrueBJetCount = cms.EDProducer(
        "CollectionSizeProducer<reco::Candidate>",
        src = cms.InputTag("btaggedTrueBJets")
    )
    process.bJetBTagEffSequence = cms.Sequence(
        process.trueBJets *
        process.btaggedTrueBJets *
        process.trueBJetCount *
        process.btaggedTrueBJetCount
    )

    #C-jet b-tagging efficiency
    process.trueCJets = cms.EDFilter("CandViewSelector",
        src=cms.InputTag("goodJets"),
        cut=cms.string("abs(partonFlavour()) == 4")
    )
    process.btaggedTrueCJets = cms.EDFilter(
        "CandViewSelector",
        src=cms.InputTag("trueCJets"),
        cut=cms.string(bTagCutStr)
    )
    process.trueCJetCount = cms.EDProducer(
        "CollectionSizeProducer<reco::Candidate>",
        src = cms.InputTag("trueCJets")
    )
    process.btaggedTrueCJetCount = cms.EDProducer(
        "CollectionSizeProducer<reco::Candidate>",
        src = cms.InputTag("btaggedTrueCJets")
    )
    process.cJetBTagEffSequence = cms.Sequence(
        process.trueCJets *
        process.btaggedTrueCJets *
        process.trueCJetCount *
        process.btaggedTrueCJetCount
    )

    #light-jet b-tagging efficiency
    process.trueLJets = cms.EDFilter("CandViewSelector",
        src=cms.InputTag("goodJets"),
        cut=cms.string("abs(partonFlavour()) <= 3")
    )
    process.btaggedTrueLJets = cms.EDFilter(
        "CandViewSelector",
        src=cms.InputTag("trueLJets"),
        cut=cms.string(bTagCutStr)
    )
    process.trueLJetCount = cms.EDProducer(
        "CollectionSizeProducer<reco::Candidate>",
        src = cms.InputTag("trueLJets")
    )
    process.btaggedTrueLJetCount = cms.EDProducer(
        "CollectionSizeProducer<reco::Candidate>",
        src = cms.InputTag("btaggedTrueLJets")
    )
    process.lightJetBTagEffSequence = cms.Sequence(
        process.trueLJets *
        process.btaggedTrueLJets *
        process.trueLJetCount *
        process.btaggedTrueLJetCount
    )


    process.trueLJets = cms.EDFilter("CandViewSelector",
        src=cms.InputTag("goodJets"),
        cut=cms.string("abs(partonFlavour()) <= 3")
    )


    process.btaggedJets = cms.EDFilter(
        "CandViewSelector",
        src=cms.InputTag("goodJets"),
        cut=cms.string(bTagCutStr)
    )

    process.bJetCount = cms.EDProducer(
        "CollectionSizeProducer<reco::Candidate>",
        src = cms.InputTag("btaggedJets")
    )

    #invert the b-tag cut
    process.untaggedJets = cms.EDFilter(
        "CandViewSelector",
        src=cms.InputTag("goodJets"),
        cut=cms.string(bTagCutStr.replace(">=", "<"))
    )

    process.lightJetCount = cms.EDProducer(
        "CollectionSizeProducer<reco::Candidate>",
        src = cms.InputTag("untaggedJets")
    )

    #Select the most forward untagged jet by absolute eta
    process.fwdMostLightJet = cms.EDFilter(
        'LargestAbsEtaCandViewProducer',
        src = cms.InputTag("untaggedJets"),
        maxNumber = cms.uint32(1)
    )

    process.highestBTagJet = cms.EDFilter(
        'LargestBDiscriminatorJetViewProducer',
        src = cms.InputTag("btaggedJets"),
        maxNumber = cms.uint32(1),
        bDiscriminator = cms.string(conf.Jets.bTagDiscriminant),
        reverse = cms.bool(False)
    )

    #Take the jet with the lowest overall b-discriminator value as the light jet
    process.lowestBTagJet = process.highestBTagJet.clone(
        src = cms.InputTag("untaggedJets"),
        reverse = cms.bool(True)
    )

    #Require exactly N jets if cutting on jets, otherwise 1...4 jets
    process.nJets = cms.EDFilter(
        "PATCandViewCountFilter",
        src=cms.InputTag("goodJets"),
        minNumber=cms.uint32(conf.Jets.nJets if conf.Jets.cutJets else 2),
        maxNumber=cms.uint32(conf.Jets.nJets if conf.Jets.cutJets else 4),
    )

    #Require exactly M bTags, otherwise 1...3 bJets
    process.mBTags = cms.EDFilter(
        "PATCandViewCountFilter",
        src=cms.InputTag("btaggedJets"),
        minNumber=cms.uint32(conf.Jets.nBTags if conf.Jets.cutJets else 1),
        maxNumber=cms.uint32(conf.Jets.nBTags if conf.Jets.cutJets else 3),
    )

    #Require at least 1 untagged jet
    process.oneUntaggedJet = cms.EDFilter(
        "PATCandViewCountFilter",
        src=cms.InputTag("untaggedJets"),
        minNumber=cms.uint32(1),
        maxNumber=cms.uint32(9999999),
    )

    sampleBEffs = Calibrations.bTaggingEfficiencies[Config.subChannel]
    process.bTagWeightProducer = cms.EDProducer('BTagSystematicsWeightProducer',
        src=cms.InputTag("goodJets"),
        nJets=cms.uint32(conf.Jets.nJets),
        nTags=cms.uint32(conf.Jets.nBTags),
        effB=cms.double(sampleBEffs.eff_b),
        effC=cms.double(sampleBEffs.eff_c),
        effL=cms.double(sampleBEffs.eff_l)
    )


    process.jetSequence = cms.Sequence(
      #process.skimJets *
      #process.noPUJets *
      process.goodJets *

      #B-jet efficiency counters
      process.bJetBTagEffSequence *
      process.cJetBTagEffSequence *
      process.lightJetBTagEffSequence *

      process.btaggedJets *
      process.untaggedJets *
      process.oneUntaggedJet *
      process.bJetCount *
      process.lightJetCount *
      process.fwdMostLightJet *
      process.highestBTagJet *
      process.lowestBTagJet *
      process.bTagWeightProducer
    )

    if conf.Jets.source == "selectedPatJets":
        process.jetSequence.insert(0, process.noPUJets)

    print "goodJets cut = %s" % process.goodJets.cut
    print "btaggedJets cut = %s" % process.btaggedJets.cut

    #if conf.isMC:
    #    process.jetSequence.insert(process.jetSequence.index(process.noPUJets)+1, process.smearedJets)
    if conf.doDebug:
        process.sourceJetAnalyzer = cms.EDAnalyzer("SimpleJetAnalyzer", interestingCollections=cms.untracked.VInputTag(conf.Jets.source))
        process.jetSequence.insert(0, process.sourceJetAnalyzer)
        process.jetAnalyzer = cms.EDAnalyzer("SimpleJetAnalyzer", interestingCollections=cms.untracked.VInputTag(conf.Jets.source, "goodJets"))
        process.jetSequence += process.jetAnalyzer

    print process.jetSequence
