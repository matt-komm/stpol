using ROOT, ROOTDataFrames, DataFrames
include("../analysis/df_extensions.jl");
include("../analysis/base.jl");
include("../fraction_fit/hists.jl");
using SingleTopBase
import SingleTopBase: FitResult, VARS

const SAMPLE = symbol(ARGS[1])
njets = 2;
ntags = 1;

files = ARGS[2:end]
println("opening $files")
chd1 = TreeDataFrame(files);
chd2 = TreeDataFrame(map(postfix_added, files));
chd = MultiColumnDataFrame(AbstractDataFrame[chd1, chd2]);
println("opened $(nrow(chd)) events")

X = chd1[[:hlt_mu, :hlt_ele, :n_signal_mu, :n_veto_mu, :n_signal_ele, :n_veto_ele, :njets, :ntags, :met, :mtw, :ljet_rms, :ljet_dr, :bjet_dr, :ljet_eta, :bjet_eta, :cos_theta_lj]];
Y = chd2[[:bdt_sig_bg, :bdt_sig_bg_top_13_001, :bdt_qcd, :xsweight]];
X = hcat(X,Y);

mu = (X[:hlt_mu].==1) .* (X[:n_signal_mu].==1) .* (X[:n_signal_ele].==0) .* (X[:n_veto_mu].==0) .* (X[:n_veto_ele].==0);
nona!(mu);

ele = (X[:hlt_ele].==1) .* (X[:n_signal_ele].==1) .* (X[:n_signal_mu].==0) .* (X[:n_veto_mu].==0) .* (X[:n_veto_ele].==0);
nona!(ele);

totw = chd1[[:lepton_weight__id, :lepton_weight__trigger, :lepton_weight__iso, :b_weight, :b_weight_old, :top_weight, :pu_weight]];
totw[:wjets_ct_shape_weight] = chd2[:wjets_ct_shape_weight]

for x in [
    :lepton_weight__trigger, :lepton_weight__iso, :lepton_weight__id, :b_weight, :top_weight, :pu_weight, :wjets_ct_shape_weight
    ]
    totw[x][isna(totw[x])] = 1.0
    totw[x][isnan(totw[x])] = 1.0
end

totw[:w_new] = totw[:lepton_weight__id] .* totw[:lepton_weight__iso] .* totw[:lepton_weight__trigger] .* totw[:pu_weight] .* totw[:top_weight] .* totw[:b_weight] .* totw[:wjets_ct_shape_weight];

jet = X[:njets].==njets
nona!(jet)

tag = X[:ntags].==ntags
nona!(tag)
#
# rms = X[:ljet_rms] .< 0.025
# nona!(rms)
#
# dr = (X[:ljet_dr] .> 0.3) .* (X[:bjet_dr] .> 0.3);
# nona!(dr)
#
# met = X[:met].>45
# nona!(met)
# mtw = X[:mtw].>50
# nona!(met)

qcd04 = X[:bdt_qcd].>0.4
nona!(qcd04)
qcd055 = X[:bdt_qcd].>0.55
nona!(qcd055)

bdt = X[:bdt_sig_bg].>0.6
nona!(bdt)
#
jet_eta = (abs(X[:ljet_eta]) .< 4.5) .* (abs(X[:bjet_eta]) .< 4.5)
nona!(jet_eta)
#
# bdtold_mu = X[:bdt_sig_bg_top_13_001].>0.06
# nona!(bdtold_mu)
#
# bdtold_ele = X[:bdt_sig_bg_top_13_001].>0.13
# nona!(bdtold_ele)

cuts = {
    :mu=>{
#        :old => {dr, mu, mtw, jet, rms, tag, jet_eta, bdtold_mu},
        :new => {mu, qcd04, jet, tag, jet_eta, bdt},
    },
    :ele=>{
#        :old => {dr, ele, met, jet, rms, tag, jet_eta, bdtold_ele},
        :new => {ele, qcd055, jet, tag, jet_eta, bdt},
    }
};

x = X[ mu .* qcd04 .* jet .* tag .* jet_eta .* bdt, :cos_theta_lj]
println("selected ", length(x), " cos_theta calculated for ", sum(!isna(x)))

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
        push!(v, sum(sel))
    end
    return {v, v}
end


if SAMPLE==:data_mu || SAMPLE==:data_ele
    d = {
        :mu=>{:new=>cutflow_data(cuts[:mu][:new])},
        :ele=>{:new=>cutflow_data(cuts[:ele][:new])}
    }
else
    d = {
        :mu=>{:new=>cutflow(cuts[:mu][:new], true, :w_new)},
        :ele=>{:new=>cutflow(cuts[:ele][:new], true, :w_new)}
    }
end
println(d)

df = similar(
    DataFrame(
        flavour=Symbol[],
        sample=Symbol[],
        lepton=Int64[],
        qcd=Int64[],
        jet=Int64[],
        tag=Int64[],
        jet_eta=Int64[],
        bdt=Int64[],
        bdt_w=Int64[],
        fit=Int64[],
    ), 2
);

j = 0
for lep in [:mu, :ele]
    for cut in [:new]
        j += 1
        df[j, :flavour] = lep
        df[j, :sample] = SAMPLE
        #println(lep, " ", cut)
        if SAMPLE in [:data_mu, :data_ele]
            l = 1.0
        else
            l = Reweight.lumis[lep]
        end
        for i=1:6
            println(i, " ", d[lep][cut][1])
            df[j, i + 2] = int(round(float(d[lep][cut][1][i])))
        end
        df[j, :bdt_w] = int(round(l * float(d[lep][cut][2][6])))

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
println(df)
