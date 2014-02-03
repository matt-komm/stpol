include("base.jl");
#include("$BASE/src/analysis/hplot.jl")
#include("$BASE/src/analysis/fit.jl")
#include("$BASE/src/analysis/pyplot.jl")

include("$BASE/src/analysis/hroot.jl")
println(methods(toroot))

println("loading histograms...")
tic()

infile = ARGS[1]
outdir = ARGS[2]
mkpath(outdir)

fi = jldopen(infile)

const hists = read(fi, "ret")

toc()

function preph(lepton, hists)
    ret = Dict()
    
    MH = Dict()

    datasamp = symbol("data_$lepton");
    samples = vcat(mcsamples..., datasamp)
    for k in keys(hists)
        typeof(k) <: Dict || continue
        #k[:sample] != :data_ele && continue
        (:lepton in keys(k) && k[:lepton] != lepton ) && continue
        k[:sample] in samples || continue
        k[:obj] == :cos_theta_lj || continue
        k[:scenario]==:unweighted && k[:sample]!=datasamp && continue
        
        s1 = k[:systematic] in keys(dd) ? dd[k[:systematic]] : k[:systematic]
        s2 = k[:scenario]
        
        
        if s1==:nominal && s2==:nominal
            s = :nominal
        elseif s1==:nominal
            s = s2
        elseif s2==:nominal
            s = s1
        else
            s = :unknown
        end
        
        dir = nothing
        if contains(string(s), "__up")
            dir = :up
            s = join(split(string(s), "__")[1:end-1], "__")|>symbol
        elseif contains(string(s), "__down")
            dir = :down
            s = join(split(string(s), "__")[1:end-1], "__")|>symbol
        end
        samp = k[:sample]
        if samp==datasamp
            samp = :DATA
        end
        MH[k[:lepton], k[:iso], samp, s, dir] = hists[k] 
    end
    
    ret["DATA"] = MH[(lepton,:iso,:DATA,:unknown,nothing)]
    for s in mcsamples
        ret[string(s)] = lumis[lepton] * MH[(lepton,:iso, s, :nominal, nothing)]
    end

    mc_aiso = lumis[lepton] * sum([MH[(lepton,:iso, s, :nominal, nothing)] for s in mcsamples])

    qcd_sf = get_sf(2, 1, lepton)
    ret["qcd"] = qcd_sf * (MH[(lepton,:antiiso,:DATA,:unknown,nothing)] - mc_aiso)
    
    systs = Dict()
    
    for samp in [:wjets, :tchan, :ttjets]
        for v in map(x->x[4], keys(MH))
            for d in [:up, :down]

                k = (lepton, :iso, samp, v, d)
                if k in keys(MH)
                    ret["$(samp)__$(v)__$(d)"] = MH[k]
                end
            end
            
        end
    end
    return ret
end

function prep_transfermatrix(hists)
    MH = Dict()
    for k in keys(hists)
        typeof(k) <: Dict || continue
        k[:obj] == :transfer_matrix || continue
        
        s = k[:scenario]
        
        dir = nothing
        if contains(string(s), "__up")
            dir = :up
            s = join(split(string(s), "__")[1:end-1], "__")|>symbol
        elseif contains(string(s), "__down")
            dir = :down
            s = join(split(string(s), "__")[1:end-1], "__")|>symbol
        end
        truelep = string(k[:true_lep]>0 ? "m" : "p", abs(k[:true_lep]))
        
        MH["tm__pdgid_$(truelep)__$(s)__$(dir)"] = hists[k]
    end
    return MH
end

h = preph(:mu, hists)
tm = prep_transfermatrix(hists)

for (k, v) in h
    println("converting $k to $outdir/hists.root/$k")
    hi = toroot("$outdir/hists.root", string(k), v::Histogram, "RECO")
end

for (k, v) in tm
    println("converting 2D histogram $k to $outdir/tmatrix.root/$k")
    toroot("$outdir/tmatrix.root", string(k), v::NHistogram, {"GEN", "RECO"})
end

