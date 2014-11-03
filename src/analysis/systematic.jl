#if !isdefined(:SYSTEMATICS)

try
    import ..B_WEIGHT_NOMINAL
catch err
end
if !isdefined(:B_WEIGHT_NOMINAL)
    global B_WEIGHT_NOMINAL
    B_WEIGHT_NOMINAL = :b_weight
end

const SYSTEMATICS_TABLE = {
    :mass178_5=>:mass2__up,
    :mass175_5=>:mass__up,

    :mass169_5=>:mass__down,
    :mass166_5=>:mass2__down,
    :nominal=>:nominal,
    :unweighted=>:unweighted,

    :EnUp=>:jes__up,
    :EnDown=>:jes__down,

    :UnclusteredEnUp=>:met__up,
    :UnclusteredEnDown=>:met__down,

    :ResUp=>:jer__up,
    :ResDown=>:jer__down,

    :scaleup=>:scale__up,
    :scaledown=>:scale__down,

    :matchingup=>:matching__up,
    :matchingdown=>:matching__down,
    :matchingdown_v1=>:matching__down,
    :matchingdown_v2=>:matching__down,

    :pu_weight__up => :pu__up,
    :pu_weight__down => :pu__down,

    :top_weight__up => :top_weight__up,
    :top_weight__down => :top_weight__down,

    :lepton_weight__id__up => :lepton_id__up,
    :lepton_weight__id__down => :lepton_id__down,
    :lepton_weight__iso__up => :lepton_iso__up,
    :lepton_weight__iso__down => :lepton_iso__down,
    :lepton_weight__trigger__up => :lepton_trigger__up,
    :lepton_weight__trigger__down => :lepton_trigger__down,
    :b_weight__bc__up => :btag_bc__up,
    :b_weight__bc__down => :btag_bc__down,
    :b_weight__l__up => :btag_l__up,
    :b_weight__l__down => :btag_l__down,

    :wjets_shape__unweighted => :wjets_shape__unweighted,
    :wjets_shape__up => :wjets_shape__up,
    :wjets_shape__down => :wjets_shape__down,

    :wjets_flavour_heavy__up => :wjets_flavour_heavy__up,
    :wjets_flavour_heavy__down => :wjets_flavour_heavy__down,
    :wjets_flavour_light__up => :wjets_flavour_light__up,
    :wjets_flavour_light__down => :wjets_flavour_light__down,

#    symbol("signal_comphep_anomWtb-unphys") => :comphep_anom_unphys,
#    symbol("signal_comphep_anomWtb-0100") => :comphep_anom_0100,
#    symbol("signal_comphep_nominal") => :comphep_nominal,
    symbol("signal_comphep__anomWtb-0100_t-channel") => :comphep_anom_0100,
    symbol("signal_comphep__anomWtb-Lv1Rt3_LVRT") => :comphep_anom_Lv1Rt3_LVRT,
    symbol("signal_comphep__anomWtb-Lv2Rt2_LVRT") => :comphep_anom_Lv2Rt2_LVRT,
    symbol("signal_comphep__anomWtb-Lv3Rt1_LVRT") => :comphep_anom_Lv3Rt1_LVRT,
    symbol("signal_comphep__anomWtb-Rt4_LVRT") => :comphep_anom_Rt4_LVRT,
    symbol("signal_comphep__anomWtb-unphys_LVLT") => :comphep_anom_unphys_LVLT,
    symbol("signal_comphep__anomWtb-unphys_t-channel") => :comphep_anom_unphys,
    symbol("signal_comphep__nominal") => :comphep_nominal,

    :qcd_antiiso__up => :qcd_antiiso__up,
    :qcd_antiiso__down => :qcd_antiiso__down,
    :lepton_weight__up => :lepton_weight__up,
    :lepton_weight__down => :lepton_weight__down,

}

const systematic_processings = collect(keys(SYSTEMATICS_TABLE))
const comphep_processings = filter(x->contains(string(x), "comphep"), systematic_processings)

const REV_SYSTEMATICS_TABLE = {v=>k for (k, v) in SYSTEMATICS_TABLE};

#loop over systematically variated datasets
#these use the nominal weight

immutable Scenario
    systematic::Symbol #a symbol signifying the systematic variation in processing
    sample::Symbol #the sample to variate
    weight::Function #the weight function pointer
    weight_scenario::Symbol
end

const scenarios = Dict{(Symbol, Symbol), Scenario}()

for syst in [

    #these exist for all samples
    "EnUp", "EnDown",
    "UnclusteredEnUp", "UnclusteredEnDown",
    "ResUp", "ResDown",

    #ttjets, w+jets
    "scaleup", "scaledown",

    #ttjets only
    "matchingup", "matchingdown",

    #ttbar, tchan
    "mass169_5", "mass175_5",

    "nominal"
    ]

    #only main samples are affected
    for samp in [:ttjets, :tchan, :wjets]
        # scenarios[(SYSTEMATICS_TABLE[syst|>symbol], samp)] = {
        #     :systematic=>symbol(syst), #processing option for sample
        #     :sample=>samp, #sample
        #     :weight=>(nw::Float64, row::DataFrameRow)->nw, #weight function, all systematics are nominal
        # }
        scenarios[(SYSTEMATICS_TABLE[symbol(syst)], samp)] = Scenario(
            #processing name
            symbol(syst),

            #sample name
            symbol(samp),

            #nominal weight function pointer
            (nw::Float64, row::DataFrameRow)->nw,

            #weight scenario name
            :nominal
        )
    end
end

#calculate the event weight, i = {pu, btag_bc, btag_l, lepton_id,iso,trigger, ...}
# w' -> total_nominal * w_i,variated / w_i,nominal
function syst_weight(nw::Float64, df::DataFrameRow, weight::Symbol, nomw::Symbol)

    #const nw = nominal_weight(df)::Float64

    const w1 = df[weight]::Union(Float32, NAtype)
    #in case variated weight was not set, use nominal weight
    (isna(w1)||isnan(w1)) && return nw

    const w2 = df[nomw]::Union(Float32, NAtype)
    (isna(w2)||isnan(w2)) && return nw

    const varw = nw * w1::Float32 / w2::Float32
    isnan(varw) && return nw
    return varw
end

#maps the variated weight to the nominal
const nominal_weights = {
    :pu_weight__up => :pu_weight,
    :pu_weight__down => :pu_weight,

    :lepton_weight__id__up => :lepton_weight__id,
    :lepton_weight__id__down => :lepton_weight__id,

    :lepton_weight__trigger__up => :lepton_weight__trigger,
    :lepton_weight__trigger__down => :lepton_weight__trigger,

    :lepton_weight__iso__up => :lepton_weight__iso,
    :lepton_weight__iso__down => :lepton_weight__iso,

    :b_weight__bc__up => B_WEIGHT_NOMINAL,
    :b_weight__bc__down => B_WEIGHT_NOMINAL,
    :b_weight__l__up => B_WEIGHT_NOMINAL,
    :b_weight__l__down => B_WEIGHT_NOMINAL,

    :top_weight__up => :top_weight,
    :top_weight__down => :top_weight,
}

#loop over the weight variations
#these use the nominal sample
const weight_scenarios = Dict{Symbol, Function}()
for weight in [
        :pu_weight__up, :pu_weight__down,
        :lepton_weight__id__up, :lepton_weight__id__down,
        :lepton_weight__iso__up, :lepton_weight__iso__down,
        :lepton_weight__trigger__up, :lepton_weight__trigger__down,
        :b_weight__bc__up, :b_weight__bc__down,
        :b_weight__l__up, :b_weight__l__down,
    ]

    nomw = nominal_weights[weight]

    weight_scenarios[SYSTEMATICS_TABLE[weight]] = (
        (nw::Float64, row::DataFrameRow) -> syst_weight(nw, row, weight, nomw)
    )

    for samp in [:ttjets, :tchan, :wjets]
        scenarios[(SYSTEMATICS_TABLE[weight], samp)] = Scenario(
            :nominal,
            samp,
            #systematic weight function pointer
            ((nw::Float64, row::DataFrameRow)-> syst_weight(nw, row, weight, nomw)),
            weight
        )
    end
end

###
### Add "lepton weight" from Andres
###
# #Check the effect of the lepton scale factor differing from unity (more correct would be mean weight)
#    muon_sel["shape"] = (
#        Weight("1.0 - 0.0*abs(1.0 - muon_IsoWeight*muon_TriggerWeight*muon_IDWeight)", "lepton_weight_shape_nominal"),
#        Weight("1.0 + abs(1.0 - muon_IsoWeight*muon_TriggerWeight*muon_IDWeight)", "lepton_weight_shape_up"),
#        Weight("1.0 - abs(1.0 - muon_IsoWeight*muon_TriggerWeight*muon_IDWeight)", "lepton_weight_shape_down")
#    )
#
# #Check the shape variation on top of the nominal weight
#    electron_sel["shape"] = (
#        Weight("1.0 - 0*abs(1.0 - electron_IDWeight*electron_TriggerWeight)", "lepton_weight_shape_nominal"),
#        Weight("1.0 + abs(1.0 - electron_IDWeight*electron_TriggerWeight)", "lepton_weight_shape_up"),
#        Weight("1.0 - abs(1.0 - electron_IDWeight*electron_TriggerWeight)", "lepton_weight_shape_down")
#    )

function lepton_weight_func_up(nw::Float64, row::DataFrameRow)
    const lt = row[:lepton_type]
    isna(lt) && return nw
    if lt == 13
        const x = nw * (1.0 + abs(1.0 - row[:lepton_weight__id] * row[:lepton_weight__iso] * row[:lepton_weight__trigger]));
        return isna(x)||isnan(x) ? nw : x;
    elseif lt == 11;
        const x = nw * (1.0 + abs(1.0 - row[:lepton_weight__iso] * row[:lepton_weight__trigger]));
        return isna(x)||isnan(x) ? nw : x
    else
        error("Unknown lepton type: ", row[:lepton_type])
    end
end

function lepton_weight_func_down(nw::Float64, row::DataFrameRow)
    const lt = row[:lepton_type]
    isna(lt) && return nw
    if lt == 13
        const x = nw * (1.0 - abs(1.0 - row[:lepton_weight__id] * row[:lepton_weight__iso] * row[:lepton_weight__trigger]));
        return isna(x)||isnan(x) ? nw : x;
    elseif lt == 11;
        const x = nw * (1.0 - abs(1.0 - row[:lepton_weight__iso] * row[:lepton_weight__trigger]));
        return isna(x)||isnan(x) ? nw : x
    else
        error("Unknown lepton type: ", row[:lepton_type])
    end
end

for samp in [:ttjets, :tchan, :wjets]
    scenarios[(:lepton_weight__up, samp)] = Scenario(
        :nominal,
        samp,
        lepton_weight_func_up,
        :lepton_weight__up
    )
    scenarios[(:lepton_weight__down, samp)] = Scenario(
        :nominal,
        samp,
        lepton_weight_func_down,
        :lepton_weight__down
    )
end

for weight in [:top_weight__up, :top_weight__down]
    nomw = nominal_weights[weight]

    scenarios[(SYSTEMATICS_TABLE[weight], :ttjets)] = Scenario(
        :nominal,
        :ttjets,
        (nw::Float64, row::DataFrameRow) -> syst_weight(nw, row, weight, nomw),
        weight
    )
end

for proc in vcat(mcsamples)
    scenarios[(:nominal, proc)] = Scenario(
        :nominal,
        proc,
        (nw::Float64, row::DataFrameRow) -> nw,
        :nominal
    )

    scenarios[(:unweighted, proc)] = Scenario(
        :nominal,
        proc,
        (nw::Float64, row::DataFrameRow) -> 1.0,
        :unweighted
    )
end

for proc in [:data_mu, :data_ele]

    scenarios[(:unweighted, proc)] = Scenario(
        symbol(""),
        proc,
        (nw::Float64, row::DataFrameRow) -> 1.0,
        :unweighted
    )

end

scenarios[(:wjets_shape__unweighted, :wjets)] = Scenario(
    :nominal,
    :wjets,
    (nw::Float64, row::DataFrameRow) -> nw / row[:wjets_ct_shape_weight],
    :wjets_shape__unweighted
)

scenarios[(:nominal, :wjets_sherpa)] = Scenario(
    :nominal,
    :wjets_sherpa,
    (nw::Float64, row::DataFrameRow) -> nw,
    :nominal
)

scenarios[(:wjets_shape__up, :wjets)] = Scenario(
    :nominal,
    :wjets,
    (nw::Float64, row::DataFrameRow) -> nw / row[:wjets_ct_shape_weight] * row[:wjets_ct_shape_weight__up],
    :wjets_shape__up
)

scenarios[(:wjets_shape__down, :wjets)] = Scenario(
    :nominal,
    :wjets,
    (nw::Float64, row::DataFrameRow) -> nw / row[:wjets_ct_shape_weight] * row[:wjets_ct_shape_weight__down],
    :wjets_shape__down
)

#remove unnecessary scenarios
pop!(scenarios, (:mass__up, :wjets))
pop!(scenarios, (:mass__down, :wjets))
pop!(scenarios, (:matching__up, :tchan))
pop!(scenarios, (:matching__down, :tchan))

# scenarios[(:unweighted, :tchan)] = {
#     :weight=>(nw::Float64, row::DataFrameRow)->1.0, :systematic=>:nominal, :sample=>:tchan
# }

scenarios[(:unweighted, :tchan)] =
    Scenario(:nominal, :tchan, (nw::Float64, row::DataFrameRow)->1.0, :unweighted)

#t-channel asymmetry re-weighting
scenarios[(:asym_028, :tchan)] =
    Scenario(:nominal, :tchan,
    (nw::Float64, row::DataFrameRow)-> nw * (0.28 * row[:cos_theta_lj_gen] + 0.5) / (0.44 * row[:cos_theta_lj_gen] + 0.5),
    :asym_028
)
scenarios[(:asym_008, :tchan)] =
    Scenario(:nominal, :tchan,
    (nw::Float64, row::DataFrameRow)-> nw * (0.08 * row[:cos_theta_lj_gen] + 0.5) / (0.44 * row[:cos_theta_lj_gen] + 0.5),
    :asym_008
)
scenarios[(:asym_000, :tchan)] =
    Scenario(:nominal, :tchan,
    (nw::Float64, row::DataFrameRow)-> nw * (0.00 * row[:cos_theta_lj_gen] + 0.5) / (0.44 * row[:cos_theta_lj_gen] + 0.5),
    :asym_000
)

for k in SingleTopBase.comphep_processings
    scenarios[(SYSTEMATICS_TABLE[k], :tchan)] = Scenario(k, :tchan, (nw::Float64, row::DataFrameRow)->nw, :nominal)
end

#scenarios relevant for signal
const scenarios_signal = collect(
    filter(
        ((_,x) -> x.sample == :tchan),
        scenarios
    )
)

#scenarios by processing group
const scens_gr = {
    g=>collect(
        filter(
            (x -> x[2].systematic == g),
            scenarios_signal
        )
    ) for g in systematic_processings
}


using JSON
function systematics_to_json(fname::ASCIIString)
    of = open(fname, "w")
    js = json({
        "systematics_table" => {
        string(k) => string(v) for (k,v) in SYSTEMATICS_TABLE
    },
    }, 4)
    write(of, js)
    close(of)
end

export SYSTEMATICS_TABLE, REV_SYSTEMATICS_TABLE, systematic_processings
export weight_scenarios, scenarios, scens_gr, Scenario
