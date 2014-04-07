
module Cuts
    using DataFrames
    import DataFrames.isna

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

    njets(indata, x) = indata[:njets].==x
    ntags(indata, x) = indata[:ntags].==x
    qcd_mva(indata, x::Real) = indata[:bdt_qcd].>x
    bdt(indata, x::Real) = indata[:bdt_sig_bg].>x

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

    iso(indata) = indata[:isolation] .== hmap_symb_from[:iso] 
    aiso(indata) = indata[:isolation] .== hmap_symb_from[:antiiso]
    dr(indata) = (indata[:ljet_dr].>0.5) & (indata[:bjet_dr].>0.5)

    cutbased_etajprime(indata) = (
        (abs(indata[:ljet_eta]).>2.5) &
        (indata[:top_mass]<220) &
        (indata[:top_mass] > 130)
    )

    function truelepton(indata, x::Symbol)
        x == :mu && return abs(indata[:gen_lepton_id]) .== 13
        x == :ele && return abs(indata[:gen_lepton_id]) .== 11
        return false
    end

    function selection(indata, selection_major, selection_minor)
        selection_major == :bdt && return bdt(indata, selection_minor)
        error("unrecognized selection_major=$selection_major")
    end
end

if !isdefined(:SELECTION)

using DataFrames

function perform_selection(indata::AbstractDataFrame)
    inds = {
        :mu => Cuts.is_mu(indata),
        :ele => Cuts.is_ele(indata),
        :ljet_rms =>indata[:ljet_rms] .> 0.025,
        :mtw =>indata[:mtw] .> 50,
        :met =>indata[:met] .> 45,
        ##:_mtw => x -> indata[:mtw] .> x,
        ##:_met => x -> indata[:met] .> x,
        ##:_qcd_mva => x -> indata[:qcd] .> x,
        :qcd_mva_mu => indata[:bdt_qcd] .> 0.4,
        :qcd_mva_ele => indata[:bdt_qcd] .> 0.55,
        :dr => (indata[:ljet_dr] .> 0.5) & (indata[:bjet_dr] .> 0.5),
        :iso => (indata[:isolation] .== ("iso"|>hash|>int)),
        :aiso => (indata[:isolation] .== ("antiiso"|>hash|>int)),
        :njets => {k=>indata[:njets].==k for k in [2,3]},
        :ntags => {k=>indata[:ntags].==k for k in [0,1,2]},
        ##:bdt_grid => {k=>indata[:bdt_sig_bg].>k for k in linspace(-1, 1, 11)},
        :hlt => {k=>indata[symbol("hlt_$k")] for k in [:mu, :ele]},
        :sample => {k=>indata[:sample].==(k|>string|>hash|>int) for k in [:data_mu, :data_ele, :tchan, :ttjets, :wjets, :dyjets, :diboson, :gjets, :schan, :twchan, :qcd_mc_mu, :qcd_mc_ele]},
        :systematic => {k=>indata[:systematic].==(k|>string|>hash|>int) for k in [
            :nominal, :unknown,
            :EnUp, :EnDown,
            :ResUp, :ResDown,
            :UnclusteredEnUp, :UnclusteredEnDown,
            symbol("signal_comphep_anomWtb-unphys"),
            symbol("signal_comphep_anomWtb-0100"),
            symbol("signal_comphep_nominal")
        ]},
        :truelepton => {
            :mu=>abs(indata[:gen_lepton_id]).==13,
            :ele=>abs(indata[:gen_lepton_id]).==11
        }
    }
    
    inds[:data] = (inds[:sample][:data_mu] | inds[:sample][:data_ele])
    inds[:mc] = !inds[:data]
    return inds
end

const SELECTION = 1

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
