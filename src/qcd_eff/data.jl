
module SingleTopData

using DataFrames
const PROCESS = :STPOLSEL2

module Sources
const mu = :goodSignalMuonsNTupleProducer
const jets = :goodJetsNTupleProducer
end


abstract Particle
import DataFrames.baseval
function baseval{T <: Particle}(s::Type{T})
    return T()
end

function to_df{T <: Particle}(x::T)
    d = {string(name) => getfield(x, name) for name in names(x)}
    return DataFrame(d)
end

function to_df{T <: Particle}(xs::Vector{T})
    d = {string(name) => [getfield(x, name) for x in xs] for name in names(typeof(xs).parameters[1])}
    return DataFrame(d)
end

function from_df{T <: Particle}(df::DataFrame, t::Type{T})
    nrows = size(df)[1]
    if size(df)[2] != length(names(t))
        throw("dataframe is wrong size: $(size(df)) =/= $(length(names(t)))")
    end

    return [t([df[n, string(name)] for name in names(t)]...) for n=1:nrows]
end

dtype_particle = Union(NAtype, Real)

immutable Lepton <: Particle
    Pt::dtype_particle
    Eta::dtype_particle
    Phi::dtype_particle
    relIso::dtype_particle
end
Lepton() = Lepton(NA, NA, NA, NA)

immutable Jet <: Particle
    Pt::dtype_particle
    Eta::dtype_particle
    Phi::dtype_particle
    deltaR::dtype_particle
    bDiscriminatorTCHP::dtype_particle
    rms::dtype_particle
end
Jet() = Jet(NA, NA, NA, NA, NA, NA)

export Particle, Lepton, Jet
export PROCESS

end #module

# using SingleTopData
# using DataFrames
# using Base.Test

# @test Lepton(NA, 1.0, 1.0, 1.0).Pt |> isna
# @test SingleTopData.to_df(Lepton(1.0, 2.0, 3.0, 4.0))[1, "Pt"] == 1.0

# @test begin
#     lep = Lepton(1.0, 2.0, 3.0, 4.0)
#     df = SingleTopData.to_df(lep)
#     lep1 = SingleTopData.from_df(df, Lepton)[1]
#     return lep == lep1
# end

# @test begin
#     lep1 = Lepton(1.0, 2.0, 3.0, 4.0)
#     lep2 = Lepton(2.0, 3.0, 4.0, 5.0)
#     df = SingleTopData.to_df([lep1, lep2])
#     return SingleTopData.from_df(df, Lepton) == [lep1, lep2]
# end