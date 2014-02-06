module Cuts
    const qcd_mva_wps = {
        :mu=>0.16,
        :ele=>0.27
    }

    is_mu(indata) = (
        (abs(indata[:lepton_type] .== 13)) & (indata[:n_signal_mu] .== 1) &
        (indata[:n_signal_ele] .== 0) & (indata[:n_veto_mu] .== 0) &
        (indata[:n_veto_ele] .== 0) & indata[:hlt_mu]
    )

    is_ele(indata) = (
        (abs(indata[:lepton_type] .== 11)) & (indata[:n_signal_mu] .== 0) &
        (indata[:n_signal_ele] .== 1) & (indata[:n_veto_mu] .== 0) &
        (indata[:n_veto_ele] .== 0) & indata[:hlt_ele]
    )
    function is_reco_lepton(row, lepton::Symbol)
        lepton==:mu && return is_mu(row)
        lepton==:ele && return is_ele(row)
        return false
    end

    njets(indata, x) = indata[:njets].==x
    ntags(indata, x) = indata[:ntags].==x
    qcd_mva(indata, x::Real) = indata[:bdt_qcd].>x
    bdt(indata, x::Real) = indata[:bdt_sig_bg].>x
    qcd_mva_wp(indata, x::Symbol) = qcd_mva(indata, qcd_mva_wps[x])
    iso(indata) = indata[:isolation] .== hmap_symb_from[:iso] 
    aiso(indata) = indata[:isolation] .== hmap_symb_from[:antiiso]
    dr(indata) = (indata[:ljet_dr].>0.5) & (indata[:bjet_dr].>0.5)

    function truelepton(indata, x::Symbol)
        x == :mu && return abs(indata[:gen_lepton_id]) .== 13
        x == :ele && return abs(indata[:gen_lepton_id]) .== 11
        return false
    end
end

if !isdefined(:SELECTION)

using DataFrames

function perform_selection(indata::AbstractDataFrame)
    inds = {
        :mu => Cuts.ismu(indata),
        :ele => Cuts.isele(indata),
        :ljet_rms =>indata[:ljet_rms] .> 0.025,
        :mtw =>indata[:mtw] .> 50,
        :met =>indata[:met] .> 45,
        ##:_mtw => x -> indata[:mtw] .> x,
        ##:_met => x -> indata[:met] .> x,
        ##:_qcd_mva => x -> indata[:qcd] .> x,
        :qcd_mva_027 => indata[:bdt_qcd] .> 0.27,
        :qcd_mva_016 => indata[:bdt_qcd] .> 0.16,
        :dr => (indata[:ljet_dr] .> 0.5) & (indata[:bjet_dr] .> 0.5),
        :iso => (indata[:isolation] .== ("iso"|>hash|>int)),
        :aiso => (indata[:isolation] .== ("antiiso"|>hash|>int)),
        :njets => {k=>indata[:njets].==k for k in [2,3]},
        :ntags => {k=>indata[:ntags].==k for k in [0,1,2]},
        ##:bdt_grid => {k=>indata[:bdt_sig_bg].>k for k in linspace(-1, 1, 11)},
        :hlt => {k=>indata[symbol("hlt_$k")] for k in [:mu, :ele]},
        :sample => {k=>indata[:sample].==(k|>string|>hash|>int) for k in [:data_mu, :data_ele, :tchan, :ttjets, :wjets, :dyjets, :diboson, :gjets, :schan, :twchan, :qcd_mc_mu, :qcd_mc_ele]},
        :systematic => {k=>indata[:systematic].==(k|>string|>hash|>int) for k in [:nominal, :unknown, :EnUp, :EnDown, :ResUp, :ResDown, :UnclusteredEnUp, :UnclusteredEnDown]},
        :truelepton => {
            :mu=>abs(indata[:gen_lepton_id]).==13,
            :ele=>abs(indata[:gen_lepton_id]).==11
        }
    }
    
    inds[:data] = (inds[:sample][:data_mu] | inds[:sample][:data_ele])
    inds[:mc] = !inds[:data]
    inds[:qcd_mva] = {:mu=>inds[:qcd_mva_016], :ele=>inds[:qcd_mva_027]}
    return inds
end

const SELECTION = 1

end #if
