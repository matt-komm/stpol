using ROOT
using DataFrames
using HDF5
using JLD

include("xs.jl")

output_file = ARGS[1]

flist = Any[]
append!(flist, ARGS[2:])

events = Events(convert(Vector{ASCIIString}, flist))

list_branches(events)

maxev = length(events)

processed_files = DataFrame(files=flist)
df = similar(
        DataFrame(
            lepton_pt=Float32[], lepton_eta=Float32[], lepton_iso=Float32[], lepton_type=ASCIIString[], lepton_id=Int32[],
            bjet_pt=Float32[], bjet_eta=Float32[], bjet_id=Float32[], bjet_bd_a=Float32[], bjet_bd_b=Float32[],
            ljet_pt=Float32[], ljet_eta=Float32[], ljet_id=Float32[], ljet_bd_a=Float32[], ljet_bd_b=Float32[],
            sjet1_pt=Float32[], sjet1_eta=Float32[], sjet1_id=Float32[], sjet1_bd=Float32[], 
            sjet2_pt=Float32[], sjet2_eta=Float32[], sjet2_id=Float32[], sjet2_bd=Float32[], 
            cos_theta=Float32[], met=Float32[], njets=Int32[], ntags=Int32[], mtw=Float32[],
            run=Int64[], lumi=Int64[], event=Int64[],
            fileindex=Int64[],
            passes=Bool[],
            xs=Float32[], nproc=Int64[],
            #fname=ASCIIString[]
        ),
        maxev
)

const sources = Dict{Symbol, Source}()

function part(x, y)
    return symbol(string(x, "_", y))
end

#leptons
for s in [:Pt, :Eta, :Phi, :relIso, :genPdgId]
    sources[part(:muon, s)] = Source(:goodSignalMuonsNTupleProducer, s, :STPOLSEL2)
    sources[part(:electron, s)] = Source(:goodSignalElectronsNTupleProducer, s, :STPOLSEL2)
end

#jets
for s in [:Pt, :Eta, :Phi, :partonFlavour, :bDiscriminatorCSV, :bDiscriminatorTCHP]
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
tic()
timeelapsed = @elapsed for i=1:maxev
    nproc += 1

    if nproc%(floor(maxev/20)) == 0
        println("$nproc ($(floor(nproc/maxev*100.0))%) events processed")
        toc()
        tic()
    end
    to!(events, i)

    df[i, :passes] = false

    df[i, :run], df[i, :lumi], df[i, :event] = where(events)
    df[i, :fileindex] = where_file(events)
    findex = df[i, :fileindex]
    
    sample = prfiles[findex, :cls][:sample]

    #fill the file-level metadata
    df[i, :xs] = haskey(cross_sections, sample) ? cross_sections[sample] : NA
    df[i, :nproc] = prfiles[findex, :total_processed]

#    df[i, :fname] = flist[df[i, :fileindex]]
    
    df[i, :lepton_pt], which_lepton = either(events[sources[:muon_Pt]], events[sources[:electron_Pt]])

    lepton_type = :neither
    if which_lepton == :first
        lepton_type = :muon
    elseif which_lepton == :second
        lepton_type = :electron
    end

    df[i, :lepton_type] = string(lepton_type)

    if which_lepton == :neither
        df[i, :passes] = false
        continue
    end

    df[i, :lepton_id] = events[sources[part(lepton_type, :genPdgId)]][1]
    df[i, :lepton_eta] = events[sources[part(lepton_type, :Eta)]][1]
    df[i, :lepton_iso] = events[sources[part(lepton_type, :relIso)]][1]
    df[i, :mtw] = events[sources[part(lepton_type, :mtw)]]
    df[i, :met] = ifpresent(events[sources[:met]])

    df[i, :njets] = events[sources[:njets]]
    df[i, :ntags] = events[sources[:ntags]]
    
    if !(df[i, :njets] >= 2 && df[i, :ntags] >= 0)
        df[i, :passes] = false
        continue
    end

    df[i, :bjet_pt] = events[sources[:bjet_Pt]] |> ifpresent
    df[i, :bjet_eta] = events[sources[:bjet_Eta]] |> ifpresent
    #df[i, :bjet_phi] = events[sources[:bjet_Phi]]
    df[i, :bjet_id] = events[sources[:bjet_partonFlavour]] |> ifpresent
    df[i, :bjet_bd_a] = events[sources[:bjet_bDiscriminatorTCHP]] |> ifpresent
    df[i, :bjet_bd_b] = events[sources[:bjet_bDiscriminatorCSV]] |> ifpresent

    df[i, :ljet_pt] = events[sources[:ljet_Pt]] |> ifpresent
    df[i, :ljet_eta] = events[sources[:ljet_Eta]] |> ifpresent
    #df[i, :ljet_phi] = events[sources[:ljet_Phi]]
    df[i, :ljet_id] = events[sources[:ljet_partonFlavour]] |> ifpresent
    df[i, :ljet_bd_a] = events[sources[:ljet_bDiscriminatorTCHP]] |> ifpresent
    df[i, :ljet_bd_b] = events[sources[:ljet_bDiscriminatorCSV]] |> ifpresent
    
    df[i, :cos_theta] = events[sources[:cos_theta]]

    jet_pts = events[sources[part(:jets, :Pt)]]
    ispresent(jet_pts) || continue
    jet_etas = events[sources[part(:jets, :Eta)]]
    ispresent(jet_etas) || continue
    jet_ids  = events[sources[part(:jets, :partonFlavour)]]
    ispresent(jet_ids) || continue
    jet_bds  = events[sources[part(:jets, :bDiscriminatorCSV)]]
    ispresent(jet_bds) || continue

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

    j = 1
    for (pt, eta, id, bd, ind) in sort(
        [z for z in zip(jet_pts, jet_etas, jet_ids, jet_bds, [1:length(jet_pts)])],
        rev=true
    )
        if (ind in specinds)
            df[i, symbol("sjet$(j)_pt")] = pt
            df[i, symbol("sjet$(j)_eta")] = eta
            df[i, symbol("sjet$(j)_id")] = id
            df[i, symbol("sjet$(j)_bd")] = bd
            
            if j==2
                break
            else
                j += 1
            end
        end
    end

    #println(join(pts, ","), "|", df[i, :bjet_pt], "|", df[i, :ljet_pt], ":",indb, ":", indl)
    df[i, :passes] = true
end

println("processed $(nproc/timeelapsed) events/second")

#Select only the events that have a lepton
mydf = df[with(df, :(passes)), :]
#mydf = df

function writezipped_jld(fn, obj::DataFrame)
    fi = jldopen("$fn.jld", "w")
    write(fi, "stpol_events", obj)
    write(fi, "processed_files", flist)
    close(fi)
    run(`gzip -f9 $fn.jld`)
end

function writezipped_csv(fn, obj::DataFrame)
    writetable("$fn.csv", obj)
    run(`gzip -f9 $fn.csv`)
end

#writetable("$(output_file).csv", mydf)
writetable("$(output_file)_processed.csv", prfiles)
ROOT.writetree("$(output_file).root", mydf)
