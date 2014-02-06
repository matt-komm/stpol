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


#load the fit results
frd = {
    :mu=>FitResult("$BASE/results/bdt_fit/results/jan16/fits/2j1t_3j2t/mu/results.json"),
    :ele=>FitResult("$BASE/results/bdt_fit/results/jan16/fits/2j1t_3j2t/ele/results.json")
};

tm = prep_transfermatrix(hists)
for (k, v) in tm
    #println("converting 2D histogram $k to $outdir/tmatrix.root/$k")
    toroot("$outdir/tmatrix.root", string(k), v::NHistogram, {"GEN", "RECO"})

    projx = project_x(v)
    toroot("$outdir/tmatrix.root", "$(k)__proj_x", projx::Histogram, "RECO")

    projy = project_y(v)
    toroot("$outdir/tmatrix.root", "$(k)__proj_y", projy::Histogram, "GEN")
end


for lep in [:mu, :ele]
    h = merge_histogram(:mu, hists, :cos_theta_lj, 2, 1)
    od = "$outdir/$lep"
    for (k, v) in h
        hi = toroot("$od/cos_theta_lj.root", "2j1t_cos_theta_lj__$(k)", v::Histogram, "RECO")
    end

    if any(map(x->x[:obj]==:bdt_sig_bg, allkeys))

        for (nj, nt) in [(2,1), (3,2)]
            ss = "$(nj)j$(nt)t"
            h = merge_histogram(:mu, hists, :bdt_sig_bg, nj, nt)
            for (k, v) in h
                hi = toroot("$od/bdt_sig_bg_$(ss)__merged.root", "$(ss)_bdt_sig_bg__$(k)", v::Histogram, "RECO")
            end

            merged = mergehists_4comp(h)
            for (k, v) in merged
                hi = toroot("$od/bdt_sig_bg_$(ss)__merged.root", "$(ss)_bdt_sig_bg__$(k)", v::Histogram, "RECO")
            end
            writetable("$od/bdt_sig_bg_$(ss)__merged.csv", todf(merged))
        end
    end
end
