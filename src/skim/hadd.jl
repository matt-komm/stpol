#!/home/joosep/.julia/ROOT/julia
include("../analysis/base.jl")

println("hostname $(gethostname()) ", "SLURM_JOB_ID" in keys(ENV) ? ENV["SLURM_JOB_ID"] : getpid())

const NOSKIM = ("STPOL_NOSKIM" in keys(ENV) && ENV["STPOL_NOSKIM"]=="1")
if NOSKIM
    println("*** skimming DEACTIVATED")
end

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
cols = [:passes, :bjet_pt, :ljet_pt, :bjet_eta, :hlt_mu, :hlt_ele, :event, :run, :lumi, :n_veto_mu, :n_veto_ele, :n_signal_mu, :n_signal_ele, :met, :ljet_rms, :pu_weight, :gen_weight, :top_weight, :C, :bjet_phi, :ljet_phi, :njets, :ntags, :ljet_dr, :bjet_dr, :shat, :ht, :cos_theta_lj, :cos_theta_bl, :cos_theta_lj_gen, :cos_theta_bl_gen, :top_mass, :ljet_eta, :mtw, :lepton_id, :lepton_type, :fileindex, :n_good_vertices, :lepton_pt, :jet_cls]

outcols = vcat(cols, [:subsample, :xs, :ngen, :sample, :isolation, :systematic, :xsweight])

tot_res = JSON.parse(readall(sumfname))
if DEBUG
    println(tot_res)
end
dfs = Any[]

nf=0

systs = ASCIIString[]

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
    processes = DataArray(Uint64, nrow(subdf))
    samples = DataArray(Uint64, nrow(subdf))
    systematics = DataArray(Uint64, nrow(subdf))
    isos = DataArray(Uint64, nrow(subdf))
    
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

        processes[i] = hash(string(proc))
        systematics[i] = hash(string(systematic))
        samples[i] = hash(string(sample))
        isos[i] = hash(string(iso))

        if !in(string(systematic), systs)
            push!(systs, string(systematic))
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

#write(jldopen("$ofile.jld", "w"), "df", df)
#run(`pbzip2 -f9 $ofile.jld`)

N = nrow(df)

#ch = chunks(50000, N)
#for _c in ch
#    sdf = df[_c, :]
#    _st = _c.start
#    writedf("$ofile.$(_st).jld", sdf)
#end

#for (cn, ct) in zip(colnames(df), coltypes(df))
#    println(cn, " ", ct)
#end

tic()
for syst in systs
    #println("writing systematic $syst")
    for nt in [0, 1, 2]
        sdf = df[:((systematic .== $(hash(syst))) .* (ntags .== $nt)), :]
        #println("writing tag $nt, ", toq())
        tic()
        write(jldopen("$ofile.jld.$(syst).$(nt)T", "w"), "df", sdf)
        writetree("$ofile.root.$(syst).$(nt)T", sdf)
    end
end
