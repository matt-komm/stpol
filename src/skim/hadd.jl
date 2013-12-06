#!/home/joosep/.julia/ROOT/julia
include("$(homedir())/.juliarc.jl")
using DataFrames
using HDF5, JLD, ROOT
using JSON

include("../analysis/util.jl")
include("../skim/xs.jl")
include("../skim/jet_cls.jl")

fname = ARGS[1]
sumfname = ARGS[2]
ofile = ARGS[3]

flist = split(readall(fname))
@assert length(flist)>0 "no files specified"

println("Running over $(length(flist)) files")

cols = [:jet_cls, :hlt_mu, :hlt_ele, :event, :run, :lumi, :n_veto_mu, :n_veto_ele, :n_signal_mu, :n_signal_ele, :met, :ljet_rms, :pu_weight, :C, :bjet_phi, :ljet_phi, :njets, :ntags, :ljet_dr, :bjet_dr, :shat, :ht, :cos_theta_lj, :cos_theta_bl, :top_mass, :ljet_eta, :mtw, :lepton_id, :lepton_type, :fileindex, :n_good_vertices]
#outcols = [:hlt_mu, :hlt_ele, :event, :run, :lumi, :n_veto_mu, :n_veto_ele, :n_signal_mu, :n_signal_ele, :met, :ljet_rms, :pu_weight, :C, :bjet_phi, :ljet_phi, :njets, :ntags, :ljet_dr, :bjet_dr, :mtw, :shat, :ht, :top_mass, :ljet_eta, :cos_theta_lj, :cos_theta_bl, :lepton_type, :xsweight, :sample, :isolation, :jet_cls, :n_good_vertices]
outcols = vcat(cols, [:sample, :isolation, :xsweight])
tot_res = JSON.parse(readall(sumfname))
println(tot_res)
dfs = Any[]
for fi in flist
    println(fi)
    acc = accompanying(fi)
    md = readtable(acc["processed"], allowcomments=true)
    nrow(md) > 0 || error("metadata was empty")
    
    sample_types = [sample_type(x) for x in md[:, :files]]

    edf = TreeDataFrame(acc["df"])
    subdf = edf[:, cols]
    
    xsweights = DataArray(Float32, nrow(subdf))
    processes = DataArray(ASCIIString, nrow(subdf))
    isos = DataArray(ASCIIString, nrow(subdf))

    for i=1:nrow(subdf)

        sample = string(sample_types[subdf[i, :fileindex]][:sample])
        
        if sample in keys(cross_sections)
            @assert (typeof(cross_sections[sample]) <: Number && cross_sections[sample] > 0.0) "illegal cross section"
            @assert (typeof(tot_res["$(sample)/counters/generated"]) <: Number && tot_res["$(sample)/counters/generated"] > 0) "illegal ngen"
        
            xsweights[i] = sample in keys(cross_sections) ? 1.0 * cross_sections[sample] / tot_res["$(sample)/counters/generated"] : NA
        end

        proc = get_process(sample)
        processes[i] = proc != :unknown ? string(proc) : string(sample)
        
        iso = string(sample_types[subdf[i, :fileindex]][:iso])
        isos[i] = string(iso)
    end
    subdf["xsweight"] = xsweights
    subdf["sample"] = processes
    subdf["isolation"] = isos
    
    local_outcols = deepcopy(outcols)
    for k in keys(acc)
        m = match(r"mva_(.*)", string(k))
        m == nothing && continue
        mvaname = m.captures[1]
        println("adding mva from $k:$(acc[k]):$(mvaname)")
        mvatable = readtable(acc[k], allowcomments=true)[1]
        @assert length(mvatable)==nrow(subdf) "number of rows in mva table $k is wrong"
        subdf[string(mvaname)] = mvatable
        push!(local_outcols, symbol(mvaname)) 
    end
    df = subdf
    
    df = df[:, local_outcols]
    println(colnames(df)) 
    push!(dfs, df)
end

@assert length(dfs)>0 "no DataFrames were produced"

df = rbind(dfs)
#describe(df)

#write output as JLD
println("writing $(nrow(df)) events to $ofile as JLD")
fi = jldopen(string(ofile, ".jld"), "w")
tic(); write(fi, "df", df); toc()
close(fi)

##write output as CSV
#tic();writetable(string(ofile, ".csv"), df, separator=',');toc()

##write output as ROOT
#tic();writetree(string(ofile, ".root"), df);toc()
