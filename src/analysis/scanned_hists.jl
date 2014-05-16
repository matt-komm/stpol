include("base.jl")
include("preprocess_data.jl")

const PARS = JSON.parse(readall(ARGS[1]))
println("PARS=", PARS)

infname = PARS["infile"]

df, inds, grs, sdfs, sdfmap = preprocess_data(infname, "/home/joosep/singletop/temp/index.jld")
getgr(s) = sdfs[sdfmap[:from][s]];

function select_bdt(inds, bdt_cut::Real)
    for gr in grs
        inds[gr][:bdt_cut] = (getgr(gr)[:bdt_sig_bg] .> bdt_cut)
    end
end

function dosyst(scenario, variable, lep, sel, dsel, binning)
    k = scenario[1] 
    k::(Symbol, Symbol)
    v = scenario[2]
    v::Associative
    ret = Any[]

    println("systematic $k=>$v (id=$(myid()))")
    syst = v[:systematic]::Symbol

    if !(syst in grs)
        warn("$syst not found in processed data")
        return ret
    end

    sample = v[:sample]::Symbol
    w = v[:weight]::Function
    
    dd = sub(getgr(syst), sel(inds[syst], lep)&inds[syst][:sample][sample])
    
    h = makehist_1d(dd, variable, binning, w)
    if (sum(entries(h))==0)
        warn("$k was empty")
    else
        push!(ret, tuple(k, h))
    end

    return ret
end

function transfer_matrix(binning, lep::Symbol, sel::Function)
    #prepare transfer matrices
    tmats = Dict{(Symbol, Symbol), NHistogram}()
    weight_exs = Dict{(Symbol, Symbol), Function}()
    
    for (k, v) in scenarios
        v[:sample] != :tchan && continue
        #println("creating transfer matrix for $k")
        tmats[k] = NHistogram({binning, binning}) 
        
        weight_exs[k] = v[:weight] 
    end
    const tmats = deepcopy(tmats)

    hi = collect(values(tmats))[1]
    
    for gr in [:nominal] #loop over variated datasets
        #get signal
        const sig = sub(getgr(gr),
            inds[gr][:sample][:tchan]&inds[gr][:iso]&inds[gr][:truelepton][lep]
        )

        #get bool array of reconstructed values
        const recorows = sel(inds[gr], lep)

        #println("$gr=>$(scens_gr)")
        println("transfer matrix for $gr: Ntot=$(nrow(sig)), Ngen=$(sum(!isna(sig[:cos_theta_lj_gen]))), Nreco=$(sum(recorows))")
        
        if gr != :nominal
            const grscens = scens_gr[gr]
        else
            const grscens = scenarios[(:nominal, :unweighted)]
        end

        println("number of scenarios ", length(grscens))
        i = 1 
       
        #get gen, reco values, reconstruction flag
        println("looping over rows...")

        tic()

        hsize = tuple([length(ed) for ed in hi.edges]...)

        for row in eachrow(sig)
            
            const x = row[:cos_theta_lj_gen]
            const y = row[:cos_theta_lj]
    	    const reco = recorows[i]::Union(Bool, NAtype)
    
            #get bin indices according to first histogram in transfer matrix list
            const nx = (isna(x)||isnan(x)) ? 1 : searchsortedfirst(hi.edges[1], x)-1
    	    const ny = (isna(y)||isnan(y)||!reco) ? 1 : searchsortedfirst(hi.edges[2], y)-1
            const linind = sub2ind(hsize, nx, ny)
             
            for (scen_name, scen) in grscens
                
                const w = weight_exs[scen_name](row)
                
                #cont, ent = asarr(tmats[scen_name])
                #cont::Array{Float64, 2}
                #ent::Array{Float64, 2}

    	#        cont[nx, ny] += (isna(w)||isnan(w)) ? 0 : w 
    	#        ent[nx, ny] += 1
                
                tmats[scen_name].baseh.bin_contents[linind] += (isna(w)||isnan(w)) ? 0.0 : w 
                tmats[scen_name].baseh.bin_entries[linind] += 1.0
            end
            i+=1
        end
        toc()
    end
    for (k, v) in tmats
        println("$k ", sum(v.baseh.bin_contents))
    end
    return tmats
end

function draw_syst_hists(variable::Symbol, binning::AbstractVector{Float64}, lep::Symbol, sel::Function, dsel::Function)
    hd = Dict()
    
    println("nominal histograms...")
    hh1 = makehists(
        getgr(:nominal),
        inds[:nominal], sel(inds[:nominal], lep), dsel(inds[:nominal], lep), variable, binning
    )
    
    hh2 = makehists(getgr(:unknown),
        inds[:unknown], sel(inds[:unknown], lep), dsel(inds[:unknown], lep), variable, binning
    )
    
    hh1[:qcd] = hh2[:qcd] - hh1[:qcd]
    hh1[:DATA] = hh2[:DATA]

    for (k, v) in hh1
        hd[(:nominal, symbol(k))] = deepcopy(v)
    end

    println("systematics...")
    scs = reduce(
        vcat,
        map(x->dosyst(x, variable, lep, sel, dsel, binning), scenarios)
    )
    
    for (k,v) in scs
        hd[k] = v 
    end

    return hd
end

function prepare_hd(hd)
    out = Dict()
    for s in [:DATA, :tchan, :wjets, :ttjets, :twchan, :schan, :qcd, :dyjets, :diboson, :gjets]
        out[string(s)] = hd[(:nominal, s)]
    end
    return out
end

const DEFBINNING=vcat(-Inf, linspace(-1, 1, 10), Inf)

function projecthists(sel, var, binning)
    dsel(x, lep) = x[:sample][symbol("data_$lep")]
    
    t0 = time()
    #hmu = draw_syst_hists(var, binning, :mu, sel, dsel);
    #hele = draw_syst_hists(var, binning, :ele, sel, dsel);

    mat_mu = transfer_matrix(binning, :mu, sel)
    mat_ele = transfer_matrix(binning, :ele, sel)
    t1 = time()

    println("projection time: $(t1-t0)")
    return {:mu=>{:hists=>mu, :matrix=>mat_mu}, :ele=>{:hists=>ele, :matrix=>mat_ele}}
#    return {:mu=>mat_mu, :ele=>mat_ele}
end


###
### Main
###

ct1 = {:cos_theta_lj, DEFBINNING}
k = linspace(-1, 1, 11)[1]
argset = {
	{(x, lep)->x[:njets][2]&x[:ntags][1]&x[:dr]&x[lep]&x[:bdt_grid][k], ct1...},
#	{(x, lep)->x[:njets][2]&x[:ntags][1]&x[:dr]&x[lep], ct1...}
}

select_bdt(inds, float(PARS["bdt_cut"]))
r = projecthists(
    (x, lep)->x[:njets][2]&x[:ntags][1]&x[:dr]&x[lep]&x[:bdt_cut]&x[:qcd_mva][lep],
    :cos_theta_lj,
    float(PARS["binning"])
)
fi = jldopen(PARS["outfile"], "w")
write(fi, "res", hists)
close(fi)
