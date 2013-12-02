#!/home/joosep/.julia/ROOT/julia
#julia skim.jl ofile infiles.txt
#runs a skim/event loop on EDM files on a single core
tstart = time()
println("hostname $(gethostname())")

using ROOT
using DataFrames
using HDF5
using JLD
using HEP

include("xs.jl")

NOSKIM = ("STPOL_NOSKIM" in keys(ENV) && ENV["STPOL_NOSKIM"]=="1")
if NOSKIM
    println("***skimming DEACTIVATED")
end

output_file = ARGS[1]

flist = Any[]
append!(flist, ARGS[2:])

#try to load the Events 
events = nothing
while true
    try
        events = Events(convert(Vector{ASCIIString}, flist))
        break
    catch e
        warn(e)
    end
end

#save information on spectator jets
const do_specjets = false

maxev = length(events) 
println("running over $maxev events")

#metadata
processed_files = DataFrame(files=flist)

#events
df = similar(
        DataFrame(
            hlt=Bool[],
            hlt_mu=Bool[], hlt_ele=Bool[],
            
            lepton_pt=Float32[], lepton_eta=Float32[],
            #lepton_iso=Float32[], lepton_phi=Float32[],
            lepton_type=Float32[],
            lepton_id=Int32[], lepton_charge=Int32[],

#jets associated with t-channel
            bjet_pt=Float32[], bjet_eta=Float32[], bjet_mass=Float32[], bjet_id=Float32[],
            #bjet_bd_a=Float32[],
            bjet_bd_b=Float32[],
            bjet_phi=Float32[],
            bjet_dr=Float32[],

            ljet_pt=Float32[], ljet_eta=Float32[], ljet_mass=Float32[], ljet_id=Float32[],
            #ljet_bd_a=Float32[],
            ljet_bd_b=Float32[],
            ljet_rms=Float32[],
            ljet_phi=Float32[],
            ljet_dr=Float32[],
#
##spectator jets
#            sjet1_pt=Float32[], sjet1_eta=Float32[], sjet1_id=Float32[], sjet1_bd=Float32[], 
#            sjet2_pt=Float32[], sjet2_eta=Float32[], sjet2_id=Float32[], sjet2_bd=Float32[], 

#event-level characteristics
            cos_theta_lj=Float32[], 
            cos_theta_bl=Float32[], 
            met=Float32[], njets=Int32[], ntags=Int32[], mtw=Float32[],
            C=Float32[],# D=Float32[], circularity=Float32[], sphericity=Float32[], isotropy=Float32[], aplanarity=Float32[], thrust=Float32[],  
            top_mass=Float32[], top_eta=Float32[], top_phi=Float32[], top_pt=Float32[],
            #wjets_cls=Int32[],
            jet_cls=Int32[],
            ht=Float32[], shat=Float32[],
            
            nu_soltype=Int32[],
            n_signal_mu=Int32[], n_signal_ele=Int32[],
            n_veto_mu=Int32[], n_veto_ele=Int32[],

#weights
            pu_weight=Float32[],

#file-level metadata
            run=Int64[], lumi=Int64[], event=Int64[],
            fileindex=Int64[],
            passes=Bool[],

        ),
        maxev
)

include("stpol.jl")

#Loop over the lumi sections, get the total processed event count
prfiles = similar(
    DataFrame(
        files=ASCIIString[],
        total_processed=Int64[],
        cls=Any[]
    ),
    length(flist)
)

i = 1
for fi in flist
    x = ROOT.get_counter_sum([fi], "singleTopPathStep1MuPreCount")
    prfiles[i, :files] = fi
    prfiles[i, :total_processed] = x
    prfiles[i, :cls] = sample_type(fi)
    i += 1
end

#Loop over the events
println("Beginning event loop")
nproc = 0

fails = {
    :lepton => 0,
    :met => 0,
    :jet => 0,
}

tic()
timeelapsed = @elapsed for i=1:maxev
    nproc += 1

    if nproc%(ceil(maxev/20)) == 0
        println("$nproc ($(ceil(nproc/maxev*100.0))%) events processed")
        toc()
        tic()
    end
    to!(events, i)

    df[i, :passes] = false
    
    df[i, :hlt] = passes_hlt(events, hlts) 
    df[i, :hlt_mu] = passes_hlt(events, HLTS[:mu]) 
    df[i, :hlt_ele] = passes_hlt(events, HLTS[:ele]) 

    df[i, :run], df[i, :lumi], df[i, :event] = where(events)
    df[i, :fileindex] = where_file(events)

    df[i, :pu_weight] = events[sources[weight(:pu)]] |> ifpresent

    findex = df[i, :fileindex]
    
    sample = prfiles[findex, :cls][:sample]

#    #fill the file-level metadata
#    df[i, :xs] = haskey(cross_sections, sample) ? cross_sections[sample] : NA
#    df[i, :nproc] = prfiles[findex, :total_processed]

#    df[i, :fname] = flist[df[i, :fileindex]]
   
    nmu = events[sources[:nsignalmu]]
    nele = events[sources[:nsignalele]]
    df[i, :lepton_pt], lepton_type = either(events[sources[:muon_Pt]], events[sources[:electron_Pt]])
    df[i, :n_signal_mu] = nmu 
    df[i, :n_signal_ele] = nele

    if isna(nmu) || isna(nele)
        fails[:lepton] += 1
        continue
    end
    
    lepton_type = nothing
    if nmu==1 && nele==0
        lepton_type = :muon
        df[i, :lepton_type] = 13
    elseif nele==1 && nmu==0
        lepton_type = :electron
        df[i, :lepton_type] = 11
    else
        fails[:lepton] += 1
        continue
    end
   
    nveto_mu = events[sources[vetolepton(:mu)]] |> ifpresent
    nveto_ele = events[sources[vetolepton(:ele)]] |> ifpresent
    df[i, :n_veto_mu] = nveto_mu
    df[i, :n_veto_ele] = nveto_ele

    if nveto_mu != 0 || nveto_ele != 0
        fails[:lepton] += 1
        continue
    end

    df[i, :lepton_id] = events[sources[part(lepton_type, :genPdgId)]] |> ifpresent
    df[i, :lepton_eta] = events[sources[part(lepton_type, :Eta)]] |> ifpresent
    #df[i, :lepton_iso] = events[sources[part(lepton_type, :relIso)]] |> ifpresent
    df[i, :lepton_charge] = events[sources[part(lepton_type, :Charge)]] |> ifpresent
    #df[i, :lepton_phi] = events[sources[part(lepton_type, :Phi)]] |> ifpresent
    df[i, :mtw] = events[sources[part(lepton_type, :mtw)]]
    df[i, :met] = events[sources[:met]] |> ifpresent
    
  
    #event had no MET
    if (isna(df[i, :met]) || isna(df[i, :mtw]) || df[i, :met] < 00)
        fails[:met] += 1
        continue
    end

#    #check for muon/electron and mtw/met
#    if  (lepton_type == :muon && df[i, :mtw] < 10.0) ||
#        (lepton_type == :electron && df[i, :met] < 10.0)
#        fails[:met] += 1
#        continue
#    end
    
    #get jet, tag
    df[i, :njets] = events[sources[:njets]] |> ifpresent
    df[i, :ntags] = events[sources[:ntags]] |> ifpresent
    
    #check for 2 jets
    if !(df[i, :njets] >= 2 && df[i, :ntags] >= 0)
        fails[:jet] += 1
        continue
    end

    df[i, :bjet_pt] = events[sources[:bjet_Pt]] |> ifpresent
    df[i, :bjet_eta] = events[sources[:bjet_Eta]] |> ifpresent
    df[i, :bjet_mass] = events[sources[:bjet_Mass]] |> ifpresent
    df[i, :bjet_id] = events[sources[:bjet_partonFlavour]] |> ifpresent
    #df[i, :bjet_bd_a] = events[sources[:bjet_bDiscriminatorTCHP]] |> ifpresent
    df[i, :bjet_bd_b] = events[sources[:bjet_bDiscriminatorCSV]] |> ifpresent
    df[i, :bjet_phi] = events[sources[:bjet_Phi]] |> ifpresent
    df[i, :bjet_dr] = events[sources[:bjet_deltaR]] |> ifpresent

    df[i, :ljet_pt] = events[sources[:ljet_Pt]] |> ifpresent
    df[i, :ljet_eta] = events[sources[:ljet_Eta]] |> ifpresent
    df[i, :ljet_mass] = events[sources[:ljet_Mass]] |> ifpresent
    df[i, :ljet_id] = events[sources[:ljet_partonFlavour]] |> ifpresent
    #df[i, :ljet_bd_a] = events[sources[:ljet_bDiscriminatorTCHP]] |> ifpresent
    df[i, :ljet_bd_b] = events[sources[:ljet_bDiscriminatorCSV]] |> ifpresent
    df[i, :ljet_rms] = events[sources[:ljet_rms]] |> ifpresent
    df[i, :ljet_phi] = events[sources[:ljet_Phi]] |> ifpresent
    df[i, :ljet_dr] = events[sources[:ljet_deltaR]] |> ifpresent
    
    df[i, :jet_cls] = jet_cls_to_number(jet_classification(df[i, :ljet_id], df[i, :bjet_id])) 
    df[i, :cos_theta_lj] = events[sources[:cos_theta_lj]]

   
    if do_specjets
        
        #get all jets
        jet_pts = events[sources[part(:jets, :Pt)]]
        if !ispresent(jet_pts) || length(jet_pts)==0
            continue
        end
        jet_etas = events[sources[part(:jets, :Eta)]]
        jet_ids  = events[sources[part(:jets, :partonFlavour)]]
        jet_bds  = events[sources[part(:jets, :bDiscriminatorCSV)]]
        
        if all(map(ispresent, Any[jet_pts, jet_etas, jet_ids, jet_bds]))
            #get the indices of the b-tagged jet and the light jet
            indb = find(x -> abs(x-df[i, :bjet_pt])<eps(x), jet_pts)[1]
            indl = find(x -> abs(x-df[i, :ljet_pt])<eps(x), jet_pts)[1]

            #get the indices of the other jets
            specinds = Int64[]
            for k=1:length(jet_pts)
                if k!=indb && k!=indl
                    push!(specinds, k)
                end
            end

            #get all the other jets
            #order by pt-descending
            j = 1
            for (pt, eta, id, bd, ind) in sort(
                [z for z in zip(jet_pts, jet_etas, jet_ids, jet_bds, [1:length(jet_pts)])],
                rev=true
            )
                #is a 'spectator jet'
                if (ind in specinds)
                    df[i, symbol("sjet$(j)_pt")] = pt
                    df[i, symbol("sjet$(j)_eta")] = eta
                    df[i, symbol("sjet$(j)_id")] = id
                    df[i, symbol("sjet$(j)_bd")] = bd
                    
                    #up to two
                    if j==2
                        break
                    else
                        j += 1
                    end
                end
            end
        end
    end

    #for v in [:C, :D, :circularity, :isotropy, :sphericity, :aplanarity, :thrust]
    for v in [:C]
        df[i, v] = events[sources[v]]
    end

    #df[i, :wjets_cls] = events[sources[:wjets_cls]] |> ifpresent
    for k in [:Pt, :Eta, :Phi, :Mass]
        p = part(:top, k)
        df[i, lowercase(string(p))] = events[sources[p]] |> ifpresent
    end

    df[i, :nu_soltype] = events[sources[part(lepton_type, :nu_soltype)]] |> ifpresent
   
    #calculate the invariant mass of the system
    totvec = FourVectorSph(0.0, 0.0, 0.0, 0.0)
    for particle in [:top, :ljet]
        vec = Float64[]
        #this should be in the order of FourVectorSph
        for k in [:pt, :eta, :phi, :mass]
            v = convert(Float64, df[i, part(particle, k)])
            push!(vec, v)
        end
        v = FourVectorSph(vec...)
        totvec += v
    end

    df[i, :shat] = l(totvec)
    df[i, :ht] = df[i, :bjet_pt] + df[i, :ljet_pt]

    df[i, :passes] = true
end

println("processed $(nproc/timeelapsed) events/second")


#Select only the events that actually pass
mydf = NOSKIM ? df : df[with(df, :(passes)), :]
#describe(mydf)
println("total rows = $(nrow(mydf))")
println("failure reasons: $fails")

#save output
writetable("$(output_file)_processed.csv", prfiles)
writetree("$(output_file).root", mydf)

tend = time()
ttot = tend-tstart
println("total script time $ttot seconds")
