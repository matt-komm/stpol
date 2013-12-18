
sample_is(x) = :(sample .== $x)

const selections = {
    :mu => :((lepton_type .== 13) .* (n_signal_mu .== 1) .* (n_signal_ele .== 0)),
    :ele => :((lepton_type .== 11) .* (n_signal_mu .== 0) .* (n_signal_ele .== 1)),
    :vetolep => :((n_veto_mu .== 0) .* (n_veto_ele .== 0)),
    :dr => :((ljet_dr .> 0.5) .* (bjet_dr .> 0.5)),
    :hlt => {:mu=>:(hlt_mu .== true), :ele=>:(hlt_ele .== true)},
    :iso => :(isolation .== "iso"),
    :aiso => :(isolation .== "antiiso"),
    :ntags => {k=>:(ntags .== $k) for k in [0,1,2]},
    :njets => {k=>:(njets .== $k) for k in [2,3]},
    :ljet_rms => :(ljet_rms .< 0.025),
    :mtw => {k=>:(mtw .> $k) for k in [20, 30, 40, 50]},
    :met => {k=>:(met .> $k) for k in [20, 30, 40, 45, 50]},
    :sample => {
        k=>:(sample .== $k)
        for k in [
            "data_mu", "data_ele", "tchan",
            "ttjets", "wjets", "dyjets",
            "diboson", "gjets", "schan",
            "twchan", "wjets_sherpa"
        ]
    },
    :systematic => {k=>:(systematic .== $k)
        for k in [
            "nominal", "ResUp", "ResDown",
            "EnUp", "EnDown", "scaleup",
            "scaledown", "matchingup", "matchingdown",
            "wjets_fsim_nominal"
        ]
    },
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
        :sample => (x -> indata["sample"] .== x),
        :nominal => ((indata["systematic"] .== "nominal") .+ (indata["systematic"] .== "unknown"))
    }
    
    samples = ["data_mu", "data_ele", "tchan", "ttjets", "wjets", "dyjets", "diboson", "gjets", "schan", "twchan"]
    for s in samples
        inds[symbol(s)] = indata["sample"] .== s
    end
#
#    for s in ["gjets", "wjets", "ttjets", "tchan"]
#        muind = inds[:iso] .* inds[:sample](s) .* inds[:hlt](:mu) .* inds[:mu] .* inds[:njets](2) .* inds[:ntags](1) .* inds[:mtw] .* inds[:ljet_rms]
#        eleind = inds[:iso] .* inds[:sample](s) .* inds[:hlt](:ele) .* inds[:ele] .* inds[:njets](2) .* inds[:ntags](1) .* inds[:met] .* inds[:ljet_rms]
#       
#        mud = indata[muind, :xsweight]
#        eled = indata[eleind, :xsweight]
#
#        println("FY ", s, " mu ", length(mud), " ", sum(mud))
#        println("FY ", s, " ele ", length(eled), " ", sum(eled))
#    end
#
    return inds
end

function load_selection(selfile)
    _inds = read(jldopen(selfile), "inds");
    inds = {
        :mu => _inds[{:sel, :mu}],
        :ele => _inds[{:sel, :ele}],
        :ljet_rms => _inds[{:sel, :ljet_rms}],
        :mtw => _inds[{:sel, :mtw, 50}],
        :met => _inds[{:sel, :met, 45}],
        :dr => _inds[{:sel, :dr}],
        :iso => _inds[{:sel, :iso}],
        :aiso => _inds[{:sel, :aiso}],
        #:data_mu => _inds[{:sel, :sample, "data_mu"}]
        #:data_ele => 
        :njets => n -> _inds[{:sel, :njets, n}],
        :ntags => n -> _inds[{:sel, :ntags, n}],
        :hlt => lep -> _inds[{:sel, :hlt, lep}],
        :sample => x -> _inds[{:sel, :sample, x}]
    }
    
    samples = ["data_mu", "data_ele", "tchan", "ttjets", "wjets", "dyjets", "diboson", "gjets", "schan", "twchan"]
    for s in samples
        inds[symbol(s)] = _inds[{:sel, :sample, s}]
    end
    return inds
end

function recurse_down(sel::Expr, prev)
    s = join(prev, "->")
    #println("Expr: [$s] => $sel")
    return (prev, sel)
end

function recurse_down{R <: Any}(sel::AbstractArray{R}, prev)
    return vcat([recurse_down(x, prev) for x in sel]...)
end

function recurse_down{A <: Any, B <: Any}(sel::Associative{A, B}, prev)
    return vcat([recurse_down(v, vcat(prev, k)) for (k, v) in sel]...)
end

const flatsel = recurse_down(selections, Any[:sel])
