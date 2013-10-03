using ROOT
using DataFrames

output_file = ARGS[1]

flist = Any[]
append!(flist, ARGS[2:])

events = Events(convert(Vector{ASCIIString}, flist))

maxev = length(events)
#maxev = 100000

processed_files = DataFrame(files=flist)
df = similar(
        DataFrame(
            lepton_pt=Float32[], lepton_type=ASCIIString[], lepton_id=Int32[],
            bjet_pt=Float32[], bjet_eta=Float32[], bjet_id=Float32[], bjet_bd_a=Float32[], bjet_bd_b=Float32[],
            ljet_pt=Float32[], ljet_eta=Float32[], ljet_id=Float32[], ljet_bd_a=Float32[], ljet_bd_b=Float32[],
            run=Int64[], lumi=Int64[], event=Int64[], fileindex=Int64[],
            passes=Bool[],
            fname=ASCIIString[]
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
for s in [:Pt, :Eta, :Phi, :partonFlavour, :bDiscriminatorCSVMVA, :bDiscriminatorTCHP]
    sources[part(:bjet, s)] = Source(:highestBTagJetNTupleProducer, s, :STPOLSEL2)
    sources[part(:ljet, s)] = Source(:lowestBTagJetNTupleProducer, s, :STPOLSEL2)
end


function ifpresent(arr, n::Integer=1)
    if length(arr)==n
        return arr[n]
    else
        return NA
    end
end

function either(a, b, n::Integer=1)
    if length(a)==n && length(b)==0
        return (a[n], :first)
    elseif length(b)==n && length(a)==0
        return (b[n], :second)
    else
        return (NA, :neither)
    end
end


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
    
    df[i, :fname] = flist[df[i, :fileindex]]
    

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


    df[i, :bjet_pt] = events[sources[:bjet_Pt]] |> ifpresent
    df[i, :bjet_eta] = events[sources[:bjet_Eta]] |> ifpresent
    #df[i, :bjet_phi] = events[sources[:bjet_Phi]]
    df[i, :bjet_id] = events[sources[:bjet_partonFlavour]] |> ifpresent
    df[i, :bjet_bd_a] = events[sources[:bjet_bDiscriminatorTCHP]] |> ifpresent
    df[i, :bjet_bd_b] = events[sources[:bjet_bDiscriminatorCSVMVA]] |> ifpresent

    df[i, :ljet_pt] = events[sources[:ljet_Pt]] |> ifpresent
    df[i, :ljet_eta] = events[sources[:ljet_Eta]] |> ifpresent
    #df[i, :ljet_phi] = events[sources[:ljet_Phi]]
    df[i, :ljet_id] = events[sources[:ljet_partonFlavour]] |> ifpresent
    df[i, :ljet_bd_a] = events[sources[:ljet_bDiscriminatorTCHP]] |> ifpresent
    df[i, :ljet_bd_b] = events[sources[:ljet_bDiscriminatorCSVMVA]] |> ifpresent

    df[i, :passes] = true
end

println("processed $(nproc/timeelapsed) events/second")

#Select only the events that have a lepton
df = df[with(df, :(passes)), :]


function writezipped(fn, t)
    writetable(fn, t)

    run(`gzip -f9 $fn`)
end

writezipped("$(output_file)", df)
#writezipped("processed.csv", processed_files)
