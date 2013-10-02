using ROOT
using DataFrames

files = {
    :tchan => "tchan.txt"
}

flist = Any[]
for (k, fname) in files
    append!(flist, split(open(readall, fname)))
end

events = Events(convert(Vector{ASCIIString}, flist))

maxev = length(events)

processed_files = DataFrame(files=flist)
df = similar(
        DataFrame(
            lepton_pt=Float32[], lepton_type=ASCIIString[], lepton_id=Int32[],
            bjet_pt=Float32[], bjet_eta=Float32[], bjet_id=Float32[],
            ljet_pt=Float32[], ljet_eta=Float32[], ljet_id=Float32[],
            run=Int64[], lumi=Int64[], event=Int64[], fileindex=Int64[],
            passes=Bool[]
        ),
        maxev
)



const sources = Dict{Symbol, Source}()

function part(x, y)
    return symbol(string(x, "_", y))
end

for s in [:Pt, :Eta, :Phi, :relIso, :genPdgId]
    sources[part(:muon, s)] = Source(:goodSignalMuonsNTupleProducer, s, :STPOLSEL2)
    sources[part(:electron, s)] = Source(:goodSignalElectronsNTupleProducer, s, :STPOLSEL2)
end

for s in [:Pt, :Eta, :Phi, :partonFlavour]
    sources[part(:bjet, s)] = Source(:highestBTagJetNTupleProducer, s, :STPOLSEL2)
    sources[part(:ljet, s)] = Source(:lowestBTagJetNTupleProducer, s, :STPOLSEL2)
end

function either(a, b)
    if length(a)==1 && length(b)==0
        return (a[1], :first)
    elseif length(b)==1 && length(a)==0
        return (b[1], :second)
    else
        return (NA, :neither)
    end
end

function ifpresent(arr, n::Integer=1)
    if length(arr)==n
        return arr[n]
    else
        return NA
    end
end

nproc = 0
timeelapsed = @elapsed for i=1:maxev
    nproc += 1
    to!(events, i)

    df[i, :passes] = false

    df[i, :run], df[i, :lumi], df[i, :event] = where(events)
    df[i, :fileindex] = where_file(events)
    

    df[i, :lepton_pt], which_lepton = either(events[sources[:muon_Pt]], events[sources[:electron_Pt]])

    lepton_type = :neither
    if which_lepton == :first
        lepton_type = :muon
    elseif which_lepton == :second
        lepton_type = :electron
    end

    df[i, :lepton_type] = string(lepton_type)

    if which_lepton == :neither
        continue
    end

    df[i, :lepton_id] = events[sources[part(lepton_type, :genPdgId)]][1]


    df[i, :bjet_pt] = events[sources[:bjet_Pt]] |> ifpresent
    df[i, :bjet_eta] = events[sources[:bjet_Eta]] |> ifpresent
    #df[i, :bjet_phi] = events[sources[:bjet_Phi]]
    df[i, :bjet_id] = events[sources[:bjet_partonFlavour]] |> ifpresent

    df[i, :ljet_pt] = events[sources[:ljet_Pt]] |> ifpresent
    df[i, :ljet_eta] = events[sources[:ljet_Eta]] |> ifpresent
    #df[i, :ljet_phi] = events[sources[:ljet_Phi]]
    df[i, :ljet_id] = events[sources[:ljet_partonFlavour]] |> ifpresent

    df[i, :passes] = true

end

println("processed $(nproc/timeelapsed) events/second")
df = df[with(df, :(passes)), :]
writetable("output.csv", df)
writetable("processed.csv", processed_files)

# using HDF5
# using JLD
# file = jldopen("output.jld", "w")
# write(file, "df", df)
# write(file, "processed_files", processed_files)
# close(file)