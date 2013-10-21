module Hist

using DataFrames

import Base.+
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

#conversion to dataframe
todf(h::Histogram) = DataFrame(bin_edges=h.bin_edges, bin_contents=h.bin_contents, bin_entries=h.bin_entries)
fromdf(df::DataFrame) = Histogram(df[:, :bin_entries].data, df[:, :bin_contents].data, df[:, :bin_edges].data)

export Histogram, hfill!, +, hplot
export todf, fromdf
end #module