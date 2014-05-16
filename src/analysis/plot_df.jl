@everywhere ENV["PYTHONPATH"]=join("../qcd_estimation")

@everywhere begin
    using DataFrames, DataArrays, HDF5, JLD;
    include("base.jl");
    include("$BASE/src/analysis/selection.jl");
    include("$BASE/src/fraction_fit/hists.jl");
    include("$BASE/src/analysis/hplot.jl");
    include("$BASE/src/analysis/fit.jl");
    include("$BASE/src/analysis/pyplot.jl");
end

dffi = jldopen("/scratch/joosep/feb5.jld", "r";mmaparrays=true)
df = read(dffi, "df")

indfi = jldopen("/home/joosep/singletop/temp/large_index.jld", "r";mmaparrays=true)
inds = read(indfi, "index")

df["qcd_weight"] = 1.0
df["lumi"] = 1.0
df[!inds[:data] & inds[:mu], :lumi] = lumis[:mu]
df[!inds[:data] & inds[:ele], :lumi] = lumis[:ele]

reweight_qcd(df, inds)

nomw(r::DataFrameRow) = nominal_weight(r) * r[:lumi]
qcdw(r::DataFrameRow) = r[:qcd_weight] * nomw(r)

nomdf = sub(df, inds[:systematic][:nominal]|inds[:systematic][:unknown])
nominds = perform_selection(nomdf)

sel(nj, nt, lep) = nominds[:njets][nj] & nominds[:ntags][nt] & nominds[:dr] & nominds[lep] & nominds[:hlt][lep]
const lowpt = (nomdf[:bjet_pt].<50) & (nomdf[:ljet_pt].<50)
const highmva = (nomdf[:bjet_pumva] .< -0.89) & (nomdf[:ljet_pumva] .< -0.89)

sels = {
    :all => (nj, nt, lep)->sel(nj, nt, lep),
    #:lowpt => (nj, nt, lep)->sel(nj, nt, lep) & lowpt,
    #:highpt => (nj, nt, lep)->sel(nj, nt, lep) & !lowpt,
    :pumva => (nj, nt, lep)->sel(nj, nt, lep) & highmva,
    :nopumva => (nj, nt, lep)->sel(nj, nt, lep) & !highmva,
}

dsel(lep) = nominds[:sample][symbol("data_$lep")]

plotconfs = {
    "ljet_eta" => {:var=>:ljet_eta, :bin=>vcat(-Inf, linspace(-5, 5, 60), Inf)},
    "ljet_pumva" => {:var=>:ljet_pumva, :bin=>vcat(-Inf, linspace(-1, 1, 60), Inf), :logy=>true},
#    "bjet_eta" => {:var=>:bjet_eta, :bin=>vcat(-Inf, linspace(-3, 3, 60), Inf)},
#    "ljet_pt" => {:var=>:ljet_pt, :bin=>vcat(-Inf, linspace(0, 200, 60), Inf)},
#    "bjet_pt" => {:var=>:bjet_pt, :bin=>vcat(-Inf, linspace(0, 200, 60), Inf)},
#    "shat" => {:var=>:shat, :bin=>vcat(-Inf, linspace(150, 800, 60), Inf)},
#    "ht" => {:var=>:ht, :bin=>vcat(-Inf, linspace(0, 500, 60), Inf)},
}

plot_dir = "output/plots"
for lep in [:mu, :ele]
    for (nj, nt) in [(2,0), (2,1), (3,1), (3,2)]
        for (name, pc) in plotconfs
            for (selname, selection) in sels
                println("plotting $lep $nj $nt $name $selname")
                hists = makehists(
                    nomdf,
                    nominds, selection(nj, nt, :mu), dsel(:mu),
                    pc[:var],
                    pc[:bin], 
                    nomw, qcdw
                )
                apply_fit_coefs = ((nj,nt)==(2,1) || (nj, nt)==(3,2))
                apply_fit_coefs && reweight_hists_to_fitres(FITRESULTS[lep], hists)
                
                fig, (ax1, ax2) = ratio_axes()

                draw_data_mc_stackplot(ax1, hists; log=get(pc, :logy, false))
                ax1[:set_ylim](bottom=1)
                ax1[:grid]()
                
                errorbars(ax2, hists)
                ax2[:grid](true, which="both")
                ax2[:set_ylim](bottom=-0.5, top=0.5)

                varname = get(VARS, pc[:var], pc[:var])|>string
                ax2[:set_xlabel](varname, size="x-large")

                svfg("$plot_dir/$(lep)__$(name)__$(nj)j$(nt)t_fit_$(apply_fit_coefs)_$(selname)")
                title("$lep $(nj)j$(nt)t $(pc[:var]) $(selname)")

                PyPlot.close()
            end
        end 
    end
end
