module Hist

using DataFrames
using DataArrays

using PyCall
@pyimport numpy

using PyPlot

import Base.+, Base.-, Base.*, Base./
immutable Histogram
    bin_entries::Vector{Int64} #n values
    bin_contents::Vector{Float64} #n values
    bin_edges::Vector{Float64} #n+1 values, lower edges of all bins + upper edge of last bin

    function Histogram(entries, contents, edges)
        @assert length(entries)==length(contents) "entries and contents vector must be of equal length"
        @assert length(entries)==length(edges)-1 "must specify n+1 edges"
        @assert all(entries .>= 0.0) "number of entries must be >= 0"
        new(entries, contents, edges)
    end
end

function Histogram(n::Integer, low::Number, high::Number)
    bins = linspace(low, high, n+1)
    unshift!(bins, -inf(Float64))
    n_contents = size(bins,1)
    return Histogram(
        zeros(Int64, (n_contents, )),
        zeros(Float64, (n_contents, )),
        bins
    )
end

Histogram(h::Histogram) = Histogram(h.bin_entries, h.bin_contents, h.bin_edges)

function errors(h::Histogram)
    return h.bin_contents .* sqrt(h.bin_entries) ./ h.bin_entries
end

function hfill!(h::Histogram, v::Real, w::Real=1.0)
    idx = searchsorted(h.bin_edges, v)
    low = idx.start-1
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
    return Histogram(h1.bin_entries, h1.bin_contents ./ h2.bin_contents, h1.bin_edges)
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

function normed(h::Histogram)
    i = integral(h)
    return i > 0 ? h/i : error("histogram integral was $i")
end

#conversion to dataframe
todf(h::Histogram) = DataFrame(bin_edges=h.bin_edges, bin_contents=h.bin_contents, bin_entries=h.bin_entries)
fromdf(df::DataFrame) = Histogram(df[:, :bin_entries].data, df[:, :bin_contents].data, df[:, :bin_edges].data)

histogramdd(args...;kwargs...) = numpy.histogramdd(args..., kwargs...);
flatten(h) = reshape(h, prod(size(h)))

function hplot(figure::PyObject, h::Histogram, prevhist::Histogram;kwargs...)
    figure[:bar](lowedge(h.bin_edges), h.bin_contents, widths(h.bin_edges), prevhist.bin_contents; kwargs...)
end

function eplot(figure::PyObject, h::Histogram;kwargs...)
    #figure[:plot](midpoints(h.bin_edges), h.bin_contents; kwargs...)
    figure[:errorbar](midpoints(h.bin_edges), h.bin_contents, errors(h); kwargs...)
end


function eplot(figure::PyObject, hs::Vector{Histogram};kwargs...)
   for h in hs
        eplot(figure, h; kwargs...)
   end
end

function hplot{T <: Number}(figure::PyObject, h::Histogram, prevval::T;kwargs...)
    prevh = Histogram(
        Int64[1 for i=1:length(h.bin_entries)],
        Float64[convert(Float64, prevval) for i=1:length(h.bin_entries)],
        h.bin_edges
    )
    hplot(figure, h, prevh; kwargs...)
end

function hplot(figure::PyObject, h::Histogram; kwargs...)
    return hplot(figure, h, 0.0*h; kwargs...)
end

function hplot(figure::PyObject, hists::Vector{Histogram}, args=Dict[]; common_args=Dict())
    ret = Any[]
    for i=1:length(hists)

        h = hists[i]
        
        arg = i <= length(args) ? args[i] : Dict()
        argd = {k=>v for (k, v) in merge(arg, common_args)}

        if !haskey(argd, :color)
            argd[:color] = figure[:_get_lines][:color_cycle][:next]()
        end

        prevh = i>1 ? sum(hists[1:i-1]) : 0.0

        r = hplot(figure, h, prevh; argd...)
        
        push!(ret, r)
    end
    return ret
end

export Histogram, hfill!, hplot, integral, normed, errors
export +, -, *, /
export todf, fromdf
export histogramdd, flatten

export hplot, eplot

end #module
