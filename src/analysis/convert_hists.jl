println("convert_hists.jl, JLD->ROOT conversion")
include("base.jl")
include("$BASE/src/analysis/systematics_gather.jl")
include("$BASE/src/analysis/hroot.jl")
include("$BASE/src/analysis/fit.jl");

println("loading histograms...")

infile = ARGS[2]
outdir = ARGS[1]

!ispath(outdir) && mkpath(outdir)

hists = Dict()
fi = jldopen(inf)
hists = read(fi, "ret")
println("histograms opened: $(length(hists))")

h = merge_histogram(hists, :mu, :cos_theta_lj, :bdt, symbol("0.20000"), 2, 1)
println(h)

#tm = prep_transfermatrix(hists)
#for (k, v) in tm
#    toroot("$outdir/tmatrix.root", string(k), v::NHistogram, {"cos #theta GEN", "cos #theta RECO"})
#
#    projx = project_x(v)
#    toroot("$outdir/tmatrix.root", "$(k)__proj_y", projx::Histogram, "cos #theta RECO")
#
#    projy = project_y(v)
#    toroot("$outdir/tmatrix.root", "$(k)__proj_x", projy::Histogram, "cos #theta GEN")
#    #println("$k $(integral(v)) $(integral(projx)) $(integral(projy))")
#end

#tm = prep_transfermatrix(hists, separate_lepton_charge=false)
#println("transfer matrices")
#for (k, v) in tm
#    toroot("$outdir/tmatrix_nocharge.root", string(k), v::NHistogram, {"cos #theta GEN", "cos #theta RECO"})
#
#    projx = project_x(v)
#    toroot("$outdir/tmatrix_nocharge.root", "$(k)__proj_y", projx::Histogram, "cos #theta RECO")
#
#    projy = project_y(v)
#    toroot("$outdir/tmatrix_nocharge.root", "$(k)__proj_x", projy::Histogram, "cos #theta GEN")
#end

#for lep in [:mu, :ele]
#    h = merge_histogram(lep, hists, :cos_theta_lj, 2, 1,
#        selfn=k -> (:purification in keys(k) && k[:purification]==:bdt_sig_bg && k[:bdt_cut]==-1.0)
#    )
#    od = "$outdir/$lep"
#    mkpath("$od/csv")
#    mkpath("$od/csv/merged")
#
#    #reweight_hists_to_fitres(FITRESULTS[lep], h)
#
#    for (k, v) in h
#        toroot("$od/cos_theta_lj.root", "2j1t_cos_theta_lj__$(k)", v::Histogram, "cos #theta RECO")
#        writetable("$od/csv/cos_theta_lj__$(k).csv", todf(v))
#    end
#
#    merged = mergehists_4comp(h)
#    for (k, v) in merged
#        toroot("$od/merged/cos_theta_lj.root", "2j1t_cos_theta_lj__$(k)", v::Histogram, "cos #theta RECO")
#        writetable("$od/csv/merged/cos_theta_lj__$(k).csv", todf(v))
#    end
#
#
#    ###
#    ### BDT
#    ###
#
#    if any(map(x->x[:obj]==:bdt_sig_bg, allkeys))
#
#        for (nj, nt) in [(2,1), (3,2)]
#            ss = "$(nj)j$(nt)t"
#            h = merge_histogram(lep, hists, :bdt_sig_bg, nj, nt;selfn=k->!(:purification in keys(k)))
#            for (k, v) in h
#                toroot("$od/bdt_sig_bg_$(ss).root", "$(ss)_bdt_sig_bg__$(k)", v::Histogram, "BDT")
#                writetable("$od/csv/bdt_sig_bg_$(ss)__$(k).csv", todf(v))
#            end
#
#            merged = mergehists_4comp(h)
#            for (k, v) in merged
#                toroot("$od/merged/bdt_sig_bg_$(ss).root", "$(ss)_bdt_sig_bg__$(k)", v::Histogram, "BDT")
#                writetable("$od/csv/merged/bdt_sig_bg_$(ss)__$(k).csv", todf(v))
#            end
#            writetable("$od/csv/bdt_sig_bg_$(ss)__merged.csv", todf(merged))
#        end
#    end
#end
