using ROOT, DataFrames
include("histo.jl")
using Hist
include("hroot2.jl")
include("fit.jl")
include("python_plots.jl")
include("hplot.jl")
include("fit.jl")
include("../fraction_fit/hists.jl")

lep = :mu;

tf = "output/bdt_scan/hists/0.40000/$lep/cos_theta_lj.root"
tf2 = "output/bdt_scan/hists/0.40000/$lep/tmatrix_nocharge__gen_mu.root"

hd = load_hists_from_file(tf)
ax = axes()
dd = similar(DataFrame(name=ASCIIString[], integral=Float64[]), length(hd));
i = 1
for (k, v) in hd
    eplot(ax, v)
    dd[i, :name] = k
    dd[i, :integral] = integral(v)
    i += 1
end
grid()
ylim(bottom=0)
