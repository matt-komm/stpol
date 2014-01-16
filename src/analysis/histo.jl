module Hist

using DataFrames

import Base.+, Base.-, Base.*, Base./, Base.==
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
# function Histogram(edges::AbstractArray)
#     hist, bins = numpy.histogramdd([[0.0 for x=1:length(edges)]], edges)
#     return Histogram(0 * flatten(hist), 0 * flatten(hist), bins[1])
# end

function errors(h::Histogram)
    return h.bin_contents ./ sqrt(h.bin_entries)
end

function findbin(h::Histogram, v::Real)
    v < h.bin_edges[1] && return -Inf
    v >= h.bin_edges[length(h.bin_edges)] && return +Inf
    isnan(v) && return 1

    idx = searchsorted(h.bin_edges, v)
    low = idx.start-1
    if (low<1 || low>length(h.bin_entries))
        error("bin index out of range: i=$(low), v=$(v)")
    end
    return low
end

function hfill!(h::Histogram, v::Real, w::Real=1.0)
    low = findbin(h, v)
    
    if isnan(w)
        w = 0.0
    end

    abs(low) == Inf && error("over- or underflow for $v")

    h.bin_entries[low] += 1
    h.bin_contents[low] += w
    return sum(h.bin_contents)
end

function hfill!(h::Histogram, v::NAtype, w::Union(Real, NAtype)=1.0)
    h.bin_entries[1] += 1
    h.bin_contents[1] += 1
    return sum(h.bin_contents)
end

function hfill!(h::Histogram, v::Real, w::NAtype=NA)
    h.bin_entries[1] += 1
    h.bin_contents[1] += 1
    return sum(h.bin_contents)
end

function +(h1::Histogram, h2::Histogram)
    @assert h1.bin_edges == h2.bin_edges
    h = Histogram(h1.bin_entries + h2.bin_entries, h1.bin_contents+h2.bin_contents, h1.bin_edges)
    return h
end

function +(h1::Histogram, x::Real)
    nb = length(h1.bin_entries)
    h2 = Histogram([0.0 for n=1:nb], [x for n=1:nb], h1.bin_edges)
    return h1+h2
end

+(x::Real, h1::Histogram) = h1+x

function ==(h1::Histogram, h2::Histogram)
    ret = h1.bin_edges == h2.bin_edges
    ret = ret && (h1.bin_contents==h2.bin_contents)
    ret = ret && (h1.bin_entries==h2.bin_entries)
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

integral(h::Histogram) = sum(h.bin_contents)
integral(x::Real) = x
nentries(h::Histogram) = int(sum(h.bin_entries))


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
todf(h::Histogram) = DataFrame(
    bin_edges=h.bin_edges,
    bin_contents=vcat(h.bin_contents, 0),
    bin_entries=vcat(h.bin_entries, 0)
)

#function fromdf(df::DataFrame)
#    edges = df[1]
#    conts = df[2][1:nrow(df)-1]
#    entries = df[3][1:nrow(df)-1]
#    return Histogram(entries, conts, edges)
#end

#assumes df columns are entries, contents, edges
#length(entries) = length(contents) = length(edges) - 1, edges are lower, lower, lower, ..., upper
function fromdf(df::DataFrame; entries=:entries)
    ent = df[2].data[1:nrow(df)-1]
    cont = df[3].data[1:nrow(df)-1]

    #entries column reflects poisson errors of the contents column 
    if entries == :poissonerrors
        ent = (cont ./ ent ) .^ 2
        ent = Float64[x > 0 ? x : 0 for x in ent]
    #entries column reflects raw entries/events
    elseif entries == :entries
        ent = ent
    else
        error("unknown value for keyword :entries=>$(entries)")
    end

    Histogram(
        ent, #entries
        cont, #contents
        df[1].data #edges
    )
end

flatten(h) = reshape(h, prod(size(h)))

function rebin(h::Histogram, k::Integer)
    @assert(length(h.bin_contents)%k == 0, "number of bins is not divisible by k")

    new_entries = Int64[]
    new_contents = Float64[]
    new_edges = Float64[]
    for i=1:k:length(h.bin_contents)
        push!(new_contents, sum(h.bin_contents[i:i+k-1]))
        push!(new_entries, sum(h.bin_entries[i:i+k-1]))
        push!(new_edges, h.bin_edges[i])
    end
    push!(new_edges, h.bin_edges[length(h.bin_edges)])
    return Histogram(new_entries, new_contents, new_edges)
end

export Histogram, hfill!
export integral, nentries, normed, errors, findbin
export +, -, *, /, ==
export todf, fromdf
export flatten
export lowedge, widths
export rebin

end #module

