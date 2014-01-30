if !isdefined(:SELECTION)

sample_is(x) = :(sample .== $(hash(x)))

function perform_selection(indata::AbstractDataFrame)
    inds = {
        :mu => (indata["lepton_type"] .== 13) & (indata["n_signal_mu"] .== 1) & (indata["n_signal_ele"] .== 0) & (indata["n_veto_mu"] .== 0) & (indata["n_veto_ele"] .== 0),
        :ele => (indata["lepton_type"] .== 11) & (indata["n_signal_mu"] .== 0) & (indata["n_signal_ele"] .== 1) & (indata["n_veto_mu"] .== 0) & (indata["n_veto_ele"] .== 0),
        :ljet_rms =>indata["ljet_rms"] .> 0.025,
        :mtw =>indata["mtw"] .> 50,
        :met =>indata["met"] .> 45,
        :_mtw => x -> indata["mtw"] .> x,
        :_met => x -> indata["met"] .> x,
        #:_qcd_mva => x -> indata["qcd"] .> x,
        #:qcd_mva027 => indata["qcd"] .> 0.27,
        #:qcd_mva016 => indata["qcd"] .> 0.16,
        :dr => (indata["ljet_dr"] .> 0.5) & (indata["bjet_dr"] .> 0.5),
        :iso => (indata["isolation"] .== ("iso"|>hash|>int)),
        :aiso => (indata["isolation"] .== ("antiiso"|>hash|>int)),
        :data_mu => (indata["sample"] .== ("data_mu"|>hash|>int)),
        :data_ele => (indata["sample"] .== ("data_ele"|>hash|>int)),
        :njets => (n -> indata["njets"] .== n),
        :ntags => (n -> indata["ntags"] .== n),
        :hlt => (n -> indata["hlt_$n"] .== true),
        :sample => (x -> indata["sample"] .== (x|>string|>hash|>int)),
        :systematic => (x -> indata["systematic"] .== (x|>string|>hash|>int)),
        :nominal => ((indata["systematic"] .== ("nominal"|>hash|>int)) | (indata["systematic"] .== ("unknown"|>hash|>int)))
    }
    
    samples = ["data_mu", "data_ele", "tchan", "ttjets", "wjets", "dyjets", "diboson", "gjets", "schan", "twchan"]
    for s in samples
        inds[symbol(s)] = (indata["sample"] .== (s|>string|>hash|>int))
    end
    inds[:data] = (inds[:data_mu] | inds[:data_ele])
    return inds
end

SELECTION = 1

end #if
