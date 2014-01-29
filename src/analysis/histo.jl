module Hist
using DataArrays, DataFrames
import DataArrays.NAtype

import Base.+, Base.-, Base.*, Base./, Base.==
import Base.show
import Base.getindex
import Base.size, Base.transpose

using JSON

immutable Histogram
    bin_entries::Vector{Float64} #n values
    bin_contents::Vector{Float64} #n values
    bin_edges::Vector{Float64} #n+1 values, lower edges of all bins + upper edge of last bin

    function Histogram(entries, contents, edges)
        @assert length(entries)==length(contents)
        @assert length(entries)==length(edges)
        @assert all(entries .>= 0.0)
        @assert issorted(edges)
        new(entries, contents, edges)
    end
end

# function Histogram(n::Integer, low::Number, high::Number)
#     bins = linspace(low, high, n)

#     #underflow low edge
#     unshift!(bins, -inf(Float64))

#     #overflow high edge
#     push!(bins, inf(Float64))

#     n_contents = size(bins,1)-1
#     return Histogram(
#         zeros(Float64, (n_contents, )),
#         zeros(Float64, (n_contents, )),
#         bins
#     )
# end
Histogram(a::Array) = Histogram(
    [0.0 for i=1:length(a)],
    [0.0 for i=1:length(a)],
    a
)

Histogram(h::Histogram) = Histogram(h.bin_entries, h.bin_contents, h.bin_edges)

#account for the under- and overflow bins
nbins(h::Histogram) = length(h.bin_contents)

contents(h::Histogram) = h.bin_contents

function errors(h::Histogram)
    errs = h.bin_contents ./ sqrt(h.bin_entries)
    for i=1:nbins(h)
        if isnan(errs[i])
            errs[i] = 0.0
        end
    end
    return errs
end

function findbin(h::Histogram, v::Real)
    v < h.bin_edges[1] && error("underflow v=$v")
    v >= h.bin_edges[nbins(h)] && error("overflow v=$v, min=$(minimum(h.bin_edges)), max=$(maximum(h.bin_edges))")

    isnan(v) && return 1 #put nans in underflow bin

    idx = searchsortedfirst(h.bin_edges, v) - 1
    if (idx<1 || idx>length(h.bin_entries))
        error("bin index out of range: i=$(idx), v=$(v)")
    end
    return idx
end

function hfill!(h::Histogram, v::Real, w::Real=1.0)
    low = findbin(h, v)

    h.bin_entries[low] += 1
    h.bin_contents[low] += isnan(w) ? 0.0 : w
    return sum(h.bin_contents)
end

function hfill!(h::Histogram, v::NAtype, w::Union(Real, NAtype)=1.0)
    h.bin_entries[1] += 1
    h.bin_contents[1] += 1
    return sum(h.bin_contents)
end

function hfill!(h::Histogram, v::Real, w::NAtype)
    h.bin_entries[1] += 1
    h.bin_contents[1] += 1
    return sum(h.bin_contents)
end

function +(h1::Histogram, h2::Histogram)
    @assert h1.bin_edges == h2.bin_edges
    h = Histogram(h1.bin_entries + h2.bin_entries, h1.bin_contents+h2.bin_contents, h1.bin_edges)
    @assert abs(integral(h1)+integral(h2)-integral(h))<0.00001
    return h
end

function +(h1::Histogram, x::Real)
    nb = nbins(h)
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
    bin_contents=h.bin_contents,
    bin_entries=h.bin_entries,
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
    ent = df[2].data
    cont = df[3].data

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

flatten(h::Histogram) = reshape(h, prod(size(h)))

function rebin(h::Histogram, k::Integer)
    @assert((nbins(h)) % k == 0, "number of bins $(nbins(h))+1 is not divisible by k=$k")

    new_entries = Int64[]
    new_contents = Float64[]
    new_edges = Float64[]
    for i=1:k:nbins(h)
        push!(new_contents, sum(h.bin_contents[i:i+k-1]))
        push!(new_entries, sum(h.bin_entries[i:i+k-1]))
        push!(new_edges, h.bin_edges[i])
    end
    #push!(new_edges, h.bin_edges[nbins(h)+1])
    return Histogram(new_entries, new_contents, new_edges)
end

function cumulative(h::Histogram)
    #hc = Histogram(h)
    cont = deepcopy(h.bin_contents)
    ent = deepcopy(h.bin_contents)
    for i=1:length(h.bin_contents)
        cont[i] = sum(h.bin_contents[1:i])
        ent[i] = sum(h.bin_entries[1:i])
    end
    return Histogram(ent, cont, h.bin_edges)
end

function test_ks(h1::Histogram, h2::Histogram)
    ch1 = cumulative(h1)
    ch2 = cumulative(h2)
    ch1 = ch1 / integral(h1)
    ch2 = ch2 / integral(h2)
    return maximum(abs(ch1.bin_contents - ch2.bin_contents))
end

type NHistogram
    baseh::Histogram
    edges::Vector{Vector{Float64}}
end

function NHistogram(edges)
    nb = prod([length(e) for e in edges])
    baseh = Histogram([1:nb])
    NHistogram(baseh, edges)
end

function ==(h1::NHistogram, h2::NHistogram)
    ret = h1.edges == h2.edges
    ret = ret && h1.baseh == h2.baseh
    return ret
end

nbins(h::NHistogram) = prod([length(e) for e in h.edges])
nbins(h::NHistogram, nd::Integer) = length(h.edges[nd])
ndim(h::NHistogram) = length(h.edges)

errors(h::NHistogram) = reshape(errors(h.baseh), Int64[length(e) for e in h.edges]...)
nentries(h::NHistogram) = nentries(h.baseh)
integral(h::NHistogram) = integral(h.baseh)

function +(h1::NHistogram, h2::NHistogram)
    @assert h1.edges == h2.edges
    return NHistogram(h1.baseh+h2.baseh, h1.edges)
end

function asarr(h::NHistogram)
    rsh(x) = reshape(x, Int64[length(e) for e in h.edges]...)
    return rsh(h.baseh.bin_contents), rsh(h.baseh.bin_entries)
end

function fromarr(nc, ne, edges)
    nb = prod([length(e) for e in edges])
    rsh(x) = reshape(x, nb)
    NHistogram(
        Histogram(rsh(nc), rsh(ne), [1:nb]),
        edges
    )
end

function Base.transpose(nh::NHistogram)
    nc, ne = asarr(nh)
    fromarr(transpose(nc), transpose(ne), nh.edges|>reverse|>collect)
end

contents(h::NHistogram) = asarr(h)[1]
Base.size(h::NHistogram) = tuple([length(e) for e in h.edges]...)

function findbin_nd(h::NHistogram, v)
    nd = length(v)
    @assert ndim(h)==nd
    idxs = Int64[]
    for i=1:nd
        x = v[i]
        j = (isna(x) || isnan(x)) ? 1 : (searchsortedfirst(h.edges[i], x) - 1)
        (j < 1 || j > length(h.edges[i])) && error("overflow dim=$i, v=$x")
        push!(idxs, j)
    end
    return tuple(idxs...)
end

function hfill!(h::NHistogram, v, w=1.0)
    a, b = asarr(h)
    xb = findbin_nd(h, v)
    #println(typeof(a), " ", size(a), " ", join(xb, ","), " ", join(v, ","))
    #a = reshape(h.baseh.bin_contents, Int64[length(e) for e in h.edges]...)
    a[xb...] += isna(w) ? 0.0 : w
    #b = reshape(h.baseh.bin_entries, Int64[length(e) for e in h.edges]...)
    b[xb...] += 1
end

function todf(h::NHistogram)
    hist = todf(h.baseh)
    return {:hist=>hist, :edges=>[DataFrame(e) for e in h.edges]}
end

function writecsv(fn, h::NHistogram)
    dfs = todf(h)
    writetable("$fn.hist", dfs[:hist];separator=',')
    dd = {:hist=>"$fn.hist", :edges=>Any[]}
    j = 1
    for e in dfs[:edges]
        writetable("$fn.edges.$j", e; separator=',')
        push!(dd[:edges], "$fn.edges.$j")
        j += 1
    end
    of = open("$fn.json", "w")
    write(of, JSON.json(dd))
    close(of)
end

function readhist(fn)
    js = JSON.parse(readall("$fn.json"))
    hist = readtable(js["hist"])
    edges = [readtable(e) for e in js["edges"]]
    nd = length(edges)
    evec = [edges[i][1] for i=1:nd]
    NHistogram(fromdf(hist), evec)
end

function Base.getindex(nh::NHistogram, args...)
    a, b = asarr(nh)
    return a[args...]#, b[args...]
end

function makehist_2d(df::AbstractDataFrame, bins::AbstractVector)
    hi = NHistogram(bins)
    @assert ncol(df)==2
    for i=1:nrow(df)
        hfill!(hi, (df[i,1], df[i,2]))
    end
    return hi
end

Base.show(io::IO, h::Histogram) = show(io, todf(h))

export Histogram, hfill!
export integral, nentries, normed, errors, findbin, nbins
export +, -, *, /, ==
export todf, fromdf
export flatten
export lowedge, widths
export rebin
export cumulative
export writecsv
export test_ks
export NHistogram, findbin_nd, ndim, asarr, readhist
export contents
export makehist_2d, fromarr
end #module
