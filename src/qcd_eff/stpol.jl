module SingleTop

using ROOT

const process = :STPOLSEL2

module Sources
const mu = :goodSignalMuonsNTupleProducer
const jets = :goodJets
end
#using .Sources

immutable SingleTopEvent
end

abstract Particle

type Lepton <: Particle
    pt::Source
    eta::Source
    phi::Source
    iso::Source
end

function Lepton(s::Symbol)
    p = Lepton(
        Source(s, :Pt, process),
        Source(s, :Eta, process),
        Source(s, :Phi, process),
        Source(s, :relIso, process)
    )
    return p
end

type Jet <: Particle
    pt::Source
    eta::Source
    phi::Source
end

function Jet(s::Symbol)
    return Jet(
        Source(s, :Pt, process),
        Source(s, :Eta, process),
        Source(s, :Phi, process),
    )
end

signal_mu = SingleTop.Lepton(SingleTop.Sources.mu)
jets = SingleTop.Jet(SingleTop.Sources.jets)

end #module SingleTop

