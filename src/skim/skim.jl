#julia skim.jl ofile infiles.txt
#runs a skim/event loop on EDM files on a single core
tstart = time()

println("hostname $(gethostname())")
using ROOT
using DataFrames
using HDF5
using JLD

include("xs.jl")

output_file = ARGS[1]
#iswritable(output_file) || error("output file $output_file is not writeable")

flist = Any[]
append!(flist, ARGS[2:])

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
            
            lepton_pt=Float32[], lepton_eta=Float32[], lepton_iso=Float32[], lepton_phi=Float32[],
            lepton_type=Int32[],
            lepton_id=Int32[], lepton_charge=Int32[],

#jets associated with t-channel
            bjet_pt=Float32[], bjet_eta=Float32[], bjet_mass=Float32[], bjet_id=Float32[], bjet_bd_a=Float32[], bjet_bd_b=Float32[], bjet_phi=Float32[], bjet_dr=Float32[],
            ljet_pt=Float32[], ljet_eta=Float32[], ljet_mass=Float32[], ljet_id=Float32[], ljet_bd_a=Float32[], ljet_bd_b=Float32[], ljet_rms=Float32[], ljet_phi=Float32[], ljet_dr=Float32[],
#
##spectator jets
#            sjet1_pt=Float32[], sjet1_eta=Float32[], sjet1_id=Float32[], sjet1_bd=Float32[], 
#            sjet2_pt=Float32[], sjet2_eta=Float32[], sjet2_id=Float32[], sjet2_bd=Float32[], 

#event-level characteristics
            cos_theta=Float32[], met=Float32[], njets=Int32[], ntags=Int32[], mtw=Float32[],
            C=Float32[],# D=Float32[], circularity=Float32[], sphericity=Float32[], isotropy=Float32[], aplanarity=Float32[], thrust=Float32[],  
            top_mass=Float32[], top_eta=Float32[], top_phi=Float32[],
            wjets_cls=Int32[],
            jet_cls=Int32[],
            
            nu_soltype=Int32[],

#file-level metadata
            run=Int64[], lumi=Int64[], event=Int64[],
            fileindex=Int64[],
            passes=Bool[],

#            xs=Float32[], nproc=Int64[],
#            fname=ASCIIString[]
        ),
        maxev
)

const sources = Dict{Symbol, Source}()

function part(x, y)
    return symbol(string(x, "_", y))
end

include("jet_cls.jl")

#see selection_step2_cfg.py for possible inputs
#leptons
for s in [:Pt, :Eta, :Phi, :relIso, :genPdgId, :Charge]
    sources[part(:muon, s)] = Source(:goodSignalMuonsNTupleProducer, s, :STPOLSEL2)
    sources[part(:electron, s)] = Source(:goodSignalElectronsNTupleProducer, s, :STPOLSEL2)
end

#jets
for s in [:Pt, :Eta, :Phi, :Mass, :partonFlavour, :bDiscriminatorCSV, :bDiscriminatorTCHP, :rms, :deltaR]
    sources[part(:bjet, s)] = Source(:highestBTagJetNTupleProducer, s, :STPOLSEL2)
    sources[part(:ljet, s)] = Source(:lowestBTagJetNTupleProducer, s, :STPOLSEL2)
    sources[part(:jets, s)] = Source(:goodJetsNTupleProducer, s, :STPOLSEL2)
end

sources[:cos_theta] = Source(:cosTheta, :cosThetaLightJet, :STPOLSEL2, Float64)
sources[:met] = Source(:patMETNTupleProducer, :Pt, :STPOLSEL2)
sources[part(:muon, :mtw)] = Source(:muMTW, symbol(""), :STPOLSEL2, Float64)
sources[part(:electron, :mtw)] = Source(:eleMTW, symbol(""), :STPOLSEL2, Float64)
sources[:njets] = Source(:goodJetCount, symbol(""), :STPOLSEL2, Int32)
sources[:ntags] = Source(:bJetCount, symbol(""), :STPOLSEL2, Int32)

sources[:nsignalmu] = Source(:muonCount, symbol(""), :STPOLSEL2, Int32)
sources[:nsignalele] = Source(:electronCount, symbol(""), :STPOLSEL2, Int32)

sources[part(:top, :mass)] = Source(:recoTopNTupleProducer, :Mass, :STPOLSEL2)
sources[part(:top, :eta)] = Source(:recoTopNTupleProducer, :Eta, :STPOLSEL2)
sources[part(:top, :phi)] = Source(:recoTopNTupleProducer, :Phi, :STPOLSEL2)

for v in [:C, :D, :circularity, :isotropy, :sphericity, :aplanarity, :thrust]
    sources[v] = Source(:eventShapeVars, v, :STPOLSEL2, Float64)
end

sources[:wjets_cls] = Source(:flavourAnalyzer, :simpleClass, :STPOLSEL2, Uint32)

sources[part(:electron, :nu_soltype)] = Source(:recoNuProducerEle, :solType, :STPOLSEL2, Int32)
sources[part(:muon, :nu_soltype)] = Source(:recoNuProducerMu, :solType, :STPOLSEL2, Int32)

const hlts = ASCIIString[
    "HLT_IsoMu24_eta2p1_v11",
    "HLT_IsoMu24_eta2p1_v12",
    "HLT_IsoMu24_eta2p1_v13",
    "HLT_IsoMu24_eta2p1_v14",
    "HLT_IsoMu24_eta2p1_v15",
    "HLT_IsoMu24_eta2p1_v17",
    "HLT_IsoMu24_eta2p1_v16",
    "HLT_Ele27_WP80_v8",
    "HLT_Ele27_WP80_v9",
    "HLT_Ele27_WP80_v10",
    "HLT_Ele27_WP80_v11",
]

function ifpresent(arr, n::Integer=1)
    if all(isna(arr)) 
        return NA
    end
    if length(arr)==n
        return arr[n]
    else
        return NA
    end
end

ispresent(x) = (typeof(x) != NAtype && !any(isna(x)))

function either(a, b, n::Integer=1)
    if length(a)==n && length(b)==0
        return (a[n], :first)
    elseif length(b)==n && length(a)==0
        return (b[n], :second)
    else
        return (NA, :neither)
    end
end

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

    df[i, :run], df[i, :lumi], df[i, :event] = where(events)
    df[i, :fileindex] = where_file(events)
    findex = df[i, :fileindex]
    
    sample = prfiles[findex, :cls][:sample]

#    #fill the file-level metadata
#    df[i, :xs] = haskey(cross_sections, sample) ? cross_sections[sample] : NA
#    df[i, :nproc] = prfiles[findex, :total_processed]

#    df[i, :fname] = flist[df[i, :fileindex]]
   
    nmu = events[sources[:nsignalmu]]
    nele = events[sources[:nsignalele]]
    df[i, :lepton_pt], which_lepton = either(events[sources[:muon_Pt]], events[sources[:electron_Pt]])
    
    if isna(nmu) || isna(nele)
        fails[:lepton] += 1
        continue
    end
    lepton_type = :neither
    if nmu==1 && nele==0
        lepton_type = :muon
        df[i, :lepton_type] = 13
    elseif nele==1 && nmu==0
        lepton_type = :electron
        df[i, :lepton_type] = 11
    end

    #event had no lepton
    if which_lepton == :neither
        fails[:lepton] += 1
        continue
    end

    df[i, :lepton_id] = events[sources[part(lepton_type, :genPdgId)]] |> ifpresent
    df[i, :lepton_eta] = events[sources[part(lepton_type, :Eta)]] |> ifpresent
    df[i, :lepton_iso] = events[sources[part(lepton_type, :relIso)]] |> ifpresent
    df[i, :lepton_charge] = events[sources[part(lepton_type, :Charge)]] |> ifpresent
    df[i, :lepton_phi] = events[sources[part(lepton_type, :Phi)]] |> ifpresent
    df[i, :mtw] = events[sources[part(lepton_type, :mtw)]]
    df[i, :met] = events[sources[:met]] |> ifpresent
    
  
    #event had no MET
    if (isna(df[i, :met]) || isna(df[i, :mtw]))
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
    df[i, :njets] = events[sources[:njets]]
    df[i, :ntags] = events[sources[:ntags]]
    
    #check for 2 jets
    if !(df[i, :njets] == 2 && df[i, :ntags] == 1)
        fails[:jet] += 1
        continue
    end

    df[i, :bjet_pt] = events[sources[:bjet_Pt]] |> ifpresent
    df[i, :bjet_eta] = events[sources[:bjet_Eta]] |> ifpresent
    df[i, :bjet_mass] = events[sources[:bjet_Mass]] |> ifpresent
    df[i, :bjet_id] = events[sources[:bjet_partonFlavour]] |> ifpresent
    df[i, :bjet_bd_a] = events[sources[:bjet_bDiscriminatorTCHP]] |> ifpresent
    df[i, :bjet_bd_b] = events[sources[:bjet_bDiscriminatorCSV]] |> ifpresent
    df[i, :bjet_phi] = events[sources[:bjet_Phi]] |> ifpresent
    df[i, :bjet_dr] = events[sources[:bjet_deltaR]] |> ifpresent

    df[i, :ljet_pt] = events[sources[:ljet_Pt]] |> ifpresent
    df[i, :ljet_eta] = events[sources[:ljet_Eta]] |> ifpresent
    df[i, :ljet_mass] = events[sources[:ljet_Mass]] |> ifpresent
    df[i, :ljet_id] = events[sources[:ljet_partonFlavour]] |> ifpresent
    df[i, :ljet_bd_a] = events[sources[:ljet_bDiscriminatorTCHP]] |> ifpresent
    df[i, :ljet_bd_b] = events[sources[:ljet_bDiscriminatorCSV]] |> ifpresent
    df[i, :ljet_rms] = events[sources[:ljet_rms]] |> ifpresent
    df[i, :ljet_phi] = events[sources[:ljet_Phi]] |> ifpresent
    df[i, :ljet_dr] = events[sources[:ljet_deltaR]] |> ifpresent
    
    df[i, :jet_cls] = jet_cls_to_number(jet_classification(df[i, :ljet_id], df[i, :bjet_id])) 
    df[i, :cos_theta] = events[sources[:cos_theta]]

   
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

    df[i, :wjets_cls] = events[sources[:wjets_cls]] |> ifpresent
    df[i, :top_mass] = events[sources[part(:top, :mass)]] |> ifpresent
    df[i, :top_eta] = events[sources[part(:top, :eta)]] |> ifpresent
    df[i, :top_phi] = events[sources[part(:top, :phi)]] |> ifpresent
    
    df[i, :nu_soltype] = events[sources[part(lepton_type, :nu_soltype)]] |> ifpresent

    df[i, :passes] = true
end

println("processed $(nproc/timeelapsed) events/second")


#Select only the events that actually pass
mydf = df[with(df, :(passes)), :]
describe(mydf)
println("total rows = $(nrow(mydf))")
println("failure reasons: $fails")

#save output
writetable("$(output_file)_processed.csv", prfiles)
writetree("$(output_file).root", mydf)

tend = time()
ttot = tend-tstart
println("total script time $ttot seconds")
