#!/home/joosep/.julia/ROOT/julia
include("../analysis/base.jl")

using JSON

include("../analysis/util.jl")
include("../skim/xs.jl")
include("../skim/jet_cls.jl")

fname = ARGS[1]
sumfname = ARGS[2]

include("$(homedir())/.juliarc.jl")
using DataFrames
using HDF5, JLD, ROOT
ofile = ARGS[3]

flist = split(readall(fname))
@assert length(flist)>0 "no files specified"

println("Running over $(length(flist)) files")

tic()
cols = [:bjet_pt, :ljet_pt, :bjet_eta, :hlt_mu, :hlt_ele, :event, :run, :lumi, :n_veto_mu, :n_veto_ele, :n_signal_mu, :n_signal_ele, :met, :ljet_rms, :pu_weight, :gen_weight, :top_weight, :C, :bjet_phi, :ljet_phi, :njets, :ntags, :ljet_dr, :bjet_dr, :shat, :ht, :cos_theta_lj, :cos_theta_bl, :top_mass, :ljet_eta, :mtw, :lepton_id, :lepton_type, :fileindex, :n_good_vertices, :lepton_pt, :jet_cls]

outcols = vcat(cols, [:subsample, :xs, :ngen, :sample, :isolation, :systematic, :xsweight])

tot_res = JSON.parse(readall(sumfname))
if DEBUG
    println(tot_res)
end
dfs = Any[]

nf=0

println("looping over files")
for fi in flist
    nf += 1

    acc = accompanying(fi)
    md = readtable(acc["processed"], allowcomments=true)
    if DEBUG
        println(fi, " ", acc["processed"])
    end
    nrow(md) > 0 || error("metadata was empty")
    
    sample_types = [sample_type(x) for x in md[:, :files]]
    if DEBUG
        println("[", join(sample_types, ",\n"), "]")
    end

    println("opening dataframe ", acc["df"], " in ROOT mode")
    edf = TreeDataFrame(acc["df"])
    #println("$fi $acc")
    println("reading ", nrow(edf), " rows, ", length(cols), " columns to memory")
    subdf = edf[1:nrow(edf), cols]
    
    xsweights = DataArray(Float32, nrow(subdf))
    ngens = DataArray(Int32, nrow(subdf))
    xss = DataArray(Float32, nrow(subdf))
    processes = DataArray(ASCIIString, nrow(subdf))
    samples = DataArray(ASCIIString, nrow(subdf))
    systematics = DataArray(ASCIIString, nrow(subdf))
    isos = DataArray(ASCIIString, nrow(subdf))
    
    println("looping over events in memory")
    for i=1:nrow(subdf)

        st = sample_types[subdf[i, :fileindex]]
        sample, iso, systematic = st[:sample], st[:iso], st[:systematic]
        
        ngen = -1
        if sample in keys(cross_sections)
            ngen = tot_res["$(sample)/$(iso)/$(systematic)/counters/generated"]
            @assert (typeof(cross_sections[sample]) <: Number && cross_sections[sample] > 0.0) "illegal cross section"
            @assert (typeof(ngen) <: Number && ngen > 0) "illegal ngen"
            
            ngens[i] = ngen
            xss[i] = cross_sections[sample]
            xsweights[i] = sample in keys(cross_sections) ? 1.0 * cross_sections[sample] / ngen : NA
        end

        proc = get_process(sample)

        processes[i] = (proc != :unknown ? string(proc) : string(sample))
        systematics[i] = string(systematic)
        samples[i] = sample
        isos[i] = string(iso)
        
        if DEBUG
            passes_mu = (isos[i] == "iso") .* (processes[i] == "gjets") .* (subdf[i, :hlt_mu] .== true) .*
                (subdf[i, :n_signal_mu] .== 1) .* (subdf[i, :n_signal_ele] .== 0) .* (subdf[i, :n_veto_mu] .== 0) .*
                (subdf[i, :n_veto_ele] .== 0) .* (subdf[i, :njets] .== 2) .* (subdf[i, :ntags] .== 1) .*
                (subdf[i, :mtw] .> 50) .* (subdf[i, :ljet_rms] .< 0.025)
            
            passes_ele = (isos[i] == "iso") .* (processes[i] == "gjets") .* (subdf[i, :hlt_ele] .== true) .*
                (subdf[i, :n_signal_mu] .== 0) .* (subdf[i, :n_signal_ele] .== 1) .* (subdf[i, :n_veto_mu] .== 0) .*
                (subdf[i, :n_veto_ele] .== 0) .* (subdf[i, :njets] .== 2) .* (subdf[i, :ntags] .== 1) .*
                (subdf[i, :met] .> 45) .* (subdf[i, :ljet_rms] .< 0.025)
            
            if isna(passes_mu)
                passes_mu = false
            end
            if isna(passes_ele)
                passes_ele = false
            end

            println("EV $nf fi=", subdf[i, :fileindex], " f=", md[subdf[i, :fileindex], :files],
                " ev=", int(subdf[i, :run]), ":", int(subdf[i, :lumi]), ":", int(subdf[i, :event]),
                " s=", samples[i], " p=", processes[i],
                " hm=", int(subdf[i, :hlt_mu]), " he=", int(subdf[i, :hlt_ele]),
                " nsm=", subdf[i, :n_signal_mu], " nse=", subdf[i, :n_signal_ele],
                " nvm=", subdf[i, :n_veto_mu], " nve=", subdf[i, :n_veto_ele],
                " nj=", subdf[i, :njets], " nt=", subdf[i, :ntags],
                " mtw=", subdf[i, :mtw],
                " met=", subdf[i, :met],
                " rms=", subdf[i, :ljet_rms],
                " i=", isos[i][1],
                " pm=$(int(passes_mu))",
                " pe=$(int(passes_ele))",
            )

        end
    end
    subdf["xsweight"] = xsweights
    subdf["subsample"] = samples 
    subdf["xs"] = xss
    subdf["ngen"] = ngens
    subdf["sample"] = processes
    subdf["systematic"] = systematics
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
    push!(dfs, df)
end

toc()
@assert length(dfs)>0 "no DataFrames were produced"

df = rbind(dfs)

inds = perform_selection(df)

##write output as CSV
include("../analysis/reweight.jl")
include("../analysis/split.jl")

println("reweighting")
reweight(df)

highmet = df[(inds[:mu] .* inds[:mtw]) .+ (inds[:ele] .* inds[:met]), :]
lowmet = df[(inds[:mu] .* !inds[:mtw]) .+ (inds[:ele] .* !inds[:met]), :]

systs = collect(keys(Stats.table(df["systematic"])))

for syst in systs
    for nt in [0, 1, 2]
        writetree(
            "$ofile.root.$(syst).$(nt).hmet",
            highmet[:((systematic .== $syst) .* (ntags .== $nt)), :]
        )
        writetree(
            "$ofile.root.$(syst).$(nt).lmet",
            lowmet[:((systematic .== $syst) .* (ntags .== $nt)), :]
        )
    end
end
