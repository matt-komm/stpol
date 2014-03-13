#if !isdefined(:SYSTEMATICS)

const SYSTEMATICS_TABLE = {
    :mass175_5=>:mass__up,
    :mass169_5=>:mass__down,
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

    :wjets_shape_unweighted => :wjets_shape_unweighted,
    :wjets_shape_up => :wjets_shape__up,
    :wjets_shape_down => :wjets_shape__down,

    symbol("signal_comphep_anomWtb-unphys") => :comphep_anom_unphys,
    symbol("signal_comphep_anomWtb-0100") => :comphep_anom_0100,
    symbol("signal_comphep_nominal") => :comphep_nominal,
}


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

    :b_weight__bc__up => :b_weight,
    :b_weight__bc__down => :b_weight,
    :b_weight__l__up => :b_weight,
    :b_weight__l__down => :b_weight,
    
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

for weight in [:top_weight__up, :top_weight__down]
    nomw = nominal_weights[weight]

    scenarios[(SYSTEMATICS_TABLE[weight], :ttjets)] = Scenario(
        :nominal,
        :ttjets,
        (nw::Float64, row::DataFrameRow) -> syst_weight(nw, row, weight, nomw),
        weight
    ) 
end

for proc in vcat(mcsamples, :data_mu, :data_ele)
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
        :unknown,
        proc, 
        (nw::Float64, row::DataFrameRow) -> 1.0,
        :unweighted 
    )

end

scenarios[(:wjets_shape_unweighted, :wjets)] = Scenario(
    :nominal,
    :wjets, 
    (nw::Float64, row::DataFrameRow) -> nw / row[:wjets_ct_shape_weight],
    :wjets_shape__unweighted 
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

for k in SingleTopBase.comphep_processings
    scenarios[(k, :tchan)] = Scenario(k, :tchan, (nw::Float64, row::DataFrameRow)->1.0, :unweighted) 
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
    })
    write(of, js)
    close(of)
end

export weight_scenarios, scenarios, scens_gr, Scenario


