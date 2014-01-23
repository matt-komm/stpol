
const sources = Dict{Any, Source}()

include("util.jl")
include("jet_cls.jl")

#see selection_step2_cfg.py for possible inputs
#leptons
for s in [:Pt, :Eta, :Phi, :relIso, :genPdgId, :Charge]
    sources[part(:muon, s)] = Source(:goodSignalMuonsNTupleProducer, s, :STPOLSEL2)
    sources[part(:electron, s)] = Source(:goodSignalElectronsNTupleProducer, s, :STPOLSEL2)
end

#jets
for s in [:Pt, :Eta, :Phi, :Mass, :partonFlavour, :bDiscriminatorCSV, :bDiscriminatorTCHP, :rms, :deltaR]
    sources[part(:bjet, s)] = Source(:highestBTagJetNTupleProducer, s, :STPOLSEL2)
    sources[part(:ljet, s)] = Source(:lowestBTagJetNTupleProducer, s, :STPOLSEL2)
    sources[part(:jets, s)] = Source(:goodJetsNTupleProducer, s, :STPOLSEL2)
end

sources[:cos_theta_lj] = Source(:cosTheta, :cosThetaLightJet, :STPOLSEL2, Float64)
sources[:cos_theta_bl] = Source(:cosTheta, :cosThetaEtaBeamline, :STPOLSEL2, Float64)
sources[:cos_theta_lj_gen] = Source(:cosThetaProducerTrueAll, :cosThetaLightJet, :STPOLSEL2, Float64)
sources[:cos_theta_bl_gen] = Source(:cosThetaProducerTrueAll, :cosThetaEtaBeamline, :STPOLSEL2, Float64)
sources[:met] = Source(:patMETNTupleProducer, :Pt, :STPOLSEL2)
sources[(:met, :phi)] = Source(:patMETNTupleProducer, :Phi, :STPOLSEL2)

sources[part(:muon, :mtw)] = Source(:muMTW, symbol(""), :STPOLSEL2, Float64)
sources[part(:electron, :mtw)] = Source(:eleMTW, symbol(""), :STPOLSEL2, Float64)
sources[:njets] = Source(:goodJetCount, symbol(""), :STPOLSEL2, Int32)
sources[:ntags] = Source(:bJetCount, symbol(""), :STPOLSEL2, Int32)
sources[:n_good_vertices] = Source(:goodOfflinePVCount, symbol(""), symbol(""), Int32)

sources[:nsignalmu] = Source(:muonCount, symbol(""), :STPOLSEL2, Int32)
sources[:nsignalele] = Source(:electronCount, symbol(""), :STPOLSEL2, Int32)

for s in [:Pt, :Eta, :Phi, :Mass]
    sources[part(:top, s)] = Source(:recoTopNTupleProducer, s, :STPOLSEL2)
end

for v in [:C, :D, :circularity, :isotropy, :sphericity, :aplanarity, :thrust]
    sources[v] = Source(:eventShapeVars, v, :STPOLSEL2, Float64)
end

sources[:wjets_cls] = Source(:flavourAnalyzer, :simpleClass, :STPOLSEL2, Uint32)

sources[part(:electron, :nu_soltype)] = Source(:recoNuProducerEle, :solType, :STPOLSEL2, Int32)
sources[part(:muon, :nu_soltype)] = Source(:recoNuProducerMu, :solType, :STPOLSEL2, Int32)

weight(a...) = (:weight, a...)

sources[weight(:pu)] = Source(:puWeightProducer, :PUWeightNtrue, :STPOLSEL2, Float64)
sources[weight(:pu, :up)] = Source(:puWeightProducer, :PUWeightNtrueUp, :STPOLSEL2, Float64)
sources[weight(:pu, :down)] = Source(:puWeightProducer, :PUWeightNtrueDown, :STPOLSEL2, Float64)

sources[weight(:btag)] = Source(:bTagWeightProducerNoCut, :bTagWeight, :STPOLSEL2, Float32)
sources[weight(:btag, :bc, :up)] = Source(:bTagWeightProducerNoCut, :bTagWeightSystBCUp, :STPOLSEL2, Float32)
sources[weight(:btag, :bc, :down)] = Source(:bTagWeightProducerNoCut, :bTagWeightSystBCDown, :STPOLSEL2, Float32)
sources[weight(:btag, :l, :up)] = Source(:bTagWeightProducerNoCut, :bTagWeightSystLUp, :STPOLSEL2, Float32)
sources[weight(:btag, :l, :down)] = Source(:bTagWeightProducerNoCut, :bTagWeightSystLDown, :STPOLSEL2, Float32)

sources[weight(:electron, :id)] = Source(:electronWeightsProducer, :electronIdIsoWeight, :STPOLSEL2, Float64)
sources[weight(:electron, :id, :up)] = Source(:electronWeightsProducer, :electronIdIsoWeightUp, :STPOLSEL2, Float64)
sources[weight(:electron, :id, :down)] = Source(:electronWeightsProducer, :electronIdIsoWeightDown, :STPOLSEL2, Float64)
sources[weight(:electron, :trigger)] = Source(:electronWeightsProducer, :electronTriggerWeight, :STPOLSEL2, Float64)
sources[weight(:electron, :trigger, :up)] = Source(:electronWeightsProducer, :electronTriggerWeightUp, :STPOLSEL2, Float64)
sources[weight(:electron, :trigger, :down)] = Source(:electronWeightsProducer, :electronTriggerWeightDown, :STPOLSEL2, Float64)

sources[weight(:muon, :id)] = Source(:muonWeightsProducer, :muonIDWeight, :STPOLSEL2, Float64)
sources[weight(:muon, :id, :up)] = Source(:muonWeightsProducer, :muonIDWeightUp, :STPOLSEL2, Float64)
sources[weight(:muon, :id, :down)] = Source(:muonWeightsProducer, :muonIDWeightDown, :STPOLSEL2, Float64)
sources[weight(:muon, :iso)] = Source(:muonWeightsProducer, :muonIsoWeight, :STPOLSEL2, Float64)
sources[weight(:muon, :iso, :up)] = Source(:muonWeightsProducer, :muonIsoWeightUp, :STPOLSEL2, Float64)
sources[weight(:muon, :iso, :down)] = Source(:muonWeightsProducer, :muonIsoWeightDown, :STPOLSEL2, Float64)
sources[weight(:muon, :trigger)] = Source(:muonWeightsProducer, :muonTriggerWeight, :STPOLSEL2, Float64)
sources[weight(:muon, :trigger, :up)] = Source(:muonWeightsProducer, :muonTriggerWeightUp, :STPOLSEL2, Float64)
sources[weight(:muon, :trigger, :down)] = Source(:muonWeightsProducer, :muonTriggerWeightDown, :STPOLSEL2, Float64)

sources[weight(:gen)] = Source(:genWeightProducer, :w, :STPOLSEL2, Float64)
sources[weight(:top)] = Source(:ttbarTopWeight, :weight, :STPOLSEL2, Float64)

vetolepton(s) = symbol("n_veto_lepton_$s")
sources[vetolepton(:mu)] = Source(:looseVetoMuCount, symbol(""), :STPOLSEL2, Int32)
sources[vetolepton(:ele)] = Source(:looseVetoEleCount, symbol(""), :STPOLSEL2, Int32)

const HLTS = {
    :mu => [
        "HLT_IsoMu24_eta2p1_v11",
        "HLT_IsoMu24_eta2p1_v12",
        "HLT_IsoMu24_eta2p1_v13",
        "HLT_IsoMu24_eta2p1_v14",
        "HLT_IsoMu24_eta2p1_v15",
        "HLT_IsoMu24_eta2p1_v17",
        "HLT_IsoMu24_eta2p1_v16",
    ],
    :ele => [
        "HLT_Ele27_WP80_v8",
        "HLT_Ele27_WP80_v9",
        "HLT_Ele27_WP80_v10",
        "HLT_Ele27_WP80_v11",
    ]
}

const hlts = vcat(collect(values(HLTS))...)
