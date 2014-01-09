using PyCall, PyPlot
@pyimport numpy

include("../analysis/base.jl")

#uses python, not compatible with CMSSW
include("../analysis/histo.jl")

using Hist
include("../analysis/hplot.jl")
using JSON

using Distributions, Stats

#df - a DataFrame
#inds - a dict of bitarrays
#var - a list of variable expressions to plot
#bins - a list of binning specifications for the variables in 'var'
#weight_ex - the weight expression used for MC and QCD
function makehists(
    mc_iso::AbstractDataFrame, mc_aiso::AbstractDataFrame,
    data_iso::AbstractDataFrame, data_aiso::AbstractDataFrame,
    vars::AbstractArray, bins::AbstractArray;
    weight_ex = :(xsweight .* totweight .* fitweight),
  )

    procs = [:wjets, :ttjets, :tchan, :gjets, :dyjets, :schan, :twchan, :diboson]
    hists = Dict()
    for k in procs
        hists[string(k)] = makehist_multid(
            select(:(sample .== $(hash(string(k)))), mc_iso),
            vars, bins, weight_ex
        );
    end

    hists["qcd"] = (
        makehist_multid(
            data_aiso,
            vars, bins, :(totweight .* qcd_weight)
        ) - 
        sum([
            makehist_multid(
                select(:(sample .== $(string(p))), mc_aiso), 
                vars, bins,
                :(xsweight .* totweight .* qcd_weight)
            )
            for p in procs
        ])
    )

    hists["DATA"] = makehist_multid(data_iso, vars, bins, 1.0);

    return hists
end

makehists(
    mc_iso::AbstractDataFrame,
    mc_aiso::AbstractDataFrame,
    data_iso::AbstractDataFrame,
    data_aiso::AbstractDataFrame,
    var::Union(Expr, Symbol), bins; args...
    ) = 
    makehists(mc_iso, mc_aiso, data_iso, data_aiso, {var,}, {bins,}; args...)

makehists(
    mc_iso::AbstractDataFrame,
    mc_aiso::AbstractDataFrame,
    data_iso::AbstractDataFrame,
    data_aiso::AbstractDataFrame,
    var::Union(Expr, Symbol), bins; args...
    ) = 
    makehists(mc_iso, mc_aiso, data_iso, data_aiso, {var,}, {bins,}; args...)

function makehist_multid(df, vars, bins, weight_ex)
    
    if nrow(df)==0
        if length(bins)==1
            return Histogram(
                [0.0 for i=1:length(bins[1])-1],
                [0.0 for i=1:length(bins[1])-1],
                bins[1]
            )
        else
            error("nrow=0 multid not implemented")
        end
    end

    arrs = Any[]
    @assert length(vars)==length(bins) "vars and bins must be the same length"
    for i=1:length(vars)
        v = vars[i]
        push!(arrs, with(df, v))    
    end
    arr = hcat(arrs...)

    if typeof(weight_ex) <: Expr || typeof(weight_ex) <: Symbol
        weights = with(df, weight_ex)
    elseif typeof(weight_ex) <: Number
        weights = Float64[convert(Float64, weight_ex) for i=1:nrow(df)]
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


function mergehists_4comp(hists)
    out = Dict()
    out["wzjets"] = hists["wjets"] + hists["gjets"] + hists["dyjets"] + hists["diboson"]
    out["ttjets"] = hists["ttjets"] + hists["schan"] + hists["twchan"]

    out["qcd"] = hists["qcd"]

    out["tchan"] = hists["tchan"] 
    out["DATA"] = hists["DATA"]
    return out
end

function mergehists_3comp(hists)
    out = Dict()
    out["wzjets"] = hists["wjets"] + hists["gjets"] + hists["dyjets"] + hists["diboson"]
    out["ttjets"] = hists["ttjets"] + hists["schan"] + hists["twchan"] + hists["qcd"]

    out["tchan"] = hists["tchan"] 
    out["DATA"] = hists["DATA"]
    return out
end

todf(bins, errs, edges) =
    DataFrame(bins=vcat(bins, -1.0), errs=vcat(errs, -1.0), edges=edges);

function todf(h::Histogram)
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

function todf(d::Associative)
    tot_df = DataFrame()
    for (k, v) in d
        df = todf(v)
        rename!(index(df), x -> "$(x)__$(k)")
        tot_df = hcat(tot_df, df)
    end
    return tot_df
end

function data_mc_stackplot(df, ax, var, bins; kwargs...)
    kwd = {k=>v for (k,v) in kwargs}
    order = pop!(kwd, :order, nothing)

    bar_args = Dict()
    if pop!(kwd, :logy, false)
        bar_args[:log] = true
    end

    hists = makehists(
        df[(:mc,:iso)],  df[(:mc,:aiso)],  df[(:data,:iso)],  df[(:data,:aiso)],
        var, bins; kwd...
    );

    draws = [
        ("dyjets", hists["dyjets"], {:color=>"purple", :label=>"DY-jets"}),
        ("diboson", hists["diboson"], {:color=>"blue", :label=>"diboson"}),
        ("schan", hists["schan"], {:color=>"yellow", :label=>"s-channel"}),
        ("twchan", hists["twchan"], {:color=>"Gold", :label=>"tW-channel"}),
        ("gjets_qcd", hists["gjets"]+hists["qcd"], {:color=>"gray", :label=>"QCD, \$ \\gamma \$-jets"}),
        #("gjets", hists["gjets"], {:color=>"gray", :label=>"\$ \\gamma \$-jets"}),
        #("qcd", hists["qcd"], {:color=>"gray", :label=>"QCD"}),
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
    #ax[:set_ylabel]("Event yield")
    return hists
end

function ratio_hist(hists)
    mc = sum([v for (k,v) in filter(x -> x[1] != "DATA", collect(hists))])
    data = sum([v for (k,v) in filter(x -> x[1] == "DATA", collect(hists))])

    mcs = [(!isna(x) && x>0) ? Poisson(x) : Poisson(1) for x in mc.bin_entries]
    datas = [(!isna(x) && x>0) ? Poisson(x) : Poisson(1) for x in data.bin_entries]
    N = 10000
    
    errs = Array(Float64, (2, length(mcs)))
    means = Array(Float64, length(mcs))
    for i=1:length(mcs)
        m = rand(mcs[i], N) * mc.bin_contents[i] / mc.bin_entries[i] 
        d = rand(datas[i], N)
        v = (d-m)./d
        v = Float32[isna(_v) || isnan(_v) ? 0 : _v for _v in v]
        err_up, mean, err_down = quantile(v, 0.99), quantile(v, 0.5), quantile(v, 0.01)
        errs[1,i] = abs(mean-err_up)
        errs[2,i] = abs(mean-err_down)
        means[i] = mean
    end

    return means, errs
end

type FitResult
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

function todf(fr::FitResult)
    procs = fr.names
    df = DataFrame()

    for (m, s, p) in zip(fr.means, fr.sigmas, fr.names)
        df["mean__$p"] = m
        df["sigma__$p"] = s
    end
    df["chi2"] = fr.chi2
    df["nbins"] = fr.nbins

    for (c1, c2) in collect(combinations(fr.names, 2))
        i = findfirst(fr.names, c1)
        j = findfirst(fr.names, c2)
        df["corr__$(c1)__$(c2)"] = fr.corr[i,j]
    end
    return df
end

function show_corr(ax, fr::FitResult; subtitle="")
    im = ax[:matshow](fr.corr, interpolation="none", cmap="jet", vmin=-1, vmax=1)
    n = length(fr.names)

    ax[:xaxis][:set_ticks]([0:n-1])
    ax[:xaxis][:set_ticks_position]("bottom")
    ax[:xaxis][:set_ticklabels](fr.names)

    ax[:yaxis][:set_ticks]([0:n-1])
    ax[:yaxis][:set_ticklabels](
        [@sprintf("%s:\n %.2f \$ \\pm \$ %.2f", fr.names[i], fr.means[i], fr.sigmas[i]) for i=1:n], rotation=0
    );

    for i=1:length(fr.names)
        for j=1:length(fr.names)
            ax[:text](i-1, j-1, @sprintf("%.4f", fr.corr[i,j]), color="green", ha="center", va="center", size="large")
        end
    end
    chindf = fr.chi2 / (fr.nbins-1)
    schindf = @sprintf("%.2f", chindf)
    ax[:set_title]("corr, \$ \\chi^2/n = $schindf \$, $subtitle");
    return im
end

function run_fit(ind; output=false)

    prevdir = pwd()
    workdir = "/Users/joosep/Documents/stpol/src/fraction_fit"

    cd(workdir);

    redir(cmd) = output ? run(cmd) : readall(cmd)

    infiles = split(readall(`find $ind -name "*.csv*"`))
    println("model files: ", join(infiles, ","))

    basedir = ""

    #convert dataframes to root
    for inf in infiles
        of = replace(inf, ".csv", ".root")
        basedir = dirname(of)
        #println("converting $inf->$of")
        cmd = `./rootwrap.sh python convert.py $inf $of`
        run(cmd)
    end

    #run theta
    cmd = `./runtheta.sh bgfit.py $ind`
    redir(cmd)

    fitres = FitResult("out.txt")
    println(joinpath(basedir, "results.json"))
    cp("out.txt", joinpath(basedir, "results.json"))
    cd(prevdir)
    return fitres
end

function rslegend(a; x...)
    handles, labels = a[:get_legend_handles_labels]()
    a[:legend](reverse(handles), reverse(labels), loc="center left", bbox_to_anchor=(1, 0.5), numpoints=1, fancybox=true; x...);
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

function ratio_axes2(;frac=0.2, w=10, h=5, xpad=0.03)
    fig = PyPlot.plt.figure(figsize=(w,h))

    a11 = PyPlot.plt.axes((0.0, 0.0, 0.5-xpad, frac))
    a12 = PyPlot.plt.axes((0.0,frac, 0.5-xpad, 1-frac), sharex=a11)

    a21 = PyPlot.plt.axes((0.5+xpad, 0.0, 0.5-xpad, frac))
    a22 = PyPlot.plt.axes((0.5+xpad,frac, 0.5-xpad, 1-frac), sharex=a21)

    for a in [a11, a21]
        a[:set_ylim](-1,1)
        a[:yaxis][:tick_right]()
        a[:yaxis][:set_label_position]("right")
    end

    for a in [a12, a22]
        PyPlot.plt.setp(a[:get_xticklabels](), visible=false)
    end
    PyPlot.plt.setp(a11[:get_yticklabels](), visible=false)

    return fig, {a11, a12, a21, a22}
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
end

function reweight_to_fitres(frd, indata, inds)
    indata["fitweight"] = 1.0
    for (lep, fr) in frd
        means = {k=>v for (k,v) in zip(fr.names, fr.means)}
        si = inds[lep]
        indata[si & (inds[:tchan]), :fitweight] = means["beta_signal"]
        indata[si & (inds[:wjets] | inds[:gjets] | inds[:dyjets] | inds[:diboson]), :fitweight] = means["wzjets"]
        indata[si & (inds[:ttjets] | inds[:schan] | inds[:twchan]), :fitweight] = means["ttjets"]
        #indata[si & inds[:aiso], :fitweight] = means["ttjets"]
    end
end

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

#plots a comparison of the ele and mu channels, stacked format
function channel_comparison(
    indata, df, base_sel, var, bins, sels; kwargs...
    )
    kwd = {k=>v for (k,v) in kwargs}
    
    if :varname in keys(kwd)
        varname = pop!(kwd, :varname)
    elseif var in keys(VARS)
        varname = VARS[var]
    else
        error("provide xlabel either through global VARS or :varname kwd")
    end

    (fig, (a11, a12, a21, a22)) = ratio_axes2();

    indmu = {k=>indata[v & base_sel & sels[:mu], :] for (k,v) in df}
    indele = {k=>indata[v & base_sel & sels[:ele], :] for (k,v) in df}

    hmu = data_mc_stackplot(
        indmu,
        a12,
        var, bins; kwd...
    );
    hele = data_mc_stackplot(
        indele,
        a22,
        var, bins; kwd...
    );

    ymu = yields(hmu)
    yele = yields(hele)
    yt = hcat(ymu, yele)
    show(yt)

    a12[:set_title]("\$ \\mu \$")
    a22[:set_title]("\$ e \$")

    a12[:grid]();
    a22[:grid]();

    errorbars(a11, hmu);
    errorbars(a21, hele);

    rslegend(a22);

    a21[:set_ylabel]("(Data - MC) / Data")

    lowlim = 0
    if :logy in keys(kwd) && kwd[:logy]
        lowlim = 10
    end
    a12[:set_ylim](bottom=lowlim)
    a22[:set_ylim](bottom=lowlim)

    a11[:set_xlabel](varname, size="x-large")
    a21[:set_xlabel](varname, size="x-large")

    return {:figure=>fig, :yields=>{:mu=>ymu, :ele=>yele}, :hists=>{:mu=>hmu, :ele=>hele}}
end

function yields{T <: Any, K <: Any}(h::Dict{T, K}; kwd...)

    #copy the input histogram collection to keep it unmodified
    h = deepcopy(h)

    #create the total-MC histogram
    hmc = nothing 
    for (k, v) in h
        if k != "DATA"
            hmc = hmc == nothing ? v : hmc+v
        end
    end
    h["MC"] = hmc
    
    #order by name
    hc = sort(collect(h), by=x->x[1])

    #create the total yield table
    yi = DataFrame(
        ds=ASCIIString[x for (x,y) in hc], #process name
        uy=Int64[sum(y.bin_entries) for (x,y) in hc], #unweighted raw events
        y=Float64[integral(y) for (x,y) in hc], #events after xs weight, other weights
    )
    return yi
end

#based on a dataset(with cut) and a data cut, draw the yield table
function yields(indata, data_cut; kwargs...)
    h = makehists(indata, data_cut, {:ljet_eta}, {linspace(-5, 5, 10)}; kwargs...)
    return yields(h;kwargs...)
end

function writehists(ofname, hists)
    writetable("$ofname.csv.mu", todf(mergehists_4comp(hists[:mu])); separator=',')
    writetable("$ofname.csv.ele", todf(mergehists_4comp(hists[:ele])); separator=',')
end

function svfg(fname)
    savefig("$fname.png", bbox_inches="tight", pad_inches=0.2)
    savefig("$fname.pdf", bbox_inches="tight", pad_inches=0.2)
end

function reweight_qcd(indata, inds)
    #stpol/qcd_estimation/fitted_scale_factors.py
    @pyimport fitted_scale_factors
    sfs = fitted_scale_factors.scale_factors
    indata["qcd_weight"] = 1.0
    indata[inds[:data_mu] .* inds[:aiso], :qcd_weight] = 1.0
    indata[inds[:data_ele] .* inds[:aiso], :qcd_weight] = 1.0
    
    for (nj, nt) in [(2,0),(2,1),(3,1),(3,2)]
        indata[inds[:mu] .* inds[:aiso] .* inds[:njets](nj) .* inds[:ntags](nt), :qcd_weight] = sfs["mu"]["$(nj)j$(nt)t"]["mtw"]
        indata[inds[:ele] .* inds[:aiso] .* inds[:njets](nj) .* inds[:ntags](nt), :qcd_weight] = sfs["ele"]["$(nj)j$(nt)t"]["met"] 
    end
end



function biaxes(frac=0.1)
    a1 = PyPlot.plt.axes((0.0, 0.0, 0.5-frac, 1.0));
    a2 = PyPlot.plt.axes((0.5+frac, 0.0, 0.5-frac, 1.0));
    return a1, a2
end


# typealias ErrorsHistogram Histogram;
# import Hist.errors, Hist.normed;
# Hist.errors{T <: ErrorsHistogram}(h::T) = h.bin_entries;

# function Hist.normed{T <: ErrorsHistogram}(h::T)
#     i = integral(h)
#     return Histogram(h.bin_entries/i, h.bin_contents/i, h.bin_edges);
# end

function read_hists(fn)
    t = readtable(fn);
    hists = Dict()
    for i=1:3:length(t)
        cn = colnames(t)
        sname = split(cn[i], "__")[2]
        binscol, errscol, edgescol = cn[i:i+2];
        println(binscol, " ", errscol, " ", edgescol)
        sub = t[:, [errscol, binscol, edgescol]];
        hist = fromdf(sub;entries=:poissonerrors)
        hists[sname] = hist
    end
    return hists
end

