
sample_is(x) = :(sample .== $x)

selections = {
    :mu => :(lepton_type .== 13),
    :ele => :(lepton_type .== 11),
    :dr => :((ljet_dr .> 0.5) .* (bjet_dr .> 0.5)),
    :iso => :(isolation .== "iso"),
    :aiso => :(isolation .== "antiiso"),
    :ntags => n -> :(ntags .== $n),
    :njets => n -> :(njets .== $n),
}

function perform_selection(indata)
    inds = {
        :mu => (indata["lepton_type"] .== 13) .* (indata["n_signal_mu"] .== 1) .* (indata["n_signal_ele"] .== 0) .* (indata["n_veto_mu"] .== 0) .* (indata["n_veto_ele"] .== 0),
        :ele => (indata["lepton_type"] .== 11) .* (indata["n_signal_mu"] .== 0) .* (indata["n_signal_ele"] .== 1) .* (indata["n_veto_mu"] .== 0) .* (indata["n_veto_ele"] .== 0),
        :ljet_rms =>indata["ljet_rms"] .> 0.025,
        :mtw =>indata["mtw"] .> 50,
        :met =>indata["met"] .> 45,
        :dr => (indata["ljet_dr"] .> 0.5) .* (indata["bjet_dr"] .> 0.5),
        :iso => indata["isolation"] .== "iso",
        :aiso => indata["isolation"] .== "antiiso",
        :data_mu => indata["sample"] .== "data_mu",
        :data_ele => indata["sample"] .== "data_ele",
        :njets => n -> indata["njets"] .== n,
        :ntags => n -> indata["ntags"] .== n,
        :hlt => n -> indata["hlt_$n"] .== true,
    }
    
    samples = ["data_mu", "data_ele", "tchan", "ttjets", "wjets", "dyjets", "diboson", "gjets", "schan", "twchan"]
    for s in samples
        inds[symbol(s)] = indata["sample"] .== s
    end
    return inds
end
