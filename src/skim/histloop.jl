#!/home/joosep/.julia/ROOT/julia
#julia skim.jl ofile infiles.txt
#runs a skim/event loop on EDM files on a single core
tstart = time()
println("hostname $(gethostname()) ", "SLURM_JOB_ID" in keys(ENV) ? ENV["SLURM_JOB_ID"] : getpid())

include("../analysis/histo.jl")

using ROOT, HEP, Hist

include("xs.jl")

output_file = ARGS[1]

flist = Any[]
append!(flist, ARGS[2:])

#try to load the Events 
events = Events(convert(Vector{ASCIIString}, flist))

maxev = length(events) 
println("running over $maxev events")

include("stpol.jl")

#Loop over the events
println("Beginning event loop")
nproc = 0

res = Dict()
hdescs = {
  :cos_theta_lj=>(120, -1, 1),
  :met=>(120, 0, 300),
  :mtw=>(120, 0, 300),
  :bdt_sig_bg=>(120, -1, 1),
  :C=>(120, 0, 1),
  :lepton_pt=>(120, 0, 300),
  :top_mass=>(120, 80, 360),
  :ljet_eta=>(120, -5, 5)
}

function gethist(res, k, var)
  if !in(k, keys(res))
    res[k] = Histogram(hdescs[var]...)
  end
  return res[k]
end

function fill_bdt_inputs(res, cache, key)
    for var in [:lepton_pt, :C, :ljet_eta, :top_mass]
        h = gethist(res, key, var)
        hfill!(h, cache[var])
    end
end

tic()
timeelapsed = @elapsed for i=1:maxev
    nproc += 1
    if nproc%(ceil(maxev/20)) == 0
        println("$nproc ($(ceil(nproc/maxev*100.0))%) events processed")
        toc()
        tic()
    end
    
    to!(events, i)
    
    fn = string("file:", split(get_current_file_name(events), ":")[1])
    st = sample_type(fn)
    iso = st[:iso]
    syst = st[:systematic]
    sample = st[:sample]

    cos_theta_lj_gen = events[sources[:cos_theta_lj_gen]] |> ifpresent
    cos_theta_bl_gen = events[sources[:cos_theta_bl_gen]] |> ifpresent
    
    hlt = passes_hlt(events, hlts) 
    hlt_mu = passes_hlt(events, HLTS[:mu]) 
    hlt_ele = passes_hlt(events, HLTS[:ele]) 
    
    nsignalmu = events[sources[:nsignalmu]]
    nsignalele = events[sources[:nsignalele]]
    
    nvetomu = events[sources[vetolepton(:mu)]]
    nvetoele = events[sources[vetolepton(:ele)]]
    
    (isna(nsignalmu) || isna(nsignalele) || isna(nvetomu) || isna(nvetoele)) && continue

    lepton_type = nothing
    if (nsignalmu==1 && nsignalele==0 && nvetomu==0 && nvetoele==1 && hlt_mu)
        lepton_type = :muon
    elseif (nsignalmu==0 && nsignalele==1 && nvetomu==0 && nvetoele==1 && hlt_ele)
        lepton_type = :electron
    else
        continue
    end
        
    lepton_id = events[sources[part(lepton_type, :genPdgId)]] |> ifpresent
    lepton_pt = events[sources[part(lepton_type, :Pt)]] |> ifpresent
    
    njets = events[sources[:njets]]
    ntags = events[sources[:ntags]]
    
    (isna(njets) || njets < 2) && continue
    (isna(ntags) || njets < 0) && continue
    
    met = events[sources[:met]] |> ifpresent
    mtw = events[sources[part(lepton_type, :mtw)]] |> ifpresent
    
    bjet_dr = events[sources[:bjet_deltaR]] |> ifpresent
    ljet_dr = events[sources[:ljet_deltaR]] |> ifpresent
    bjet_eta = events[sources[:bjet_Eta]] |> ifpresent
    ljet_eta = events[sources[:ljet_Eta]] |> ifpresent
    bjet_id = events[sources[:bjet_partonFlavour]] |> ifpresent
    ljet_id = events[sources[:ljet_partonFlavour]] |> ifpresent
    
    jet_cls = jet_cls_to_number(jet_classification(ljet_id, bjet_id)) 
    cos_theta_lj = events[sources[:cos_theta_lj]] |> ifpresent
    cos_theta_bl = events[sources[:cos_theta_bl]] |> ifpresent
    
    n_good_vertices = events[sources[:n_good_vertices]] |> ifpresent
        
    C = events[sources[:C]]
    top_mass = events[sources[part(:top, :Mass)]] |> ifpresent
   
    k = "$iso/$(lepton_type)/$(njets)J/$(ntags)T/$(syst)/$(sample)"
    
    h = gethist(res, "$(k)/met_off/cos_theta_lj", :cos_theta_lj)
    hfill!(h, cos_theta_lj)
    
    h = gethist(res, "$(k)/met_off/met", :met)
    hfill!(h, met)
    
    h = gethist(res, "$(k)/met_off/mtw", :mtw)
    hfill!(h, mtw)
    
    cache = {:lepton_pt=>lepton_pt, :C=>C, :ljet_eta=>ljet_eta, :top_mass=>top_mass}
    if (!isna(met) && met>45)
        fill_bdt_inputs(res, cache, "$k/met45/$var") 
    end
    if (!isna(met) && met>60)
        fill_bdt_inputs(res, cache, "$k/met60/$var") 
    end
    if (!isna(mtw) && mtw>50)
        fill_bdt_inputs(res, cache, "$k/mtw50/$var") 
    end

    if (isna(met) || isna(mtw) || (lepton_type==:muon && mtw<50) || (lepton_type==:electron && met<45))
        continue
    end
    
    fill_bdt_inputs(res, cache, "$k/met_on/$var") 
end

println("processed $(nproc/timeelapsed) events/second")

tend = time()
ttot = tend-tstart
println("total script time $ttot seconds")
