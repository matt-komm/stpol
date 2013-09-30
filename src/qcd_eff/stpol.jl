include("data.jl")

module SingleTop

using ROOT
using SingleTopData
using DataFrames

function make_backend(t::Type, s::Symbol)
    sources = Dict{Symbol, Source}()

    for name in names(t)
        sources[name] = Source(s, name, PROCESS)
    end

    return sources
end

const backends = {
    :signal_muon => make_backend(Lepton, :goodSignalMuonsNTupleProducer),
    :jets => make_backend(Jet, :goodJetsNTupleProducer)
}

const particle_types = {
    :signal_muon => Lepton,
    :jets => Jet
}

function get_particles(events::Events, particle::Symbol)    
    sources::Dict{Symbol, Source} = backends[particle]

    particles = particle_types[particle][]


    datas = Dict{Symbol, DataArray}()
    for (name, s) in sources
        datas[name] = DataArray(events[s])
        if length(datas[name])==0
            return particles
        end
    end

    assert(length(datas)>0)
    l = length(collect(values(datas))[1])

    for (k, d) in datas
        assert(length(d)==l, "Data array length should be $l but is $(length(d)): $datas")
    end

    for i=1:l
        pars = [datas[name][i] for name in names(particle_types[particle])]
        part = particle_types[particle](pars...)
        push!(particles, part)
    end
    return particles
end

end #module SingleTop

