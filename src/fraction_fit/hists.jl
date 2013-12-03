#!/usr/bin/env julia

using DataFrames

#for jldopen, hdf5 storage
using HDF5
using JLD

using Distributions, Stats

#for numpy.histogram
using PyCall
@pyimport numpy

using PyPlot

include("../analysis/histo.jl")
using Hist

#######
#Input#
#######

sample_is(x) = :(sample .== $x)

indir = "/Users/joosep/Documents/stpol/results/";
infile = "$indir/skim_output.jld";

println("opening $infile")
tic()
fi = jldopen(infile, "r", mmaparrays=false);
indata = read(fi, "df");
close(fi);
toc();

indata["totweight"] = 1.0
indata["fitweight"] = 1.0

#apply PU weighting
indata[:(sample .== "data_mu"), :pu_weight] = 1.0
indata[:(sample .== "data_ele"), :pu_weight] = 1.0
indata[:totweight] = indata[:pu_weight].*indata[:totweight]

#electron channel QCD weight (ad-hoc)
indata[:((sample .== "data_ele") .* (isolation .== "antiiso")), :totweight] = 0.00005
indata[:((sample .== "data_mu") .* (isolation .== "antiiso")), :totweight] = 0.000025
indata[:((sample .== "data_mu") .* (isolation .== "antiiso") .* (njets .== 3) .* (ntags .== 2)), :totweight] = 0.0000000002;
indata[:((sample .== "data_mu") .* (isolation .== "antiiso") .* (njets .== 3) .* (ntags .== 1)), :totweight] = 0.000000002;
indata[:((sample .== "data_ele") .* (isolation .== "antiiso") .* (njets .== 3) .* (ntags .== 2)), :totweight] = 0.000000002;
indata[:((sample .== "data_ele") .* (isolation .== "antiiso") .* (njets .== 3) .* (ntags .== 1)), :totweight] = 0.0000002;

#Sherpa reweight to madgraph yield
indata[sample_is("wjets_sherpa"), :xsweight] = 0.04471345 .* indata[sample_is("wjets_sherpa"), :xsweight]

#remove events with incorrect weights
indata[isna(indata[:totweight]), :totweight] = 1.0

indata[sample_is("data_mu"), :xsweight] = 1.0
indata[sample_is("data_ele"), :xsweight] = 1.0

const lumis = {:mu => 19764, :ele =>19820}

###########
#Selection#
###########

println("performing selection")

selections = {
    :mu => :(lepton_type .== 13),
    :ele => :(lepton_type .== 11),
    :dr => :((ljet_dr .> 0.5) .* (bjet_dr .> 0.5)),
    :iso => :(isolation .== "iso"),
    :aiso => :(isolation .== "antiiso")
}

inds = {
    :mu =>indata["lepton_type"] .== 13,
    :ele =>indata["lepton_type"] .== 11,
    :ljet_rms =>indata["ljet_rms"] .> 0.025,
    :mtw =>indata["mtw"] .> 50,
    :met =>indata["met"] .> 45,
    :dr => (indata["ljet_dr"] .> 0.5) .* (indata["bjet_dr"] .> 0.5),
    :iso => indata["isolation"] .== "iso",
    :aiso => indata["isolation"] .== "antiiso",
    :data_mu => indata["sample"] .== "data_mu",
    :data_ele => indata["sample"] .== "data_ele",
    :njets => n -> indata["njets"] .== n,
    :ntags => n -> indata["ntags"] .== n,
}

samples = ["data_mu", "data_ele", "tchan", "ttjets", "wjets", "dyjets", "diboson", "gjets", "schan", "twchan"]
for s in samples
    inds[symbol(s)] = indata["sample"] .== s
end

for c in [:mu, :ele]
    indata[inds[c], :xsweight] = indata[inds[c], :xsweight] .* lumis[c]
end

function makehist(df, sample_ex, var_ex, bins, weight_ex)
    subdf = select(sample_ex, df)
    #x = subdf[var_ex]
    x = with(subdf, var_ex)
    weights = []
    if typeof(weight_ex) <: Expr || typeof(weight_ex) <: Symbol
      weights = with(subdf, weight_ex)
    elseif typeof(weight_ex) <: Number
      weights = Float64[convert(Float64, weight_ex) for i=1:nrow(subdf)]
    else
      error("unknown weights type $(typeof(weight_ex))")
    end
    counts, edges = numpy.histogram(x, bins)
    bins, edges = numpy.histogram(x, bins, weights=weights)
    #errs = sqrt(counts)/counts * bins
    ret = Histogram(counts, bins, edges)
    return ret
end

#df - a DataFrame
#data_expr - the projection expression to get the measured data from 'df'
#var - a list of variable expressions to plot
#bins - a list of binning specifications for the variables in 'var'
#weight_ex - the weight expression used for MC and QCD
function makehists(
    df, data_expr, vars, bins;
    weight_ex = :(xsweight .* totweight .* fitweight)
  )
    iso = select(selections[:iso], df)
    aiso = select(selections[:aiso], df)

    procs = ["wjets", "ttjets", "tchan", "gjets", "dyjets", "schan", "twchan", "diboson"]
    hists = Dict()
    for k in procs
        hists[k] = makehist_multid(iso, sample_is(k), vars, bins, weight_ex);
    end

    hists["qcd"] = (makehist_multid(aiso, data_expr, vars, bins, weight_ex) - 
        sum([makehist_multid(aiso, sample_is(p), vars, bins, weight_ex) for p in procs]))

    hists["DATA"] = makehist_multid(iso, data_expr, vars, bins, 1.0);

    return hists
end

makehists(df, data_expr, var::Union(Expr, Symbol), bins; args...) = 
    makehists(df, data_expr, {var,}, {bins,}; args...)

flatten{T}(a::Array{T,1}) =
    any(map(x->isa(x,Array),a)) ? flatten(vcat(map(flatten,a)...)): a
flatten{T}(a::Array{T}) = reshape(a,prod(size(a)))
flatten(a)=a

function makehist_multid(df, sample_ex, vars, bins, weight_ex)
    subdf = select(sample_ex, df)
    arrs = Any[]
    @assert length(vars)==length(bins) "vars and bins must be the same length"
    for i=1:length(vars)
        v = vars[i]
        push!(arrs, with(subdf, v))    
    end
    arr = hcat(arrs...)

    if typeof(weight_ex) <: Expr || typeof(weight_ex) <: Symbol
        weights = with(subdf, weight_ex)
    elseif typeof(weight_ex) <: Number
        weights = Float64[convert(Float64, weight_ex) for i=1:nrow(subdf)]
    else
        error("unknown weights type $(typeof(weight_ex))")
    end

    hist, edges = numpy.histogramdd(arr, bins, weights=weights)
    counts, edges = numpy.histogramdd(arr, bins)
    fhist = flatten(hist)
    fcounts = flatten(counts)

    #in case of a 1D histogram, bin labels are well-defined.
    #otherwise, use simply sequential numbering
    edges = length(vars)>1 ? [1:length(fhist)+1] : edges[1]

    return Histogram(fcounts, fhist, edges)
end


function mergehists(hists)
    out = Dict()
    out["wzjets"] = hists["wjets"] + hists["gjets"] + hists["dyjets"] + hists["diboson"]
    out["ttjets"] = hists["ttjets"] + hists["schan"] + hists["twchan"]

    out["qcd"] = hists["qcd"]

    out["tchan"] = hists["tchan"] 
    out["DATA"] = hists["DATA"]
    return out
end

to_df(bins, errs, edges) =
    DataFrame(bins=vcat(bins, -1.0), errs=vcat(errs, -1.0), edges=edges);

function to_df(h::Histogram)
    errs = (sqrt(h.bin_entries) ./ h.bin_entries .* h.bin_contents) 
    for i=1:length(errs)
        if !(errs[i] > 0)
            errs[i] = 0.0
        end
    end 
    return DataFrame(
        bins=vcat(h.bin_contents, -1.0),
        errs=vcat(errs, -1.0),
        edges=h.bin_edges
    );
end

function to_df(d::Associative)
    tot_df = DataFrame()
    for (k, v) in d
        df = to_df(v)
        rename!(index(df), x -> "$(x)__$(k)")
        tot_df = hcat(tot_df, df)
    end
    return tot_df
end

function data_mc_stackplot(df, data_ex, ax, var, bins; kwargs...)
    kwd = {k=>v for (k,v) in kwargs}
    order = pop!(kwd, :order, nothing)

    bar_args = Dict()
    if pop!(kwd, :logy, false)
        bar_args[:log] = true
    end

    hists = makehists(df, data_ex, var, bins; kwd...);

    draws = [
        ("dyjets", hists["dyjets"], {:color=>"purple", :label=>"DY-jets"}),
        ("diboson", hists["diboson"], {:color=>"blue", :label=>"diboson"}),
        ("schan", hists["schan"], {:color=>"yellow", :label=>"s-channel"}),
        ("twchan", hists["twchan"], {:color=>"Gold", :label=>"tW-channel"}),
        ("gjets", hists["gjets"], {:color=>"gray", :label=>"\$ \\gamma \$-jets"}),
        ("qcd", hists["qcd"], {:color=>"gray", :label=>"QCD"}),
        ("wjets", hists["wjets"], {:color=>"green", :label=>"W+jets"}),
        ("ttjets", hists["ttjets"], {:color=>"orange", :label=>"\$ t \\bar{t} \$"}),
        ("tchan", hists["tchan"], {:color=>"red", :label=>"t-channel"})
    ]
    dd = {k[1]=>k for k in draws}

    order = order==nothing ? [k[1] for k in draws] : order
    hlist = Histogram[dd[o][2] for o in order]
    arglist = Dict{Any, Any}[dd[o][3] for o in order]
    
    hplot(
        ax, hlist, arglist,
        common_args=merge({:edgecolor=>"none", :linewidth=>0.0}, bar_args)
    )

    tot_mc = 0.0
    tot_data = 0.0
    yieldsd = Dict()
    for (hn, hi) in hists
        yieldsd[hn] = integral(hi)
        if hn == "DATA"
            tot_data += integral(hi)
        else
            tot_mc += integral(hi)
        end
    end
    yieldsd["total_mc"] = tot_mc
    yieldsd["total_data"] = tot_data

    eplot(ax, hists["DATA"], ls="", marker="o", color="black", label="Data")
    ylabel("Event yield")
    return ax, hists, yieldsd
end

function ratio_hist(hists)
    mc = sum([v for (k,v) in filter(x -> x[1] != "DATA", collect(hists))])
    data = sum([v for (k,v) in filter(x -> x[1] == "DATA", collect(hists))])

    mcs = [Poisson(x) for x in mc.bin_entries]
    datas = [Poisson(x) for x in data.bin_entries]
    N = 10000
    
    errs = Array(Float64, (2, length(mcs)))
    means = Array(Float64, length(mcs))
    for i=1:length(mcs)
        m = rand(mcs[i], N) * mc.bin_contents[i] / mc.bin_entries[i] 
        d = rand(datas[i], N)
        v = (d-m)./d
        err_up, mean, err_down = quantile(v, 0.99), quantile(v, 0.5), quantile(v, 0.01)
        errs[1,i] = abs(mean-err_up)
        errs[2,i] = abs(mean-err_down)
        means[i] = mean
    end

    return means, errs
end

immutable FitResult
    means::Vector{Float64}
    sigmas::Vector{Float64}
    corr::Array{Float64, 2}
    names::Vector{ASCIIString}
    chi2::Float64
    nbins::Int64
end

function FitResult(fn::ASCIIString)
    fit = JSON.parse(readall(fn));
    n = length(fit["names"])
    FitResult(
        convert(Vector{Float64}, fit["means"]), 
        convert(Vector{Float64}, fit["errors"]),
        convert(Array{Float64, 2}, [fit["corr"][x][y] for x=1:n,y=1:n]),
        #corr_ij = cov_ij / (sigma_i * sigma_j)
        #Float64[fit["cov"][x][y]/(fit["errors"][x] * fit["errors"][y]) for x=1:n, y=1:n],
        convert(Vector{ASCIIString}, fit["names"]),
        fit["chi2"][1],
        fit["nbins"]
    )
end

function show_corr(a, fr::FitResult; subtitle="")
    im = a[:matshow](fr.corr, interpolation="none", cmap="jet", vmin=-1, vmax=1)
    n = length(fr.names)

    ax[:xaxis][:set_ticks]([0:n-1])
    ax[:xaxis][:set_ticks_position]("bottom")
    ax[:xaxis][:set_ticklabels](
        [@sprintf("%s:\n %.2f \$ \\pm \$ %.2f", fr.names[i], fr.means[i], fr.sigmas[i]) for i=1:n], rotation=90
    );
    ax[:yaxis][:set_ticks]([0:n-1])
    ax[:yaxis][:set_ticklabels](fr.names)

    for i=1:length(fr.names)
        for j=1:length(fr.names)
            a[:text](i-1, j-1, @sprintf("%.4f", fr.corr[i,j]), color="green", ha="center", va="center", size="large")
        end
    end
    chindf = fr.chi2 / (fr.nbins-1)
    schindf = @sprintf("%.2f", chindf)
    a[:set_title]("corr, \$ \\chi^2/n = $schindf \$, $subtitle");
    return im
end

function run_fit(ind; output=false)

    workdir = "/Users/joosep/Documents/stpol/src/fraction_fit"
    cd(workdir);

    redir(cmd) = output ? run(cmd) : readall(cmd)

    #convert dataframes to root
    for inf in split(readall(`find $ind -name "*.csv"`))
        of = replace(inf, ".csv", ".root")
        #println("converting $inf->$of")
        cmd = `./rootwrap.sh python convert.py $inf $of`
        run(cmd)
    end

    #run theta
    cmd = `./runtheta.sh bgfit.py $ind`
    redir(cmd)

    fitres = FitResult("out.txt")
    return fitres
end

function rslegend(a; x...)
    handles, labels = a[:get_legend_handles_labels]()
    a[:legend](reverse(handles), reverse(labels), loc="center left", bbox_to_anchor=(1, 0.5); x...);
end;

function bdt_plot(a, df::DataFrame, data_ex, fr::FitResult; xrange=linspace(-1, 1, 20))
    #df = indata[inds[:mu] .* inds[:dr] .* inds[:mtw] .* inds[:ljet_rms], :];
    hists = makehists(
        df, data_ex,
        :(bdt_sig_bg),
        xrange
    ) |> mergehists;
  
    mu = {k=>v for (k,v) in zip(fr.names, fr.means)}
    hplot(a,
        [
            hists["qcd"] * mu["qcd"],
            hists["ttjets"] * mu["ttjets"],
            hists["wzjets"] * mu["wzjets"],
            hists["tchan"] * mu["beta_signal"],
        ],
        [
            {:label=>"QCD", :color=>"gray"},
            {:label=>"\$ t \\bar{t} \$, s, tW", :color=>"orange"},
            {:label=>"W+Jets+", :color=>"g"},
            {:label=>"t-channel", :color=>"r"}
        ]
    )
    eplot(a, hists["DATA"]; color="black", marker="o", ls="", drawstyle="steps-mid")
    #rslegend(a)
    xlabel("BDT output")
    ylabel("expected, fitted yield")
end

function ratio_axes(;frac=0.2, w=5, h=5)
    fig = PyPlot.plt.figure(figsize=(w,h))
    a2 = PyPlot.plt.axes((0.0, 0.0, 1.0, frac))
    a1 = PyPlot.plt.axes((0.0,frac, 1.0, 1-frac), sharex=a2)
    a2[:set_ylim](-1,1)
    a2[:yaxis][:tick_right]()
    a2[:yaxis][:set_label_position]("right")
    PyPlot.plt.setp(a1[:get_xticklabels](), visible=false)
    return fig, {a1, a2}
end

function subplots(args...;kwargs...)
    fig, axs = convert(PyVector, PyPlot.plt.subplots(args...;kwargs...))
    return fig, convert(PyVector, axs)
end

function errorbars(a, h; kwargs...)
    hdata = h["DATA"]
    means, errs = ratio_hist(h)

    a[:errorbar](midpoints(hdata.bin_edges), means, errs, ls="", marker=".", color="black"; kwargs...)
    #a[:errorbar](midpoints(hdata.bin_edges), means, errs, ls="", marker="", color="black"; kwargs...)
    a[:axhline](0.0, color="black")
    a[:grid]()
    a[:set_ylabel]("(Data - MC) / Data")
end

function reweigh_to_fitres(frd)
    for (lep, fr) in frd
        means = {k=>v for (k,v) in zip(fr.names, fr.means)}
        si = inds[lep]
        indata[si .* (inds[:tchan]), :fitweight] = means["beta_signal"]
        indata[si .* (inds[:wjets] .+ inds[:gjets] .+ inds[:dyjets] .+ inds[:diboson]), :fitweight] = means["wzjets"]
        indata[si .* (inds[:ttjets] .+ inds[:schan] .+ inds[:twchan]), :fitweight] = means["ttjets"]
        indata[si .* inds[:aiso] .* (inds[symbol("data_$lep")]), :fitweight] = means["qcd"]
    end
end;

@pyimport scipy.stats.kde as KDE
@pyimport matplotlib.cm as cmap
function kde_contour(arr, X, Y, n=6; kwargs...)
    k = KDE.gaussian_kde(transpose(matrix(arr)));
    xy = zeros(Float64, (2,length(X)*length(Y)));
    n = 1
    for x in X
      for y in Y
        xy[1,n] = x
        xy[2,n] = y
        n += 1
      end
    end
    Z = reshape(k[:__call__](xy), (length(X), length(Y)));
    contour(X,Y,Z; kwargs...)
end

function yield_table(a, x, y, yieldsd)
    tx = "DEBUG\n"
    for (k, v) in sort(collect(yieldsd), by=x->x[2], rev=true)
      if k == "DATA"
        continue
      end
      tx = string(tx, k, @sprintf(": %.1f\n", v))
    end

    a[:text](x, y, tx, alpha=0.4, color="black", size="x-small");
end