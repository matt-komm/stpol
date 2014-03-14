#!/home/joosep/.julia/ROOT/julia

include("base.jl");
include("$BASE/src/analysis/hplot.jl");
include("$BASE/src/analysis/pyplot.jl");

inf = jldopen("/home/joosep/singletop/output/skims/feb15.jld", "r";mmaparrays=true)
df = read(inf, "df")
inds = read(inf, "index")

function draw(var, bins; nj=2, nt=1, apply_fit=false)
    h = Dict()
    for lep in [:mu, :ele]
        h[lep] = makehists(
            ND, NI, NI[:njets][nj]&NI[:ntags][nt]&NI[lep]&NI[:dr]&NI[:hlt][lep], NI[:sample][symbol("data_$lep")],
            var, bins,
            row->nominal_weight(row)*row[:lumi], row->qcd_weight(row)*row[:lumi]
        )
        if apply_fit
            reweight_hists_to_fitres(FITRESULTS[lep], h[lep])
        end
    end

    (fig, (ar1, a1, ar2, a2)) = ratio_axes2()
    
    draw_data_mc_stackplot(a1, h[:mu]);
    draw_data_mc_stackplot(a2, h[:ele]);
    
    ar1[:set_xlim](minimum(bins), maximum(bins))
    ar2[:set_xlim](minimum(bins), maximum(bins))

    a1[:grid](true, which="both")
    a2[:grid](true, which="both")
    return fig 
end

df[:qcd_weight] = 1.0;
df[:lumi] = 1.0;
df[!inds[:data]&inds[:mu], :lumi] = lumis[:mu]
df[!inds[:data]&inds[:ele], :lumi] = lumis[:ele]

ND = sub(df, inds[:systematic][:nominal]|inds[:systematic][:unknown])
NI = perform_selection(ND)
reweight_qcd(ND, NI)

WS = row->nominal_weight(row)*row[:lumi], row->qcd_weight(row)*row[:lumi]

draw(:bdt_sig_bg, linspace(-1, 1, 30))
svfg("p1")
close()

draw(:bdt_sig_bg, linspace(-1, 1, 30); apply_fit=true)
svfg("p2")
close()

