module Hist
using DataArrays, DataFrames

import Base.+, Base.-, Base.*, Base./, Base.==
import Base.show
import Base.getindex
import Base.size, Base.transpose

using JSON

immutable Histogram
    bin_entries::Vector{Float64}
    bin_contents::Vector{Float64}
    bin_edges::Vector{Float64}

    function Histogram(entries::AbstractVector, contents::AbstractVector, edges::AbstractVector)
        @assert length(entries)==length(contents)
        @assert length(entries)==length(edges)
        @assert all(entries .>= 0.0)
        @assert issorted(edges)
        new(
            convert(Vector{Float64}, entries),
            convert(Vector{Float64}, contents),
            convert(Vector{Float64}, edges)
        )
    end
end

Histogram(a::Vector) = Histogram(
    Float64[0.0 for i=1:length(a)],
    Float64[0.0 for i=1:length(a)],
    a
)

Histogram(h::Histogram) = Histogram(h.bin_entries, h.bin_contents, h.bin_edges)

#account for the under- and overflow bins
nbins(h::Histogram) = length(h.bin_contents)

contents(h::Histogram) = h.bin_contents

function subhist(h::Histogram, bins)
    entries = Int64[]
    contents = Float64[]
    edges = Float64[]
    for b in bins
        push!(entries, h.bin_entries[b])
        push!(contents, h.bin_contents[b])
        push!(edges, h.bin_edges[b])
    end
    return Histogram(entries, contents, edges)
end

function errors(h::Histogram, replacenan=true, replace0=true, replaceval=0.0)
    errs = h.bin_contents ./ sqrt(h.bin_entries)
    T = eltype(errs)
    for i=1:nbins(h)
        if replacenan && isnan(errs[i])
            errs[i] = replaceval
        end

        #in case of zero bins, put error 1.0
        if replace0 && errs[i] < eps(T)
            errs[i] = replaceval
        end
    end
    return errs
end

function findbin{T <: Real}(h::Histogram, v::T)
    isnan(v) && return 1 #put nans in underflow bin

    v < h.bin_edges[1] && error("underflow v=$v")
    v >= h.bin_edges[nbins(h)] && error("overflow v=$v, min=$(minimum(h.bin_edges)), max=$(maximum(h.bin_edges))")

    const idx = searchsortedfirst(h.bin_edges, v)::Int64 - 1
    if (idx<1 || idx>length(h.bin_entries))
        error("bin index out of range: i=$(idx), v=$(v)")
    end
    return idx
end

entries(h::Histogram) = h.bin_entries

function hfill!{T <: Real, K <: Real}(h::Histogram, v::T, w::K=1.0)
    const low = findbin(h, v)
    h.bin_entries[low] += 1
    h.bin_contents[low] += isnan(w) ? 0.0 : w
end

function hfill!{T <: Real}(h::Histogram, v::NAtype, w::Union(T, NAtype)=1.0)
    h.bin_entries[1] += 1
    h.bin_contents[1] += isnan(w) ? 0.0 : w
end

function hfill!{T <: Real}(h::Histogram, v::T, w::NAtype)
    h.bin_entries[1] += 1
    h.bin_contents[1] += 0
end

function +(h1::Histogram, h2::Histogram)
    @assert h1.bin_edges == h2.bin_edges
    h = Histogram(
        h1.bin_entries + h2.bin_entries,
        h1.bin_contents + h2.bin_contents,
        h1.bin_edges
    )
    abs(integral(h1)+integral(h2)-integral(h)) < 0.00001 || warn("problem adding histograms: $(integral(h1)) != $(integral(h2))")
    return h
end

function +(h1::Histogram, x::Real)
    nb = nbins(h1)
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

function *(h1::Histogram, h2::Histogram)
    @assert(h1.bin_edges == h2.bin_edges, "bin edges must be the same for both histograms")
    conts = h1.bin_contents.* h2.bin_contents
    ents = 1.0 / (1.0 ./ entries(h1) + 1.0 ./ entries(h2))

    conts[isnan(conts)] = 0.0
    ents[isnan(ents)] = 0.0

    Histogram(ents, conts, h1.bin_edges)
end


function /{T <: Real}(h1::Histogram, x::T)
    return h1 * (1.0/x)
end

#err / C = sqrt((err1/C1)^2 + (err2/C2)^2) 
function /(h1::Histogram, h2::Histogram)
    @assert(h1.bin_edges == h2.bin_edges, "bin edges must be the same for both histograms")
    
    conts = h1.bin_contents ./ h2.bin_contents
    ents = 1.0 / (1.0 ./ entries(h1) + 1.0 ./ entries(h2))

    conts[isnan(conts)] = 0.0
    ents[isnan(ents)] = 0.0

    return Histogram(ents, conts, h1.bin_edges)

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

#function fromdf(df::DataFrame)
#    edges = df[1]
#    conts = df[2][1:nrow(df)-1]
#    entries = df[3][1:nrow(df)-1]
#    return Histogram(entries, conts, edges)
#end

#assumes df columns are entries, contents, edges
#length(entries) = length(contents) = length(edges) - 1, edges are lower, lower, lower, ..., upper
# function fromdf(df::DataFrame; entries=:entries)
#     ent = df[2].data
#     cont = df[3].data

#     #entries column reflects poisson errors of the contents column 
#     if entries == :poissonerrors
#         ent = (cont ./ ent ) .^ 2
#         ent = Float64[x > 0 ? x : 0 for x in ent]
#     #entries column reflects raw entries/events
#     elseif entries == :entries
#         ent = ent
#     else
#         error("unknown value for keyword :entries=>$(entries)")
#     end

#     Histogram(
#         ent, #entries
#         cont, #contents
#         df[1].data #edges
#     )
# end

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

function *{T <: Real}(h::NHistogram, x::T)
    return NHistogram(x * h.baseh, h.edges)
end

function *{T <: Real}(x::T, h::NHistogram)
    return h * x
end


function asarr(h::NHistogram)
    return reshape(h.baseh.bin_contents, Int64[length(e) for e in h.edges]...),
    reshape(h.baseh.bin_entries, Int64[length(e) for e in h.edges]...)
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
    fromarr(transpose(ne), transpose(nc), nh.edges|>reverse|>collect)
end

contents(h::NHistogram) = asarr(h)[1]
entries(h::NHistogram) = asarr(h)[2]
Base.size(h::NHistogram) = tuple([length(e) for e in h.edges]...)

function findbin_nd(h::NHistogram, v)
    const nd = length(v)
    @assert ndim(h)==nd
    const idxs = Int64[-1 for i=1:nd]
    for i=1:nd
        const x = v[i]
        const j = (isna(x) || isnan(x)) ? 1 : (searchsortedfirst(h.edges[i], x) - 1)
        (j < 1 || j > length(h.edges[i])) && error("overflow dim=$i, v=$x")
        idxs[i] = j
    end
    return idxs
end

#is slow
function hfill!{K <:Real}(h::NHistogram, v, w::K=1.0)
    a, b = asarr(h)
    xb = findbin_nd(h, v)
    a[xb...] += w
    b[xb...] += 1
end

function hfill!{K <: NAtype}(h::NHistogram, v, w::K)
    warn("NA weight in NHistogram")
    #a, b = asarr(h)
    #xb = findbin_nd(h, v)
    #a[xb...] += 0
    #b[xb...] += 1
end

# function writecsv(fn, h::NHistogram)
#     dfs = todf(h)
#     writetable("$fn.hist", dfs[:hist];separator=',')
#     dd = {:hist=>"$fn.hist", :edges=>Any[]}
#     j = 1
#     for e in dfs[:edges]
#         writetable("$fn.edges.$j", e; separator=',')
#         push!(dd[:edges], "$fn.edges.$j")
#         j += 1
#     end
#     of = open("$fn.json", "w")
#     write(of, JSON.json(dd))
#     close(of)
# end

# function readhist(fn)
#     js = JSON.parse(readall("$fn.json"))
#     hist = readtable(js["hist"])
#     edges = [readtable(e) for e in js["edges"]]
#     nd = length(edges)
#     evec = [edges[i][1] for i=1:nd]
#     NHistogram(fromdf(hist), evec)
# end

function Base.getindex(nh::NHistogram, args...)
    a, b = asarr(nh)
    return a[args...]#, b[args...]
end

# function makehist_2d(df::AbstractDataFrame, bins::AbstractVector)
#     hi = NHistogram(bins)
#     @assert ncol(df)==2
#     cont, ent = asarr(hi)
#     for i=1:nrow(df)
#         x = df[i,1]
#         y = df[i,2]
#         nx = isna(x)||isnan(x) ? 1 : searchsortedfirst(hi.edges[1], x)-1
#         ny = isna(y)||isnan(y) ? 1 : searchsortedfirst(hi.edges[2], y)-1
#         cont[nx, ny] += 1
#         ent[nx, ny] += 1
#     end
#     return hi
# end

# project_n(nh::NHistogram, n) = NHistogram(
#     sum(nh|>entries, n)[:],
#     sum(nh|>contents, n)[:],
#     nh.edges[2]
# )


project_x(nh::NHistogram) = Histogram(sum(nh|>entries, 1)[:], sum(nh|>contents, 1)[:], nh.edges[2])
project_y(nh::NHistogram) = Histogram(sum(nh|>entries, 2)[:], sum(nh|>contents, 2)[:], nh.edges[1])

Base.show(io::IO, h::Histogram) = show(io, hcat(h.bin_edges, h.bin_contents, h.bin_entries))

export Histogram, hfill!
export integral, nentries, normed, errors, findbin, nbins
export +, -, *, /, ==
#export todf, fromdf
export flatten
export lowedge, widths
export rebin
export cumulative
export writecsv
export test_ks
export NHistogram, findbin_nd, ndim, asarr, readhist
export contents, entries
export makehist_2d, fromarr
export project_x, project_y
end #module
