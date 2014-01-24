using PyCall
using PyPlot

function hplot(ax::PyObject, h::Histogram, prevhist::Histogram;kwargs...)
    
    @assert nbins(h)==nbins(prevhist) "Histograms have different bins: $(nbins(h)) != $(nbins(prevhist))"
    kwargsd = {k=>v for (k, v) in kwargs}

    #in case of log scale, low bins must be \eps; otherwise 0,0,0,...,0 or lower
    if (:log in keys(kwargsd) && kwargsd[:log])
        prevbins = [x > 0 ? x : 1 for x in prevhist.bin_contents]
    else
        prevbins = prevhist.bin_contents
    end

    ax[:bar](lowedge(h.bin_edges), h.bin_contents[1:nbins(h)-1], widths(h.bin_edges), prevbins[1:nbins(h)-1]; kwargs...)
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
    ax[:errorbar](midpoints(h.bin_edges), h.bin_contents[1:nbins(h)-1], errors(h)[1:nbins(h)-1]; kwargs...)
end


function eplot{T <: Histogram}(ax::PyObject, hs::Vector{T};kwargs...)
   rets = Any[]
   for h in hs
        r = eplot(ax, h; kwargs...)
        push!(rets, r)
   end
   return rets
end
