using PyCall, PyPlot
using Distributions
using Histograms

function draw_data_mc_stackplot(ax, hists;order=nothing,wjets_split=false,kwd...)
    draws = [
        ("dyjets", hists["dyjets"], {:color=>"purple", :label=>"DY-jets"}),
        ("diboson", hists["diboson"], {:color=>"blue", :label=>"diboson"}),
        ("schan", hists["schan"], {:color=>"yellow", :label=>"s-channel"}),
        ("twchan", hists["twchan"], {:color=>"Gold", :label=>"tW-channel"}),
        ("gjets_qcd", hists["gjets"]+hists["qcd"], {:color=>"gray", :label=>"QCD, \$ \\gamma \$-jets"}),
        #("gjets", hists["gjets"], {:color=>"gray", :label=>"\$ \\gamma \$-jets"}),
        #("qcd", hists["qcd"], {:color=>"gray", :label=>"QCD"}),
        #("wjets", hists["wjets"], {:color=>"green", :label=>"W+jets"}),

    ]
    if wjets_split
        append!(draws, [
            ("wjets__light", hists["wjets__light"], {:color=>"lightgreen", :label=>"W+jets (l)"}),
            ("wjets__heavy", hists["wjets__heavy"], {:color=>"darkgreen", :label=>"W+jets (bc)"})
        ])
    else
        append!(draws, [
            ("wjets", hists["wjets"], {:color=>"green", :label=>"W+jets"}),
        ])
    end

    append!(draws, [
        ("ttjets", hists["ttjets"], {:color=>"orange", :label=>"\$ t \\bar{t} \$"}),
        ("tchan", hists["tchan"], {:color=>"red", :label=>"t-channel"})
    ])

    #create a dictionary
    dd = {k[1]=>k for k in draws}

    order = order==nothing ? [k[1] for k in draws] : order
    hlist = Histogram[dd[o][2] for o in order]
    arglist = Dict{Any, Any}[dd[o][3] for o in order]

    hplot(
        ax, hlist, arglist,
        common_args=merge({:edgecolor=>"none", :linewidth=>0.0}, {k=>v for (k, v) in kwd})
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

    # for k in sort(collect(keys(yieldsd)))
    #     println("$k ", @sprintf("%.0f", integral(yieldsd[k])))
    # end

    eplot(ax, hists["DATA"], ls="", marker="o", color="black", label="Data")
    ax[:set_ylim](bottom=0)
end

function data_mc_stackplot(
    df::AbstractDataFrame,
    inds, sel::DataVector{Bool},
    dsel::DataVector{Bool}, ax::PyObject,
    var, bins; kwargs...
    )
    kwd = {k=>v for (k,v) in kwargs}
    order = pop!(kwd, :order, nothing)

    bar_args = Dict()
    if pop!(kwd, :logy, false)
        bar_args[:log] = true
    end

    hists = makehists(
        df, inds, sel, dsel,
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
    return hists
end

function ratio_hist(hists)
    mc = reduce(
        +, Histogram(hists["DATA"].bin_edges), [
        hists[k] for k in [
            "tchan", "ttjets", "wjets",
            "qcd", "gjets", "twchan",
            "schan", "diboson", "dyjets"
        ]
    ])

    data = reduce(
        +, Histogram(hists["DATA"].bin_edges),
        [v for (k,v) in filter(x -> x[1] == "DATA", collect(hists))]
    )

    mcs = [(!isna(x) && x>0) ? Poisson(int(round(x))) : Poisson(1) for x in entries(mc)]
    datas = [(!isna(x) && x>0) ? Poisson(int(round(x))) : Poisson(1) for x in entries(data)]
    N = 10000

    errs = Array(Float64, (2, length(mcs)))
    means = Array(Float64, length(mcs))

    for i=1:length(mcs)
        m = float(rand(mcs[i], N)) * mc.bin_contents[i] / mc.bin_entries[i]
        d = rand(datas[i], N)
        v = (d-m)./d
        v = Float32[isna(_v) || isnan(_v) ? 0 : _v for _v in v]
        err_up, mean, err_down = quantile(v, 0.68), quantile(v, 0.5), quantile(v, 0.32)
        errs[1,i] = abs(mean-err_down)
        errs[2,i] = abs(mean-err_up)
        means[i] = mean
    end

    return means, errs
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

function rslegend(a; do_reverse=true, x...)
    handles, labels = a[:get_legend_handles_labels]()
    f = do_reverse ? reverse : x->x
    return a[:legend](
        f(handles), f(labels),
        loc="center left",
        bbox_to_anchor=(1, 0.5),
        numpoints=1,
        fancybox=true; x...
    )
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
    nb = nbins(hdata)
    means, errs = ratio_hist(h)

    a[:errorbar](midpoints(hdata.bin_edges), means[1:nb-1], errs[:, 1:nb-1], ls="", marker=".", color="black"; kwargs...)
    a[:axhline](0.0, color="black")
    a[:grid]()

    return means, errs
end

function biaxes(frac=0.1)
    a1 = PyPlot.plt.axes((0.0, 0.0, 0.5-frac, 1.0));
    a2 = PyPlot.plt.axes((0.5+frac, 0.0, 0.5-frac, 1.0));
    return a1, a2
end


function svfg(fname)
    mkpath(dirname(fname))
    #savefig("$fname.png", bbox_inches="tight", pad_inches=0.4)
    savefig("$fname.pdf", bbox_inches="tight", pad_inches=0.4)
    close()
end
#
# function channel_comparison(
#     data::AbstractDataFrame, inds, sel::DataVector{Bool}, var::Union(Expr, Symbol), bins, sels; kwargs...
#     )
#     kwd = {k=>v for (k,v) in kwargs}
#
#     if :varname in keys(kwd)
#         varname = pop!(kwd, :varname)
#     elseif var in keys(VARS)
#         varname = VARS[var]
#     else
#         error("provide xlabel either through global VARS or :varname kwd")
#     end
#
#     (fig, (a11, a12, a21, a22)) = ratio_axes2();
#
#     hmu = data_mc_stackplot(
#         data, inds, sel&sels[:mu], inds[:data_mu],
#         a12,
#         {var}, {bins}; kwd...
#     );
#     hele = data_mc_stackplot(
#         data, inds, sel&sels[:ele], inds[:data_ele],
#         a22,
#         {var}, {bins}; kwd...
#     );
#
#     ymu = yields(hmu)
#     yele = yields(hele)
#     yt = hcat(ymu, yele)
#     #println(yt)
#
#     a12[:set_title]("\$ \\mu \$")
#     a22[:set_title]("\$ e \$")
#
#     a12[:grid]();
#     a22[:grid]();
#
#     errorbars(a11, hmu);
#     errorbars(a21, hele);
#
#     rslegend(a22);
#
#     a21[:set_ylabel]("(Data - MC) / Data")
#
#     lowlim = 0
#     if :logy in keys(kwd) && kwd[:logy]
#         lowlim = 10
#     end
#     a12[:set_ylim](bottom=lowlim)
#     a22[:set_ylim](bottom=lowlim)
#
#     a11[:set_xlabel](varname, size="x-large")
#     a21[:set_xlabel](varname, size="x-large")
#
#     return {
#         :figure=>fig,
#         :yields=>{:mu=>ymu, :ele=>yele},
#         :hists=>{:mu=>hmu, :ele=>hele}
#     }
# end

function mc_variated_keys(
    hists::Associative, systematic::ASCIIString, direction=nothing
    )

    ret = Any[]
    systematic = (systematic !="nominal" ? "$(systematic)__$(direction)" : systematic)
    for s in TOTAL_SAMPLES
        k = "$(s)__$(systematic)"

        #variated if exists, otherwise nominal
        k = k in keys(hists) ? k : s
        push!(ret, string(k))
    end

    ret
end

function total_mc_variated(
    hists::Associative, systematic::ASCIIString, direction=nothing
    )

    #println("mc_variated_keys=", join(mc_variated_keys(hists, systematic, direction), ", "))

    sum([hists[h] |> contents
            for h in mc_variated_keys(hists, systematic, direction)
        ]
    )
end

total_stat_error(
    hists::Associative
    ) = sqrt(
    sum([
        (errors(hists[h])).^2
        for h in mc_variated_keys(hists, "nominal", nothing)
    ])
)

function deltaerr(
    hists::Associative,
    systematics::Vector{ASCIIString},
    normed
    )
    N = total_mc_variated(hists, "nominal")[1:end-1]

    function normf(syst, direction)
        tot_var = total_mc_variated(hists, syst, direction)[1:end-1]

        #normed to nominal yield
        if normed
            tot_var = (sum(N) / sum(tot_var)) .* tot_var
        end

        return tot_var
    end

    #fully uncorrelated, sum in quadrature of template variations
    #f(direction) = [(N - normf(s, direction)).^2 for s in systematics] |> sum |> sqrt

    #fully correlated, simple sum of template variations from nominal
    f(direction) = [abs(normf(s, direction) - N) for s in systematics] |> sum

    return f("up"), f("down")
end

function tot_syst_err(
    hists::Associative,
    systematics_unnormed::Vector{ASCIIString},
    systematics_normed::Vector{ASCIIString}
    )

    #unnormalized variations
    du1, dd1 = deltaerr(hists, systematics_unnormed, false);

    #normalized variations
    du2, dd2 = deltaerr(hists, systematics_normed, true);

    du = sqrt(du1.^2 + du2.^2)
    dd = sqrt(dd1.^2 + dd2.^2)
    return du, dd
end

function draw_errband(
    axes::PyObject,
    hists::Associative;
    log=false,
    systematics_unnormed::Vector{ASCIIString}=ASCIIString[
        "ttjets_scale", "wzjets_scale", "tchan_scale"
    ],
    systematics_normed::Vector{ASCIIString}=[
        "matching",
        "jes", "jer",
        "mass",
        "met",
        "lepton_id", "lepton_iso", "lepton_trigger",
        "pu", "btag_bc", "btag_l"
    ]
    )

    N = total_mc_variated(hists, "nominal")[1:end-1]


    du, dd = tot_syst_err(hists, systematics_unnormed, systematics_normed)

    se = total_stat_error(hists)[1:end-1]
    tot_du = sqrt(du.^2 + se.^2)
    tot_dd = sqrt(dd.^2 + se.^2)

    #println("lows = ", join(N - tot_dd, ", "))
    #println("highs = ", join(tot_du + tot_dd, ", "))
    axes[:bar](
        lowedge(hists["DATA"].bin_edges),
        tot_du + tot_dd,
        widths(hists["DATA"].bin_edges),
        N - tot_dd,
        edgecolor="grey",
        color="grey",
        fill=false,
        linewidth=0,
        hatch="///",
        label="uncertainty";
        log=log
    )

    return tot_du, tot_dd

    # axes[:bar](
    #     lowedge(hists["DATA"].bin_edges),
    #     dd+du,
    #     widths(hists["DATA"].bin_edges),
    #     N - dd,
    #     edgecolor="black",
    #     color="black",
    #     fill=false,
    #     linewidth=0,
    #     hatch="\\\\",
    #     label="systematic\nuncertainty";
    #     log=log
    # )
end

cmspaper(ax, x, y, lumi=20; additional_text="") = text(
    x, y,
    "CMS \$ \\sqrt{s}=8\$ TeV \n \$ L_{int}=$lumi\\ fb^{-1}\$\n$additional_text",
    transform=ax[:transAxes], horizontalalignment="center", verticalalignment="top"
)

function combdraw(
    hists, var::Symbol;
    log=false, plot_title="",
    loc_paperstring=(:top, :right), titletext=""
    )
    fig, (ax, rax) = ratio_axes()

    draw_data_mc_stackplot(ax, hists;log=log,wjets_split=true);
    ax[:set_ylim](bottom=log?10:0)
    ax[:grid](true, which="both")
    tot_du, tot_dd = draw_errband(ax, hists;
        log=log
    )
    means, errs = errorbars(rax, hists)

    mc = reduce(
    +, Histogram(hists["DATA"].bin_edges), [
            hists[k] for k in [
                "tchan", "ttjets", "wjets",
                "qcd", "gjets", "twchan",
                "schan", "diboson", "dyjets"
            ]
    ]);
    #println(hcat(tot_dd, mc.bin_contents[1:end-1], hists["DATA"].bin_contents[1:end-1], tot_du))

    mup = (hists["DATA"].bin_contents[1:end-1] - (mc.bin_contents[1:end-1] + tot_du)) ./ hists["DATA"].bin_contents[1:end-1]
    mdown = (hists["DATA"].bin_contents[1:end-1] - (mc.bin_contents[1:end-1] - tot_dd)) ./ hists["DATA"].bin_contents[1:end-1]

    rax[:bar](
        lowedge(hists["DATA"].bin_edges),
        mdown - mup,
        widths(hists["DATA"].bin_edges),
        mup,
        edgecolor="grey",
        color="grey",
        fill=false,
        linewidth=0,
        hatch="///",
    )
#     rax[:plot](midpoints(hists["DATA"].bin_edges), mdown, marker=".")
#     rax[:plot](midpoints(hists["DATA"].bin_edges), mup, marker=".")

    if loc_paperstring == (:top, :right)
        cmspaper(ax, 0.8, 0.97, additional_text=titletext)
    elseif loc_paperstring == (:top, :left)
        cmspaper(ax, 0.22, 0.97, additional_text=titletext)
    end
    ax[:set_title](plot_title)
    rax[:set_xlabel](VARS[var], fontsize=22)
    rax[:set_ylabel]("\$ \\frac{D - M}{D} \$")
    rslegend(ax)
    ax[:set_ylim](top=maximum(contents(hists["DATA"])) * 1.3)

    return ax, rax, mup, mdown, means[1:end-1]
end

lepton_string = {:mu=>"\$\\mu^\\pm \$", :ele=>"\$e^\\pm \$"}
title_string(nj, nt, lepton) = "$(nj)J$(nt)T $(lepton_string[lepton])"


function systematics_comparison(hists, varname, sample, syst; frac=0.5, savename=nothing)
    fig, (ax1, ax2) = ratio_axes(frac=0.5)
    title("systematic template for $sample, $syst")

    nom = hists["$(sample)"]
    hup = hists["$(sample)__$(syst)__up"]
    hdown = hists["$(sample)__$(syst)__down"]

    ints(h) = @sprintf("Y=%.0f N=%.0f", integral(h), sum(entries(h)))
    eplot(ax1, nom, label="nominal $(ints(nom))", drawstyle="steps-mid")
    eplot(ax1, hup, label="up $(ints(hup))", drawstyle="steps-mid")
    eplot(ax1, hdown, label="down $(ints(hdown))", drawstyle="steps-mid")
    hupn = integral(nom)/integral(hup) * hup
    hdownn = integral(nom)/integral(hdown) * hdown
    eplot(ax1, hupn, label="up (normed)", drawstyle="steps-mid")
    eplot(ax1, hdownn, label="down (normed)", drawstyle="steps-mid")

    ax1[:set_ylabel]("expected event yield")

    ax2[:set_ylim](1.0 - frac, 1.0 + frac)
    eplot(ax2, divide_noerr(nom, nom), drawstyle="steps-mid")
    eplot(ax2, divide_noerr(hup, nom), drawstyle="steps-mid")
    eplot(ax2, divide_noerr(hdown, nom), drawstyle="steps-mid")
    eplot(ax2, divide_noerr(hupn, nom), drawstyle="steps-mid")
    eplot(ax2, divide_noerr(hdownn, nom), drawstyle="steps-mid")


    ax2[:grid](which="both")
    ax2[:set_ylabel]("ratio nominal / variated")
    ax2[:set_xlabel](VARS[varname], fontsize="16")
    ylim(bottom=0)
    rslegend(ax1, do_reverse=false)
    grid()
    if savename!=nothing
        svfg("$(savename)/$(sample)_$(syst)")
    end

end

function variation_plots(hists, varname, savename)
    systematics_comparison(hists, varname, "tchan", "btag_bc", frac=0.05, savename=savename)
    systematics_comparison(hists, varname, "tchan", "btag_l", frac=0.005, savename=savename)
    systematics_comparison(hists, varname, "tchan", "mass", savename=savename)
    systematics_comparison(hists, varname, "tchan", "jes", savename=savename)
    systematics_comparison(hists, varname, "tchan", "jer", savename=savename)
    systematics_comparison(hists, varname, "tchan", "scale", savename=savename)

    systematics_comparison(hists, varname, "ttjets", "btag_bc", frac=0.05, savename=savename)
    systematics_comparison(hists, varname, "ttjets", "btag_l", frac=0.005, savename=savename)
    systematics_comparison(hists, varname, "ttjets", "mass", savename=savename)
    systematics_comparison(hists, varname, "ttjets", "jes", savename=savename)
    systematics_comparison(hists, varname, "ttjets", "jer", savename=savename)
    systematics_comparison(hists, varname, "ttjets", "scale", savename=savename)
    systematics_comparison(hists, varname, "ttjets", "matching", savename=savename)
    systematics_comparison(hists, varname, "ttjets", "top_weight", frac=0.2, savename=savename)

    systematics_comparison(hists, varname, "wjets", "btag_bc", frac=0.05, savename=savename)
    systematics_comparison(hists, varname, "wjets", "btag_l", frac=0.05, savename=savename)
    systematics_comparison(hists, varname, "wjets", "jes", savename=savename)
    systematics_comparison(hists, varname, "wjets", "jer", savename=savename)
    systematics_comparison(hists, varname, "wjets", "matching", frac=1.0, savename=savename)
    systematics_comparison(hists, varname, "wjets", "wjets_shape", frac=0.2, savename=savename)
end
