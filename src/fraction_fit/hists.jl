function makehists(
    data::AbstractDataFrame, inds,
    sel, dsel,
    var::Symbol, binning::AbstractVector{Float64},
    weight_ex=nominal_weight, qcdweight_ex=qcd_weight
  )

    hists = Dict()

    for k in procs
        df = sub(data, inds[:sample][k] & inds[:iso] & sel)
        hists[k] = makehist_1d(df, var, binning, weight_ex)
    end

    aiso_mc = {
        p=>makehist_1d(sub(data, inds[:sample][p] & inds[:aiso] & sel), var, binning, qcdweight_ex)
        for p in mcsamples
    }
    sum_aiso_mc = aiso_mc |> values |> collect |> sum
    
    df = sub(data, inds[:data] & inds[:aiso] & sel & dsel)
    hists[(:antiiso, :mc)] = sum_aiso_mc
    hists[(:antiiso, :data)] = makehist_1d(df, var, binning, (df::DataFrameRow)->df[:qcd_weight])
    hists[:qcd] = hists[(:antiiso, :data)] - hists[(:antiiso, :mc)]

    hists[:DATA] = makehist_1d(
        sub(data, inds[:data] & inds[:iso] & sel & dsel), 
        var, binning, (df::DataFrameRow)->1.0);

    all([h.bin_edges==hists[:DATA].bin_edges for h in values(hists)]) ||
        (error("not all histograms have the same binning:\n --- \n $hists \n --- \n"))

    return {string(k)=>v for (k,v) in hists}
end

function makehist_1d(df::AbstractDataFrame, var::Symbol, binning::AbstractVector{Float64}, weight_f::Function)
    hi = Histogram(binning)
    sumw = 0.0
    for row in eachrow(df)
        const x = row[var]
        const w = weight_f(row)
        hfill!(hi, x, w)
        sumw += w
    end
    #println("meanw = $(sumw/nrow(df))")
    return hi
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

# todf(bins, errs, edges) =
#     DataFrame(bins=bins, errs=errs, edges=edges);

# function todf(h::Histogram)
#     errs = (sqrt(h.bin_entries) ./ h.bin_entries .* h.bin_contents) 
#     for i=1:length(errs)
#         if !(errs[i] > 0)
#             errs[i] = 0.0
#         end
#     end 
#     return DataFrame(
#         bins=h.bin_contents,
#         errs=errs,
#         edges=h.bin_edges
#     );
# end

todf(h::Histogram) = DataFrame(
    bin_edges=h.bin_edges,
    bin_contents=contents(h),
    bin_entries=entries(h),
    bin_errors=errors(h),
)

function todf(h::NHistogram)
    hist = todf(h.baseh)
    return {:hist=>hist, :edges=>[DataFrame(e) for e in h.edges]}
end

function todf(d::Associative)
    tot_df = DataFrame()
    for (k, v) in d
        df = todf(v)
        for cn in names(df)
            rename!(df, symbol(cn), symbol("$(cn)__$(k)"))
        end
        tot_df = hcat(tot_df, df)
    end
    return tot_df
end

function reweight_to_fitres(frd, indata, inds)
    indata["fitweight"] = 1.0
    for (lep, fr) in frd
        means = {k=>v for (k,v) in zip(fr.names, fr.means)}
        si = inds[lep]
        indata[si & (inds[:tchan]), :fitweight] = means["beta_signal"]
        indata[si & (inds[:wjets] | inds[:gjets] | inds[:dyjets] | inds[:diboson]), :fitweight] = means["wzjets"]
        indata[si & (inds[:ttjets] | inds[:schan] | inds[:twchan]), :fitweight] = means["ttjets"]
        #indata[si & inds[:aiso], :fitweight] = means["qcd"]
    end
end

function reweight_hists_to_fitres(fr, hists)
    means = {k=>v for (k,v) in zip(fr.names, fr.means)}

    function weightall(a, b)
        for k in keys(hists)
            if contains(k, a)
                hists[k] = hists[k] * means[b]
            end
        end
    end

    for s in ["wjets", "gjets", "dyjets", "diboson"]
        weightall(s, "wzjets")
    end

    for s in ["ttjets", "twchan", "schan"]
        weightall(s, "ttjets")
    end
    #weightall("qcd", "qcd")
end

#@pyimport scipy.stats.kde as KDE
#@pyimport matplotlib.cm as cmap
#function kde_contour(arr, X, Y, n=6; kwargs...)
#    k = KDE.gaussian_kde(transpose(matrix(arr)));
#    xy = zeros(Float64, (2,length(X)*length(Y)));
#    n = 1
#    for x in X
#      for y in Y
#        xy[1,n] = x
#        xy[2,n] = y
#        n += 1
#      end
#    end
#    Z = reshape(k[:__call__](xy), (length(X), length(Y)));
#    contour(X,Y,Z; kwargs...)
#end

#function yield_table(a, x, y, yieldsd)
#    tx = "DEBUG\n"
#    for (k, v) in sort(collect(yieldsd), by=x->x[2], rev=true)
#      if k == "DATA"
#        continue
#      end
#      tx = string(tx, k, @sprintf(": %.1f\n", v))
#    end
#
#    a[:text](x, y, tx, alpha=0.4, color="black", size="x-small");
#end

#plots a comparison of the ele and mu channels, stacked format

function writehists(ofname, hists)
    println("writing histograms to $ofname")

    writetable("$ofname.csv.mu", todf(mergehists_4comp(hists[:mu])); separator=',')
    writetable("$ofname.csv.ele", todf(mergehists_4comp(hists[:ele])); separator=',')
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
        uy=Int64[int(sum(y.bin_entries)) for (x,y) in hc], #unweighted raw events
        y=Float64[integral(y) for (x,y) in hc], #events after xs weight, other weights
    )
    return yi
end

#based on a dataset(with cut) and a data cut, draw the yield table
function yields(indata, data_cut; kwargs...)
    h = makehists(indata, data_cut, {:ljet_eta}, {linspace(-5, 5, 10)}; kwargs...)
    return yields(h;kwargs...)
end

function read_hists(fn)
   t = readtable(fn);
   hists = Dict()
   for i=1:3:length(t)
       cn = names(t)
       sname = split(string(cn[i]), "__")[2]
       binscol, errscol, edgescol = cn[i:i+2];
       #println(binscol, " ", errscol, " ", edgescol)
       sub = t[:, [edgescol, errscol, binscol]];
       hist = fromdf(sub;entries=:poissonerrors)
       hists[sname] = hist
   end
   return hists
end
#
#function toroot{T <: Any, H <: Histogram}(hd::Associative{T, H}, fn)
#    tn = tempname()
#    df = todf(hd)
#    writetable(tn, df)
#    cmd = `$BASE/src/fraction_fit/rootwrap.sh python $BASE/src/fraction_fit/convert.py $tn $fn`
#    rm(tn)
#end
