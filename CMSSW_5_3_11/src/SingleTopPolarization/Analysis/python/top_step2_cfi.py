import FWCore.ParameterSet.Config as cms

def TopRecoSetup(process, leptonSource="goodSignalLeptons", bTagSource="highestBTagJet", untaggedJetSource="lowestBTagJet"):
	#Reconstruct the 4-momentum of the top quark by adding the momenta of the b-jet, the neutrino and the charged lepton

	#Combine the neutrino collections produced in the electron and muon paths, taking exactly 1 neutrino per event
	process.recoNu = cms.EDProducer(
		 'CandRefCombiner',
		 sources=cms.untracked.vstring(["recoNuProducerMu", "recoNuProducerEle"]),
			 maxOut=cms.untracked.uint32(1),
			 minOut=cms.untracked.uint32(1)
	)

	process.recoTop = cms.EDProducer('SimpleCompositeCandProducer',
		sources=cms.VInputTag(["recoNu", bTagSource, leptonSource])
	)

	process.topCount = cms.EDProducer('CollectionSizeProducer<reco::Candidate>',
		src = cms.InputTag('recoTop')
	)

	process.cosTheta = cms.EDProducer('CosThetaProducer',
		topSrc=cms.InputTag("recoTop"),
		jetSrc=cms.InputTag(untaggedJetSource),
		leptonSrc=cms.InputTag("goodSignalLeptons")
	)

	process.topRecoSequenceMu = cms.Sequence(
      process.recoNuProducerMu *
      process.recoNu *
	  process.recoTop *
	  process.topCount *
	  process.cosTheta
	)

	process.topRecoSequenceEle = cms.Sequence(
      process.recoNuProducerEle *
      process.recoNu *
	  process.recoTop *
	  process.topCount *
	  process.cosTheta
	)
