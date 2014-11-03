import Base.convert

immutable HistKey
    object::Symbol
    sample::Symbol
    iso::Symbol
    systematic::Symbol
    scenario::Symbol
    selection_major::Symbol
    selection_minor::Symbol
    lepton::Symbol
    njets::Int64
    ntags::Int64
end

Base.convert{T<:String}(t::Type{Int64}, x::T) = int64(x)

function HistKey(d::Associative)
    args = Any[]
    for (name, t) in zip(names(HistKey), HistKey.types)
        push!(args, convert(t, d[name]))
    end
    HistKey(args...)
end

tostr(hk::HistKey) = join([string("$(n)=", getfield(hk, n)) for n in names(hk)], ";")