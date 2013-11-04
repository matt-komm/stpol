#julia skim.jl ofile infiles.txt
#runs a skim/event loop on EDM files on a single core
tstart = time()

println("hostname $(gethostname())")
using ROOT
using DataFrames
using HDF5
using JLD

include("xs.jl")
include("util.jl")

output_file = ARGS[1]

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

maxev = 5*length(events) 
println("running over $maxev events")

#metadata
processed_files = DataFrame(files=flist)

#events
df = similar(
    DataFrame(pt=Float32[], eta=Float32[], id=Int32[], bdisc=Float32[]),
    maxev
)

const sources = Dict{Symbol, Source}()

#jets
for s in [:Pt, :Eta, :Phi, :Mass, :partonFlavour, :bDiscriminatorCSV, :bDiscriminatorTCHP, :rms, :deltaR]
    sources[part(:jets, s)] = Source(:goodJetsNTupleProducer, s, :STPOLSEL2)
end

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
j = 0
timeelapsed = @elapsed for i=1:length(events)
    nproc += 1

    if nproc%(ceil(maxev/20)) == 0
        println("$nproc ($(ceil(nproc/maxev*100.0))%) events processed")
        toc()
        tic()
    end
    to!(events, i)
    

    for (pt, eta, id, bdisc) in zip(
        events[sources[part(:jets, :Pt)]],
        events[sources[part(:jets, :Eta)]],
        events[sources[part(:jets, :partonFlavour)]], 
        events[sources[part(:jets, :bDiscriminatorCSV)]]
        )
        isna(pt) && continue
        j += 1
        df[j, :pt] = pt
        df[j, :eta] = eta
        df[j, :id] = id 
        df[j, :bdisc] = bdisc
    end

end

println("processed $(nproc/timeelapsed) events/second")


#Select only the events that actually pass
mydf = df[1:j, :]
println(nrow(mydf))
describe(mydf)

#save output
writetable("$(output_file)_processed.csv", prfiles)
writetree("$(output_file).root", mydf)

tend = time()
ttot = tend-tstart
println("total script time $ttot seconds")
