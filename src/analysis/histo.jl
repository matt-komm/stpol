module Hist

using DataFrames
using DataArrays

using PyCall
@pyimport numpy
using PyPlot

import Base.+, Base.-, Base.*, Base./
immutable Histogram
    bin_entries::Vector{Float64} #n values
    bin_contents::Vector{Float64} #n values
    bin_edges::Vector{Float64} #n+1 values, lower edges of all bins + upper edge of last bin

    function Histogram(entries, contents, edges)
        @assert length(entries)==length(contents) "entries and contents vector must be of equal length"
        if (length(entries)!=length(edges)-1)
            error("must specify n+1 edges, $(length(entries))!=$(length(edges)-1)")
        end
        @assert all(entries .>= 0.0) "number of entries must be >= 0"
        new(entries, contents, edges)
    end
end

function Histogram(n::Integer, low::Number, high::Number)
    bins = linspace(low, high, n)
    unshift!(bins, -inf(Float64))
    push!(bins, inf(Float64))
    n_contents = size(bins,1)-1
    return Histogram(
        zeros(Float64, (n_contents, )),
        zeros(Float64, (n_contents, )),
        bins
    )
end

Histogram(h::Histogram) = Histogram(h.bin_entries, h.bin_contents, h.bin_edges)

function errors(h::Histogram)
    return h.bin_contents ./ sqrt(h.bin_entries)
end

function findbin(h::Histogram, v::Real)
    v < h.bin_edges[1] && return -Inf
    v >= h.bin_edges[length(h.bin_edges)] && return +Inf

    idx = searchsorted(h.bin_edges, v)
    low = idx.start-1
    return low
end

function hfill!(h::Histogram, v::Real, w::Real=1.0)
    low = findbin(h, v)
    abs(low) == Inf && error("over- or underflow for $v")

    h.bin_entries[low] += 1
    h.bin_contents[low] += w
    return sum(h.bin_contents)
end

function hfill!(h::Histogram, v::NAtype, w::Union(Real, NAtype))
    h.bin_entries[1] += 1
    h.bin_contents[1] += 1
    return sum(h.bin_contents)
end

function +(h1::Histogram, h2::Histogram)
    @assert h1.bin_edges == h2.bin_edges
    h = Histogram(h1.bin_entries + h2.bin_entries, h1.bin_contents+h2.bin_contents, h1.bin_edges)
    return h
end

-(h1::Histogram, h2::Histogram) = h1 + (-1.0 * h2)

function *{T <: Real}(h1::Histogram, x::T)
    return Histogram(h1.bin_entries, h1.bin_contents * x, h1.bin_edges)
end

function *{T <: Real}(x::T, h1::Histogram)
    return h1 * x
end


function /{T <: Real}(h1::Histogram, x::T)
    return h1 * (1.0/x)
end

function /(h1::Histogram, h2::Histogram)
    #warn("ratio plot errors are currently incorrect")
    @assert(h1.bin_edges == h2.bin_edges, "bin edges must be the same for both histograms")
    div = h1.bin_contents ./ h2.bin_contents
    #div = Float64[d >= 0.0 ? d : 0.0 for d in div]

    ent = (h1.bin_entries ./ h1.bin_contents) .^ 2 + (h2.bin_entries ./ h2.bin_contents) .^ 2
    #ent = Float64[x >= 0.0 ? x : 0.0 for x in ent]

    return Histogram(
        ent,
        div,
        h1.bin_edges
    )
end

function integral(h::Histogram)
    return sum(h.bin_contents)
end

function integral(h::Histogram, x1::Real, x2::Real)
    if !(x1 in h.bin_edges) || !(x2 in h.bin_edges)
        warn("integration will be inexact due to binning")
    end
    a = searchsorted(h.bin_edges, x1).start
    b = searchsorted(h.bin_edges, x2).start
    return sum(h.bin_contents[a:b])
end

#returns the low edges of a list of histogram edges
lowedge(arr) = arr[1:length(arr)-1];
widths(arr) = [arr[i+1]-arr[i] for i=1:length(arr)-1]

function normed{T <: Histogram}(h::T)
    i = integral(h)
    return i > 0 ? h/i : error("histogram integral was $i")
end

#conversion to dataframe
#todf(h::Histogram) = DataFrame(bin_edges=h.bin_edges, bin_contents=h.bin_contents, bin_entries=h.bin_entries)

#assumes df columns are entries, contents, edges
#length(entries) = length(contents) = length(edges) - 1, edges are lower, lower, lower, ..., upper
function fromdf(df::DataFrame; entries=:entries)
    ent = df[1].data[1:nrow(df)-1]
    cont = df[2].data[1:nrow(df)-1]
    if entries == :poissonerrors
        ent = (cont ./ ent ) .^ 2
        ent = Float64[x > 0 ? x : 0 for x in ent]
    elseif entries == :entries
        ent = ent
    else
        error("unknown value for keyword :entries=>$(entries)")
    end

    Histogram(
        ent, #entries
        cont, #contents
        df[3].data #edges
    )
end

histogramdd(args...;kwargs...) = numpy.histogramdd(args..., kwargs...);
flatten(h) = reshape(h, prod(size(h)))

function hplot(ax::PyObject, h::Histogram, prevhist::Histogram;kwargs...)
    kwargsd = {k=>v for (k, v) in kwargs}

    nbins = length(kwargs)
    #in case of log scale, low bins must be \eps; otherwise 0,0,0,...,0 or lower
    if (:log in keys(kwargsd) && kwargsd[:log])
        prevbins = [x > 0 ? x : 1 for x in prevhist.bin_contents]
    else
        prevbins = prevhist.bin_contents
    end

    ax[:bar](lowedge(h.bin_edges), h.bin_contents, widths(h.bin_edges), prevbins; kwargs...)
end

function hplot{T <: Number}(ax::PyObject, h::Histogram, prevval::T;kwargs...)
    prevh = Histogram(
        Float64[1 for i=1:length(h.bin_entries)],
        Float64[convert(Float64, prevval) for i=1:length(h.bin_entries)],
        h.bin_edges
    )
    hplot(ax, h, prevh; kwargs...)
end

function hplot(ax::PyObject, h::Histogram; kwargs...)
    return hplot(ax, h, 0.0*h; kwargs...)
end

function hplot(ax::PyObject, hists::Vector{Histogram}, args=Dict[]; common_args=Dict(), kwargs...)
    ret = Any[]
    kwd = {k=>v for (k,v) in kwargs}
    for i=1:length(hists)

        h = hists[i]
        
        arg = i <= length(args) ? args[i] : Dict()
        argd = {k=>v for (k, v) in merge(arg, common_args, kwd)}

        if !haskey(argd, :color)
            argd[:color] = ax[:_get_lines][:color_cycle][:next]()
        end

        prevh = i>1 ? sum(hists[1:i-1]) : 0.0
        r = hplot(ax, h, prevh; argd...)
        
        push!(ret, r)
    end
    return ret
end

function eplot{T <: Histogram}(ax::PyObject, h::T;kwargs...)
    #ax[:plot](midpoints(h.bin_edges), h.bin_contents; kwargs...)
    ax[:errorbar](midpoints(h.bin_edges), h.bin_contents, errors(h); kwargs...)
end


function eplot{T <: Histogram}(ax::PyObject, hs::Vector{T};kwargs...)
   rets = Any[]
   for h in hs
        r = eplot(ax, h; kwargs...)
        push!(rets, r)
   end
   return rets
end

export Histogram, hfill!, hplot, integral, normed, errors, findbin
export +, -, *, /
export todf, fromdf
export histogramdd, flatten

export hplot, eplot

end #module

if "--test" in ARGS
    using Hist
    h = Histogram([1,2], [2.0,3.0], [0,1,2])
    d = h / h
    m = h - h
    println(d)
    println(m)
    m / d
end

