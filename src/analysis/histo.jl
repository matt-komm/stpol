module Hist

using DataFrames
using PyCall

@pyimport numpy

import Base.+, Base.*, Base./
immutable Histogram
    bin_entries::Vector{Int64}
    bin_contents::Vector{Float64}
    bin_edges::Vector{Float64}
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

function *(h1::Histogram, x::Real)
    return Histogram(h1.bin_entries, h1.bin_contents * x, h1.bin_edges)
end

function /(h1::Histogram, x::Real)
    return h1 * (1.0/x)
end

function integral(h::Histogram)
    return sum(h.bin_contents)
end

function integral(h::Histogram, x1::Real, x2::Real)
    a = searchsorted(h.bin_edges, x1).start
    b = searchsorted(h.bin_edges, x2).start
    return sum(h.bin_contents[a:b])
end

function norm!(h::Histogram)
    i = integral(h)
    return i > 0 ? h/i : error("histogram integral was $i")
end

#conversion to dataframe
todf(h::Histogram) = DataFrame(bin_edges=h.bin_edges, bin_contents=h.bin_contents, bin_entries=h.bin_entries)
fromdf(df::DataFrame) = Histogram(df[:, :bin_entries].data, df[:, :bin_contents].data, df[:, :bin_edges].data)

histogramdd(args...;kwargs...) = numpy.histogramdd(args..., kwargs...);
flatten(h) = reshape(h, prod(size(h)))

export Histogram, hfill!, hplot, integral, norm!
export +, *, /
export todf, fromdf
export histogramdd, flatten
end #module
