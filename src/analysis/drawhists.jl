#!/home/joosep/.julia/ROOT/julia
error("this file is deprecated")
ENV["PYTHONPATH"]=join("../../qcd_estimation")

include("../fraction_fit/hists.jl");
include("../analysis/util.jl");

using DataFrames
mkpath(PDIR)
mkpath(HDIR)

indata = readdf("$BASE/results/data.jld")
#indata = readdf("/scratch/joosep/test.jld")
println("opened data S=$(size(indata))")

println("performing selection")
tic()
inds = perform_selection(indata);
toc()

reweight_qcd(indata, inds)
frd = {
  :mu=>FitResult("$BASE/src/fraction_fit/results/dec13/2j1t_3j2t/mu/results.json"),
  :ele=>FitResult("$BASE/src/fraction_fit/results/dec13/2j1t_3j2t/ele/results.json")
};
reweight_to_fitres(frd, indata, inds);

wex = {:qcd=>:(xsweight .* totweight), :qcd_fractionfit=>:(xsweight .* totweight .* fitweight)}

#println("c variable 2j1t")
#tic()
#ret = channel_comparison(
#    indata, df, inds[:njets](2) .* inds[:ntags](1) .* inds[:dr],
#    :C, linspace(0, 1, 30),
#    {:mu=>(inds[:hlt](:mu) .* inds[:mu] .* inds[:mtw]), :ele=>(inds[:hlt](:ele) .* inds[:ele] .* inds[:met])};
#    weight_ex=wex[:qcd],
#)
#svfg("$PDIR/c__2j1t_hmet")
#writehists("$HDIR/c__2j1t_hmet", ret[:hists])
#toc()

println("bdt 2j1t qcd mva")
tic()
ret = channel_comparison(indata, inds, (inds[:njets](2) & inds[:ntags](1) & inds[:dr] & inds[:nominal]),
    :bdt_sig_bg, linspace(-1, 1, 20),
    {:mu=>inds[:hlt](:mu) & inds[:mu] & inds[:qcd_mva016], :ele=>inds[:hlt](:ele) & inds[:ele] & inds[:qcd_mva027]},
    weight_ex=wex[:qcd]
)
svfg("$PDIR/bdt__2j1t_hmet_qcd_mva_mu_016_ele_027")
writehists("$HDIR/bdt__2j1t_hmet_qcd_mva_mu_016_ele_027", ret[:hists])
toc()

println("bdt 3j2t qcd mva")
tic()
ret = channel_comparison(
    indata, df, inds[:njets](3) .* inds[:ntags](2) .* inds[:dr],
    :bdt_sig_bg, linspace(-1, 1, 20),
    {:mu=>inds[:hlt](:mu) .* inds[:mu] .* inds[:qcd_mva016], :ele=>inds[:hlt](:ele) .* inds[:ele] .* inds[:qcd_mva027]},
    weight_ex=wex[:qcd]
)
svfg("$PDIR/bdt__3j2t_hmet_qcd_mva_mu_016_ele_027")
writehists("$HDIR/bdt__3j2t_hmet_qcd_mva_mu_016_ele_027", ret[:hists])
toc()

println("bdt 2j1t")
tic()
ret = channel_comparison(
    indata, df, inds[:njets](2) .* inds[:ntags](1) .* inds[:dr],
    :bdt_sig_bg, linspace(-1, 1, 20), 
    {:mu=>inds[:hlt](:mu) .* inds[:mu] .* inds[:mtw], :ele=>inds[:hlt](:ele) .* inds[:ele] .* inds[:met]};
    weight_ex=wex[:qcd]
)
svfg("$PDIR/bdt__2j1t_hmet")
writehists("$HDIR/bdt__2j1t_hmet", ret[:hists])
toc()

#println("scanning over BDT")
#for bdt_cut in linspace(-1, 1, 11)
#    println("cos_theta 2j1t, bdt>$(bdt_cut)")
#    tic()
#
#    bdt_inds = indata["bdt_sig_bg"] .> bdt_cut
#
#    ret = channel_comparison(
#        indata, df, inds[:njets](2) .* inds[:ntags](1) .* inds[:dr] .* bdt_inds,
#        :cos_theta_lj, linspace(-1, 1, 20), 
#        {:mu=>inds[:hlt](:mu) .* inds[:mu] .* inds[:mtw], :ele=>inds[:hlt](:ele) .* inds[:ele] .* inds[:met]};
#        weight_ex=wex[:qcd_fractionfit]
#    )
#    bdts = @sprintf("%.2f", bdt_cut)
#
#    svfg("$PDIR/cos_theta__2j1t_bdt_$(bdts)_hmet")
#    writehists("$HDIR/cos_theta__2j1t_bdt_$(bdts)_hmet", ret[:hists])
#    toc()
#end


#println("bdt 3j1t")
#tic()
#ret = channel_comparison(
#    indata, df, inds[:njets](3) .* inds[:ntags](1) .* inds[:dr],
#    :bdt_sig_bg, linspace(-1, 1, 20),
#    {:mu=>inds[:hlt](:mu) .* inds[:mu] .* inds[:mtw], :ele=>inds[:hlt](:ele) .* inds[:ele] .* inds[:met]},
#    weight_ex=wex[:qcd]
#)
#svfg("$PDIR/bdt__3j1t_hmet")
#writehists("$HDIR/bdt__3j1t_hmet", ret[:hists])
#toc()

println("bdt 3j2t")
tic()
ret = channel_comparison(
    indata, df, inds[:njets](3) .* inds[:ntags](2) .* inds[:dr],
    :bdt_sig_bg, linspace(-1, 1, 20),
    {:mu=>inds[:hlt](:mu) .* inds[:mu] .* inds[:mtw], :ele=>inds[:hlt](:ele) .* inds[:ele] .* inds[:met]},
    weight_ex=wex[:qcd]
)
svfg("$PDIR/bdt__3j2t_hmet")
writehists("$HDIR/bdt__3j2t_hmet", ret[:hists])
toc()

println("bdt 2j1t mtw in ele channel")
tic()
ret = channel_comparison(
    indata, df, inds[:njets](2) .* inds[:ntags](1) .* inds[:dr],
    :bdt_sig_bg, linspace(-1, 1, 20), 
    {:mu=>inds[:hlt](:mu) .* inds[:mu] .* inds[:mtw], :ele=>inds[:hlt](:ele) .* inds[:ele] .* inds[:_mtw](60)};
    weight_ex=wex[:qcd]
)
svfg("$PDIR/bdt__2j1t_hmet_ele_mtw60")
writehists("$HDIR/bdt__2j1t_hmet_ele_mtw60", ret[:hists])
toc()

#println("bdt 3j1t mtw")
#tic()
#ret = channel_comparison(
#    indata, df, inds[:njets](3) .* inds[:ntags](1) .* inds[:dr],
#    :bdt_sig_bg, linspace(-1, 1, 20),
#    {:mu=>inds[:hlt](:mu) .* inds[:mu] .* inds[:mtw], :ele=>inds[:hlt](:ele) .* inds[:ele] .* inds[:_mtw](60)},
#    weight_ex=wex[:qcd]
#)
#svfg("$PDIR/bdt__3j1t_hmet_mtw60")
#writehists("$HDIR/bdt__3j1t_hmet_mtw60", ret[:hists])
#toc()

println("bdt 3j2t mtw in ele channel")
tic()
ret = channel_comparison(
    indata, df, inds[:njets](3) .* inds[:ntags](2) .* inds[:dr],
    :bdt_sig_bg, linspace(-1, 1, 20),
    {:mu=>inds[:hlt](:mu) .* inds[:mu] .* inds[:mtw], :ele=>inds[:hlt](:ele) .* inds[:ele] .* inds[:_mtw](60)},
    weight_ex=wex[:qcd]
)
svfg("$PDIR/bdt__3j2t_hmet_ele_mtw60")
writehists("$HDIR/bdt__3j2t_hmet_ele_mtw60", ret[:hists])
toc()

#println("met 2j1t")
#tic()
#ret = channel_comparison(
#    indata, df, inds[:njets](2) .* inds[:ntags](1) .* inds[:dr],
#    :met, linspace(0, 150, 30),
#    {:mu=>inds[:hlt](:mu) .* inds[:mu], :ele=>inds[:hlt](:ele) .* inds[:ele]},
#    weight_ex=wex[:qcd]
#)
#svfg("$PDIR/met__2j1t")
#writehists("$HDIR/met__2j1t_hmet", ret[:hists])
#toc()
#
#println("met 3j1t")
#tic()
#ret = channel_comparison(
#    indata, df, inds[:njets](3) .* inds[:ntags](1) .* inds[:dr],
#    :met, linspace(0, 150, 30),
#    {:mu=>inds[:hlt](:mu) .* inds[:mu], :ele=>inds[:hlt](:ele) .* inds[:ele]},
#    weight_ex=wex[:qcd]
#)
#svfg("$PDIR/met__3j1t")
#writehists("$HDIR/met__3j1t_hmet", ret[:hists])
#toc()
#
#println("met 3j2t")
#tic()
#ret = channel_comparison(
#    indata, df, inds[:njets](3) .* inds[:ntags](2) .* inds[:dr],
#    :met, linspace(0, 150, 30),
#    {:mu=>inds[:hlt](:mu) .* inds[:mu], :ele=>inds[:hlt](:ele) .* inds[:ele]},
#    weight_ex=wex[:qcd]
#)
#svfg("$PDIR/met__3j2t")
#writehists("$HDIR/met__3j2t_hmet", ret[:hists])
#toc()
#
#println("mtw 2j1t")
#tic()
#ret = channel_comparison(
#    indata, df, inds[:njets](2) .* inds[:ntags](1) .* inds[:dr],
#    :mtw, linspace(0, 250, 30),
#    {:mu=>inds[:hlt](:mu) .* inds[:mu], :ele=>inds[:hlt](:ele) .* inds[:ele]},
#    weight_ex=wex[:qcd]
#)
#svfg("$PDIR/mtw__2j1t")
#writehists("$HDIR/mtw__2j1t_hmet", ret[:hists])
#toc()
#
#println("mtw 3j1t")
#tic()
#ret = channel_comparison(
#    indata, df, inds[:njets](3) .* inds[:ntags](1) .* inds[:dr],
#    :mtw, linspace(0, 250, 30),
#    {:mu=>inds[:hlt](:mu) .* inds[:mu], :ele=>inds[:hlt](:ele) .* inds[:ele]},
#    weight_ex=wex[:qcd]
#)
#svfg("$PDIR/mtw__3j1t")
#writehists("$HDIR/mtw__3j1t_hmet", ret[:hists])
#toc()
#
#println("mtw 3j2t")
#tic()
#ret = channel_comparison(
#    indata, df, inds[:njets](3) .* inds[:ntags](2) .* inds[:dr],
#    :mtw, linspace(0, 250, 30),
#    {:mu=>inds[:hlt](:mu) .* inds[:mu], :ele=>inds[:hlt](:ele) .* inds[:ele]},
#    weight_ex=wex[:qcd]
#)
#svfg("$PDIR/mtw__3j2t")
#writehists("$HDIR/mtw__3j2t_hmet", ret[:hists])
#toc()

#println("bdt 2j0t")
#tic()
#ret = channel_comparison(
#    indata, inds[:njets](2) .* inds[:ntags](0) .* inds[:dr],
#    :bdt_sig_bg, linspace(-1, 1, 10), 
#    {:mu=>inds[:hlt](:mu) .* inds[:mu] .* inds[:mtw], :ele=>inds[:hlt](:ele) .* inds[:ele] .* inds[:met]};
#    cols=[:bdt_sig_bg, :xsweight, :totweight, :sample, :isolation, :qcd_weight, :pu_weight],
#    weight_ex=:(xsweight .* totweight .* qcd_weight)
#)
#svfg("$PDIR/bdt__2j0t_hmet.png")
#writehists("$HDIR/bdt__2j0t_hmet", ret[:hists])
#toc()

#println("top mass 2j1t")
#tic()
#ret = channel_comparison(
#    indata, df, inds[:njets](2) .* inds[:ntags](1) .* inds[:dr],
#    :top_mass, linspace(80, 350, 30),
#    {:mu=>(inds[:hlt](:mu) .* inds[:mu] .* inds[:mtw]), :ele=>inds[:hlt](:ele) .* inds[:ele] .* inds[:met]}
#)
#svfg("$PDIR/mtop__2j1t_hmet")
#writehists("$HDIR/mtop__2j1t_hmet", ret[:hists])
#toc()
#
#println("top mass 3j1t")
#tic()
#ret = channel_comparison(
#    indata, df, inds[:njets](3) .* inds[:ntags](1) .* inds[:dr],
#    :top_mass, linspace(80, 350, 30),
#    {:mu=>(inds[:hlt](:mu) .* inds[:mu] .* inds[:mtw]), :ele=>inds[:hlt](:ele) .* inds[:ele] .* inds[:met]}
#)
#svfg("$PDIR/mtop__3j1t_hmet")
#writehists("$HDIR/mtop__3j1t_hmet", ret[:hists])
#toc()
#
#println("top mass 3j2t")
#tic()
#ret = channel_comparison(
#    indata, df, inds[:njets](3) .* inds[:ntags](2) .* inds[:dr],
#    :top_mass, linspace(80, 350, 30),
#    {:mu=>(inds[:hlt](:mu) .* inds[:mu] .* inds[:mtw]), :ele=>inds[:hlt](:ele) .* inds[:ele] .* inds[:met]}
#)
#svfg("$PDIR/mtop__3j2t_hmet")
#writehists("$HDIR/mtop__3j2t_hmet", ret[:hists])
#toc()
#
#println("ljet eta 2j1t")
#tic()
#ret = channel_comparison(
#    indata, df, inds[:njets](2) .* inds[:ntags](1) .* inds[:dr],
#    :(abs(ljet_eta)), linspace(0, 5.0, 30),
#    {:mu=>inds[:hlt](:mu) .* inds[:mu] .* inds[:mtw], :ele=>inds[:hlt](:ele) .* inds[:ele] .* inds[:met]}
#)
#svfg("$PDIR/abs_ljet_eta__2j1t_hmet")
#writehists("$HDIR/abs_ljet_eta__2j1t_hmet", ret[:hists])
#toc()
#
#println("ljet eta 3j1t")
#tic()
#ret = channel_comparison(
#    indata, df, inds[:njets](3) .* inds[:ntags](1) .* inds[:dr],
#    :(abs(ljet_eta)), linspace(0, 5.0, 30),
#    {:mu=>inds[:hlt](:mu) .* inds[:mu] .* inds[:mtw], :ele=>inds[:hlt](:ele) .* inds[:ele] .* inds[:met]}
#)
#svfg("$PDIR/abs_ljet_eta__3j1t_hmet")
#writehists("$HDIR/abs_ljet_eta__3j1t_hmet", ret[:hists])
#toc()
#
#println("ljet eta 3j2t")
#tic()
#ret = channel_comparison(
#    indata, df, inds[:njets](3) .* inds[:ntags](2) .* inds[:dr],
#    :(abs(ljet_eta)), linspace(0, 5.0, 30),
#    {:mu=>inds[:hlt](:mu) .* inds[:mu] .* inds[:mtw], :ele=>inds[:hlt](:ele) .* inds[:ele] .* inds[:met]}
#)
#svfg("$PDIR/abs_ljet_eta__3j2t_hmet")
#writehists("$HDIR/abs_ljet_eta__3j2t_hmet", ret[:hists])
#toc()
