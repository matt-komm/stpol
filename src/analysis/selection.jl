
module Cuts
    using DataFrames
    import DataFrames.isna
    import SingleTopBase: hmap_symb_from, hmap_symb_to

    const qcd_mva_wps = {
        :mu=>0.4,
        :ele=>0.55
    }

    is_mu(indata) = (
        !(isna(indata[:n_veto_mu])) &
        !(isna(indata[:n_veto_ele])) &
        (abs(indata[:lepton_type]) .== 13) & (indata[:n_signal_mu] .== int32(1)) &
        (indata[:n_signal_ele] .== int32(0)) & (indata[:n_veto_mu] .== int32(0)) &
        (indata[:n_veto_ele] .== int32(0)) & indata[:hlt_mu]
    )

    is_ele(indata) = (
        !(isna(indata[:n_veto_mu])) &
        !(isna(indata[:n_veto_ele])) &
        (abs(indata[:lepton_type]) .== 11) & (indata[:n_signal_mu] .== 0) &
        (indata[:n_signal_ele] .== 1) & (indata[:n_veto_mu] .== 0) &
        (indata[:n_veto_ele] .== 0) & indata[:hlt_ele]
    )
    function is_reco_lepton(row, lepton::Symbol)
        lepton==:mu && return is_mu(row)
        lepton==:ele && return is_ele(row)
        error("unecognized lepton=$lepton")
    end

    njets(indata, x) = indata[:njets] .== x
    ntags(indata, x) = indata[:ntags] .== x
    qcd_mva(indata, x::Real) = indata[:bdt_qcd] .> x
    bdt(indata, x::Real, bdtvar=:bdt_sig_bg) = indata[bdtvar] .> x

    function qcd_cut(indata, cut_type::Symbol, lepton::Symbol)
        cut_type == :mva_nominal && return qcd_mva_wp(indata, lepton)
        cut_type == :metmtw_nominal && return qcd_met_mtw(indata, lepton)
        error("unrecognized cut_type=$cut_type")
    end

    qcd_mva_wp(indata, x::Symbol) = qcd_mva(indata, qcd_mva_wps[x])

    function qcd_met_mtw(indata, x::Symbol)
        x == :mu && return ((!isna(indata[:mtw])) & (indata[:mtw] .> 50))
        x == :ele && return ((!isna(indata[:met])) & (indata[:met] .> 45))
    end

    iso(indata) = int(indata[:isolation]) .== hmap_symb_to[:iso]
    aiso(indata) = int(indata[:isolation]) .== hmap_symb_to[:antiiso]
    dr(indata) = (
        aiso(indata) & (indata[:ljet_dr] .> 0.3) & (indata[:bjet_dr] .> 0.3)
    ) | iso(indata)

    cutbased_etajprime(indata) = (
        (abs(indata[:ljet_eta]) .> 2.5) &
        (indata[:top_mass] < 220) &
        (indata[:top_mass] > 130)
    )

    function truelepton(indata, x::Symbol)
        x == :mu && return abs(indata[:gen_lepton_id]) .== 13
        x == :ele && return abs(indata[:gen_lepton_id]) .== 11
        return false
    end

    function selection(indata, selection_major, selection_minor)
        selection_major == :bdt && return bdt(indata, selection_minor)
        error("unrecognized selection_major = $selection_major")
    end

    function nu_soltype(indata, soltype::Symbol)
        soltype == :real && return indata[:nu_soltype] .== 0
        soltype == :cplx && return indata[:nu_soltype] .== 1
        soltype == :none && return true
        error("unrecognized soltype=$soltype")
    end
    ljet_rms(indata) = indata[:ljet_rms] .< 0.025
end


function pass_selection(reco::Bool, bdt_cut::Float64, reco_lepton::Symbol, row::DataFrameRow)
    if reco && !is_any_na(row, :njets, :ntags, :bdt_sig_bg, :n_signal_mu, :n_signal_ele, :n_veto_mu, :n_veto_ele)::Bool

        reco = reco && sel(row) && Cuts.bdt(row, bdt_cut)

        if reco && Cuts.is_reco_lepton(row, reco_lepton) # && Cuts.truelepton(row, :mu)::Bool
            reco = reco && Cuts.qcd_mva_wp(row, reco_lepton)
        else
            reco = false
        end
    else
        reco = false
    end
    return reco
end
