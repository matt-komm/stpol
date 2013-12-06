include("hists.jl")

ofdir = "/Users/joosep/Documents/stpol/src/fraction_fit/results"
mkpath("$ofdir/hists")

#nbins = nedges - 1 (low_1, low_2, ..., low_n, high_n)
nedges = 4

data_exprs = {
    :mu => :(sample .== "data_mu"),
    :ele => :(sample .== "data_ele")
}

sels = {
    :mu => inds[:mu] .* inds[:dr] .* inds[:mtw] .* inds[:ljet_rms],
    :ele => inds[:ele] .* inds[:dr] .* inds[:met] .* inds[:ljet_rms],
}

for chan in [:mu, :ele]
    mkpath("$ofdir/hists/$chan")
    println("projecting histograms for channel=$chan")

    de = data_exprs[chan]

    println("data selection expression de=$de")

    df = indata[sels[chan], :]
    println("mc+data events $(nrow(df))")

    println("writing 1D bdt_sig_bg histograms")
    hists = makehists(
        df, de,
        :(bdt_sig_bg),
        linspace(-1, 1, 20)
    ) |> mergehists;
    writetable("$ofdir/hists/$chan/bdt_sig_bg.csv", to_df(hists));

    println("writing 3D top_mass/ljet_eta/mtw histograms")
    hists = makehists(
        df, de,
        [:(top_mass), :(abs(ljet_eta)), :(C)],
        {linspace(80, 400, nedges), linspace(0, 4.5, nedges), linspace(0, 1, nedges)}
    ) |> mergehists;
    writetable("$ofdir/hists/$chan/top_mass_AND_ljet_eta_AND_C.csv", to_df(hists));

    println("writing 3D bdt_sig_bg1/bdt_sig_bg2/bdt_bg1_bg2 histograms")
    hists = makehists(
        df, de,
        [:(bdt_sig_bg1), :(bdt_sig_bg2), :(bdt_bg1_bg2)],
        {linspace(-1, 1, nedges), linspace(-1, 1, nedges), linspace(-1, 1, nedges)}
    ) |> mergehists;
    writetable("$ofdir/hists/$chan/bdt_sig_bg1_AND_bdt_sig_bg2_AND_bdt_bg1_bg2.csv", to_df(hists));
end
