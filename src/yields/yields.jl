using ROOT, ROOTDataFrames, DataFrames
include("../analysis/df_extensions.jl");
include("../analysis/base.jl");
include("../fraction_fit/hists.jl");
using SingleTopBase
import SingleTopBase: FitResult, VARS

const SAMPLE = symbol(ARGS[1])
njets = 2;
ntags = 1;

files = ARGS[2:]

chd1 = TreeDataFrame(files);
chd2 = TreeDataFrame(map(postfix_added, files));
chd = MultiColumnDataFrame(AbstractDataFrame[chd1, chd2]);

X = chd1[[:hlt_mu, :hlt_ele, :n_signal_mu, :n_veto_mu, :n_signal_ele, :n_veto_ele, :njets, :ntags, :met, :mtw, :ljet_rms, :ljet_dr, :bjet_dr]];
Y = chd2[[:bdt_sig_bg, :bdt_sig_bg_top_13_001, :bdt_qcd, :xsweight]];
X = hcat(X,Y);

mu = (X[:hlt_mu].==1) .* (X[:n_signal_mu].==1) .* (X[:n_signal_ele].==0) .* (X[:n_veto_mu].==0) .* (X[:n_veto_ele].==0);
nona!(mu);

ele = (X[:hlt_ele].==1) .* (X[:n_signal_ele].==1) .* (X[:n_signal_mu].==0) .* (X[:n_veto_mu].==0) .* (X[:n_veto_ele].==0);
nona!(ele);

totw = chd1[[:lepton_weight__id, :lepton_weight__trigger, :lepton_weight__iso, :b_weight, :b_weight_old, :top_weight, :pu_weight]];

totw[isnan(totw[:b_weight]), :b_weight] = 0.0;
totw[isnan(totw[:b_weight_old]), :b_weight_old] = 0.0;
totw[isna(totw[:b_weight]), :b_weight] = 0.0;
totw[isna(totw[:b_weight_old]), :b_weight_old] = 0.0;

totw[:top_weight][isna(totw[:top_weight])] = 1.0;

totw[:lepton_weight__trigger][isnan(totw[:lepton_weight__trigger])] = 0.0;
totw[:lepton_weight__id][isnan(totw[:lepton_weight__id])] = 0.0;
totw[:lepton_weight__iso][isnan(totw[:lepton_weight__iso])] = 0.0;

totw[:w_new] = totw[:lepton_weight__id] .* totw[:lepton_weight__iso] .* totw[:lepton_weight__trigger] .* totw[:pu_weight] .* totw[:top_weight];
totw[:w_new][isna(totw[:w_new])] = 0.0;
totw[:w_old] = totw[:w_new] .* totw[:b_weight_old];
totw[:w_new] = totw[:w_new] .* totw[:b_weight];

sum(totw[:w_new]), sum(totw[:w_old])

jet = X[:njets].==njets
nona!(jet)

tag = X[:ntags].==ntags
nona!(tag)

rms = X[:ljet_rms] .< 0.025
nona!(rms)

dr = (X[:ljet_dr] .> 0.3) .* (X[:bjet_dr] .> 0.3);
nona!(dr)

met = X[:met].>45
nona!(met)
mtw = X[:mtw].>50
nona!(met)

qcd04 = X[:bdt_qcd].>0.4
nona!(qcd04)
qcd055 = X[:bdt_qcd].>0.55
nona!(qcd055)

bdt = X[:bdt_sig_bg].>0.6
nona!(bdt)

bdtold_mu = X[:bdt_sig_bg_top_13_001].>0.06
nona!(bdtold_mu)

bdtold_ele = X[:bdt_sig_bg_top_13_001].>0.13
nona!(bdtold_ele)

cuts = {
    :mu=>{
        :old => {dr, mu, mtw, jet, rms, tag, bdtold_mu},
        :new => {dr, mu, qcd04, jet, jet, tag, bdt},
    },
    :ele=>{
        :old => {dr, ele, met, jet, rms, tag, bdtold_ele},
        :new => {dr, ele, qcd055, jet, jet, tag, bdt},
    }
};

function cutflow(A, weighted, weight)
    sel = first(A)
    v = Any[]
    w = Any[]
    for a in A
        sel = sel .* a
        nona!(sel)
        push!(v, sum(sel))
        push!(w, sum(
            X[sel, :xsweight] .*
            totw[sel, weight]
        ))
    end
    return {v,w}
end

function cutflow_data(A)
    sel = first(A)
    v = Int64[]
    for a in A
        sel = sel .* a
        sel[isna(sel)] = false
        #println(sel)
        #println(sum(sel), " ", length(sel))
        #sum(sel)
        push!(v, sum(sel))
    end
    return {v, v}
end


if SAMPLE==:data_mu || SAMPLE==:data_ele
    d = {
        :mu=>{:old=>cutflow_data(cuts[:mu][:old]), :new=>cutflow_data(cuts[:mu][:new])},
        :ele=>{:old=>cutflow_data(cuts[:ele][:old]), :new=>cutflow_data(cuts[:ele][:new])}
    }
else
    d = {
        :mu=>{:old=>cutflow(cuts[:mu][:old], true, :w_old), :new=>cutflow(cuts[:mu][:new], true, :w_new)},
        :ele=>{:old=>cutflow(cuts[:ele][:old], true, :w_old), :new=>cutflow(cuts[:ele][:new], true, :w_new)}
    }
end

oldref = {
    :mu=>{
        :data_mu=>Int[2653069, 1651737, 1326824, 1088802, 61241, 4303],
        :tchan=>Int[43531, 30506, 24521, 21436, 8060, 2371],
        :wjets=>Int[1964609, 1341407, 1148255, 966843, 13198, 601],
        :ttjets=>Int[277067, 188469, 87863, 72213, 26776, 545]
    },
    :ele=>{
        :data_ele=>Int[2562836, 919441, 709906, 597362, 34652, 2031],
        :tchan=>Int[33282, 17371, 13550, 11830, 4369, 1171],
        :wjets=>Int[1595244, 711925, 591467, 497259, 7293, 239],
        :ttjets=>Int[227208, 137988, 64476, 52810, 19244, 314]

    }
}

df = similar(
    DataFrame(
        cut=Symbol[], flavour=Symbol[], sample=Symbol[],
        total=Int64[],
        dr=Int64[], lepton=Int64[],
        qcd=Int64[], jet=Int64[],
        rms=Int64[], tag=Int64[], bdt=Int64[],
        bdt_w=Int64[],
fit=Int64[],
    ), 4
);

j = 0
for lep in [:mu, :ele]
    for cut in [:old, :new]
        j += 1
        df[j, :cut] = cut
        df[j, :flavour] = lep
        df[j, :sample] = SAMPLE
        df[j, :total] = nrow(X)
        println(lep, " ", cut)
        if SAMPLE in [:data_mu, :data_ele]
            l = 1.0
        else
            l = Reweight.lumis[lep]
        end
        for i=1:7
            println(i, " ", d[lep][cut][1])
            df[j, i+4] = int(round(float(d[lep][cut][1][i])))
        end
        df[j, :bdt_w] = int(round(l * float(d[lep][cut][2][7])))
        if SAMPLE == :tchan
            sf = FITRESULTS[lep][:beta_signal]
        elseif SAMPLE in [:wjets, :gjets, :dyjets, :diboson]
            sf = FITRESULTS[lep][:wzjets]
        elseif SAMPLE in [:schan, :twchan, :ttjets]
            sf = FITRESULTS[lep][:ttjets]
        else
            sf = 1.0
        end
        df[j, :fit] = round(df[j, :bdt_w] * sf)|>int
    end
end

writetable("../../results/yields/$(SAMPLE)_$(njets)j_$(ntags)t.csv", df)
