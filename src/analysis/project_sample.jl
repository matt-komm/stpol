require("base.jl")
using ROOT, ROOTDataFrames

infile = ARGS[2:end]

println("opening files: ", length(infile))
const df_base = TreeDataFrame(infile)
const df_added = TreeDataFrame(map(x->"$x.added", infile))

println("getting N of events")
const N = nrow(df_base)
#nrow(df_base) == nrow(df_added) || error("unequal datasets: $(nrow(df_base))!=$(nrow(df_added))")
#println(nrow(df_base))

enable_branches(df_base, [
    "hlt*", "event*", "run*", "lumi*",
    "met*", "mtw*", "cos_theta_lj*", "n_signal*",
    "n_veto*", "njets*", "ntags*", "ljet_dr*", "bjet_dr*", "ljet_rms*",
    "ljet_eta*", "bjet_eta*"
])
enable_branches(df_added, ["bdt*"])

println("making df")
out_df = similar(DataFrame(
    hlt_mu=Bool[], hlt_ele=Bool[],
    event=Int32[], run=Int32[], lumi=Int32[],
    met=Float32[], mtw=Float32[], cos_theta_lj=Float32[],
    n_veto_mu=Int32[], n_veto_ele=Int32[], n_signal_mu=Int32[], n_signal_ele=Int32[],
    njets=Int32[], ntags=Int32[],
    ljet_dr=Float32[], bjet_dr=Float32[],
    ljet_eta=Float32[], bjet_eta=Float32[],
    bdt_sig_bg=Float32[], bdt_sig_bg_top_13_001=Float32[], bdt_qcd=Float32[],
    passes_mu_new=Int32[],
    passes_ele_new=Int32[],
    passes_mu_old=Int32[],
    passes_ele_old=Int32[],
    ), N 
)

println("looping")
for i=1:nrow(df_base)
    i%50000 == 0 && println(i)
    load_row(df_base, i)
    load_row(df_added, i)
    for x in [
        :hlt_mu, :hlt_ele, :event, :run, :lumi,
        :met, :mtw,
        :cos_theta_lj,
        :n_signal_mu, :n_veto_mu, :n_signal_ele, :n_veto_ele,
        :njets, :ntags,
        :ljet_dr, :bjet_dr,
        :ljet_eta, :bjet_eta
        ]
        out_df[i, x] = df_base[i, x]
    end
    for x in [:bdt_sig_bg, :bdt_sig_bg_top_13_001, :bdt_qcd]
        out_df[i, x] = df_added[i, x]
    end
    
    out_df[i, :passes_mu_new] = (
        (out_df[i, :hlt_mu] .== 1) .*
        (out_df[i, :n_signal_mu] .== 1) .* (out_df[i, :n_signal_ele] .== 0) .*
        (out_df[i, :n_veto_mu] .== 0) .* (out_df[i, :n_veto_ele] .== 0) .*
        (out_df[i, :njets] .== 2) .* (out_df[i, :ntags] .== 1) .*
        (out_df[i, :bdt_qcd] .> 0.4) .*
        (abs(out_df[i, :ljet_eta]) .< 4.5 ) .*
        (abs(out_df[i, :bjet_eta]) .< 4.5 ) .*
#        (out_df[i, :ljet_dr].>0.3) .*
#        (out_df[i, :bjet_dr].>0.3) .*
        (out_df[i, :bdt_sig_bg] .> 0.6)
    )
    
    out_df[i, :passes_ele_new] = (
        (out_df[i, :hlt_ele] .== 1) .*
        (out_df[i, :n_signal_mu] .== 0) .* (out_df[i, :n_signal_ele] .== 1) .*
        (out_df[i, :n_veto_mu] .== 0) .* (out_df[i, :n_veto_ele] .== 0) .*
        (out_df[i, :njets] .== 2) .* (out_df[i, :ntags] .== 1) .*
        (out_df[i, :bdt_qcd] .> 0.55) .*
        (abs(out_df[i, :ljet_eta]) .< 4.5 ) .*
        (abs(out_df[i, :bjet_eta]) .< 4.5 ) .*
#        (out_df[i, :ljet_dr].>0.3) .*
#        (out_df[i, :bjet_dr].>0.3) .*
        (out_df[i, :bdt_sig_bg] .> 0.6)
    )
    
    out_df[i, :passes_mu_old] = (
        (out_df[i, :hlt_mu] .== 1) .*
        (out_df[i, :n_signal_mu] .== 1) .* (out_df[i, :n_signal_ele] .== 0) .*
        (out_df[i, :n_veto_mu] .== 0) .* (out_df[i, :n_veto_ele] .== 0) .*
        (out_df[i, :njets] .== 2) .* (out_df[i, :ntags] .== 1) .*
        (out_df[i, :mtw] .> 55) .*
        (abs(out_df[i, :ljet_eta]) .< 4.5 ) .*
        (abs(out_df[i, :bjet_eta]) .< 4.5 ) .*
#        (out_df[i, :ljet_dr].>0.3) .*
#        (out_df[i, :bjet_dr].>0.3) .*
        (df_base[i, :ljet_rms] .<0.025 ) .*
        (out_df[i, :bdt_sig_bg_top_13_001] .> 0.06)
    )
    
    out_df[i, :passes_ele_old] = (
        (out_df[i, :hlt_ele] .== 1) .*
        (out_df[i, :n_signal_mu] .== 0) .* (out_df[i, :n_signal_ele] .== 1) .*
        (out_df[i, :n_veto_mu] .== 0) .* (out_df[i, :n_veto_ele] .== 0) .*
        (out_df[i, :njets] .== 2) .* (out_df[i, :ntags] .== 1) .*
        (out_df[i, :met] .> 40) .*
        (abs(out_df[i, :ljet_eta]) .< 4.5 ) .*
        (abs(out_df[i, :bjet_eta]) .< 4.5 ) .*
#        (out_df[i, :ljet_dr].>0.3) .*
#        (out_df[i, :bjet_dr].>0.3) .*
        (df_base[i, :ljet_rms] .< 0.025) .*
        (out_df[i, :bdt_sig_bg_top_13_001] .> 0.13)
    )
end

writetable(ARGS[1], out_df)

for x in [:passes_mu_old, :passes_mu_new, :passes_ele_old, :passes_ele_new]
    z = out_df[x].==1
    z[isna(z)] = false
    println("$x $(sum(z))")
end
