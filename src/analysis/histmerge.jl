using ROOT, ROOT.ROOTHistograms
include("base.jl");
using SingleTopBase
import SingleTopBase: FitResult

import SingleTopBase: sfs, reweight_hists_to_fitres
import Reweight: lumis

# const FITRESULTS = {
#     :mu=>FitResult("$BASE/src/fraction_fit/results2/csvt/qcd__mva_nominal/bdt/mu.json"),
#     :ele=>FitResult("$BASE/src/fraction_fit/results2/csvt/qcd__mva_nominal/bdt/ele.json"),
#     #:mu=>FitResult("$BASE/results/fits/apr03/csvt/qcd__mva_nominal/bdt/mu.json"),
#     #:ele=>FitResult("$BASE/results/fits/apr03/csvt/qcd__mva_nominal/bdt/ele.json")
# }

include("$BASE/src/analysis/histkey.jl")
include("$BASE/src/analysis/python_plots.jl")
include("$BASE/src/analysis/hplot.jl");

const fn = "/Users/joosep/Dropbox/kbfi/top/stpol/results/hists/apr08/csvt_mva.root"

classname(o) = ClassName(root_cast(TObject, o))|>bytestring;
#
# function load_rootfile_hists(fn::ASCIIString; hkey_filter=hk->true)
#     tf = TFile(fn)
#     ks = GetListOfKeys(tf)
#
#     hd = Dict{HistKey, Histogram}()
#
#     for i=1:length(ks)
#         i%10000 == 0 && println(i)
#         k = ks[i]
#
#         n = bytestring(GetName(k))
#
#         hkey_filter(n) || continue
#
#         toks = {
#             symbol(x[1])=>string(x[2]) for x in
#             map(x->split(x, "="), split(n, ";"))
#         }
#         hk = HistKey(toks)
#
#
#         o = ReadObj(k)
#         o = to_root(o)
#         cn = classname(o)
#         cn == "TH1D" || continue
#
#         cx, ex, ents, edges = get_hist_bins(o)
#         # if !all(ents .>= 0)
#         #     warn("entries error: $ents")
#         # end
#         hd[hk] = Histogram(ents, cx, edges);
#     end
#     return hd
# end

query(inp, q1::Symbol, q2) =
    collect(filter(x -> getfield(x, q1)==q2, collect(inp)))

function select_histograms(
    hd::Associative,
    lepton::Symbol,
    object::Symbol;
    selection_major::Symbol = :preselection, selection_minor::Symbol = :nothing,
    njets = 2, ntags = 1, dofit = true)

    hists = Dict()

    ks = query(
        keys(hd), :object, object) |>
        x -> query(x, :selection_major, selection_major) |>
        x -> query(x, :selection_minor, selection_minor) |>
        x -> query(x, :lepton, lepton) |>
        x -> query(x, :njets, njets) |>
        x -> query(x, :ntags, ntags) |>
        #x -> filter(y -> y.sample != :wjets_sherpa, x) |>
        x -> filter(y -> y.sample != :tchan_inc, x) |>
        x -> filter(y -> y.sample != :wjets_inc, x) |>
        collect;

    #println("$ks")
    length(ks)==0 && error("nothing selected!")

    ds = symbol("data_$lepton")
    d = query(ks, :sample, ds) |> z -> query(z, :iso, :iso) |>
        z -> query(z, :scenario, :unweighted) |> collect
    length(d) == 1 || error("unable to select data: $ds, $lepton, $object")
    d = first(d)

    hists["DATA"] = hd[d]

    for x in vcat(mcsamples, :wjets__light, :wjets__heavy)
        q = query(ks, :sample, x) |> z -> query(z, :iso, :iso)

        #get systematic variations
        for sc in filter(y->y[2]==x, keys(scenarios))
            #println("sc = [", join(sc, ","), "]")

            sc[1] == :nominal && continue
            scen = scenarios[sc]
            #println("scen = $scen")

            syst = nothing
            try
                syst = get(REV_SYSTEMATICS_TABLE, sc[1], sc[1])
            catch
                syst = sc[1]
            end

            _q = query(q, :systematic, scen.systematic) |>
                z -> query(
                    z, :scenario,
                    get(SYSTEMATICS_TABLE, scen.weight_scenario, scen.weight_scenario)
                )
            h = length(_q) == 1 ? hd[first(_q)] : (
            warn("ambigous systematic query: $sc, $(length(_q))");
                Histogram(hists["DATA"].bin_edges)
            )
            hists["$(x)__$(sc[1])"] = lumis[lepton] * h
        end

        _q = query(q, :scenario, :nominal) |> z -> query(z, :systematic, :nominal)
        hists[string(x)] = length(_q) == 1 ? hd[first(_q)] : (
            warn("ambigous nominal query: $x, $(length(_q))");
            Histogram(hists["DATA"].bin_edges)
        )
        hists[string(x)] = lumis[lepton] * hists[string(x)]

    end

    d = query(ks, :sample, ds) |>
        z -> query(z, :iso, :antiiso) |> collect

    if length(d)!=1
        warn("could not select antiiso data")
        hists["qcd"] = Histogram(hists["DATA"].bin_edges)

        hists["antiiso_data"] = hists["qcd"]
        hists["antiiso_mc"] = Dict()
    else
        d = first(d)
        mcs = query(ks, :iso, :antiiso) |>
            z->query(z, :scenario, :nominal) |>
            z->query(z, :systematic, :nominal) |> collect
        #println("aiso mcs $(length(mcs))")
        mcs = {k.sample => k for k in mcs}
        #println("aiso mcs $(length(mcs)) ")

        sf = get(sfs[string(lepton)], "$(njets)j$(ntags)t", {"qcd_mva"=>1.0})["qcd_mva"]
        hists["qcd"] = hd[d];
        #println("anti-iso data: ", hists["qcd"])
        summc = Histogram(hists["qcd"].bin_edges)
        for k in [:ttjets, :wjets, :tchan, :diboson, :dyjets]
            if haskey(mcs, k)
                #println("anti-iso mc $k ", hd[mcs[k]])
                summc += lumis[lepton] * hd[mcs[k]]
            else
                println("anti-iso MC $k not found")
            end
        end
        #println("anti-iso data before scaling, MC subtraction: \n", hists["qcd"])
        #println("sumMC: \n", summc)

        hists["qcd"] = hists["qcd"] - summc
        hists["qcd"] = sf * hists["qcd"]

        hists["antiiso_data"] = hd[d]
        hists["antiiso_mc"] = {k=>hd[v] for (k,v) in mcs}
    end

    if dofit
        println("applying fit coefficients: ", join(FITRESULTS[lepton].means, ", "))
        hists = reweight_hists_to_fitres(FITRESULTS[lepton], hists)
    end
    return hists
end
