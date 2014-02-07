println("convert_hists.jl, JLD->ROOT conversion")
include("base.jl")
include("$BASE/src/analysis/systematics_gather.jl")
include("$BASE/src/analysis/hroot.jl")
include("$BASE/src/analysis/fit.jl");

println("loading histograms...")
tic()

infile = ARGS[1]
outdir = ARGS[2]
println("converting $infile to $outdir")
!ispath(outdir) && mkpath(outdir)

fi = jldopen(infile)

const hists = read(fi, "ret")
allkeys = filter(x->typeof(x)<:Dict, keys(hists))

toc()

tm = prep_transfermatrix(hists)
for (k, v) in tm
    toroot("$outdir/tmatrix.root", string(k), v::NHistogram, {"GEN", "RECO"})

    projx = project_x(v)
    toroot("$outdir/tmatrix.root", "$(k)__proj_y", projx::Histogram, "RECO")

    projy = project_y(v)
    toroot("$outdir/tmatrix.root", "$(k)__proj_x", projy::Histogram, "GEN")
    #println("$k $(integral(v)) $(integral(projx)) $(integral(projy))")
end


for lep in [:mu, :ele]
    h = merge_histogram(lep, hists, :cos_theta_lj, 2, 1)
    od = "$outdir/$lep"
    reweight_hists_to_fitres(FITRESULTS[lep], h)

    for (k, v) in h
        hi = toroot("$od/cos_theta_lj.root", "2j1t_cos_theta_lj__$(k)", v::Histogram, "RECO")
    end

    if any(map(x->x[:obj]==:bdt_sig_bg, allkeys))

        for (nj, nt) in [(2,1), (3,2)]
            ss = "$(nj)j$(nt)t"
            h = merge_histogram(lep, hists, :bdt_sig_bg, nj, nt)
            for (k, v) in h
                hi = toroot("$od/bdt_sig_bg_$(ss).root", "$(ss)_bdt_sig_bg__$(k)", v::Histogram, "RECO")
            end

            merged = mergehists_4comp(h)
            for (k, v) in merged
                hi = toroot("$od/merged/bdt_sig_bg_$(ss).root", "$(ss)_bdt_sig_bg__$(k)", v::Histogram, "RECO")
            end
            writetable("$od/bdt_sig_bg_$(ss)__merged.csv", todf(merged))
        end
    end
end
