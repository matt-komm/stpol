@everywhere using ROOT
@everywhere using DataFrames

require("stpol.jl")
@everywhere using SingleTop

@everywhere begin
    files = {
        :tchan => "tchan.txt"
        #:aiso => "/Users/joosep/Documents/stpol/data/qcd_aiso.txt",
        #:iso => "/Users/joosep/Documents/stpol/data/qcd_iso.txt"
    }

    flist = Any[]
    for (k, fname) in collect(files)
        append!(flist, split(open(readall, fname)))
    end

    el = @elapsed ev = Events(convert(Vector{ASCIIString}, flist))

    println("Opened $(length(flist)) files in $el seconds.")
    maxev = length(ev)

    dataframes = {
        :signal_muon => similar(SingleTopData.to_df(SingleTopData.Lepton[]), maxev),
        :events => DataFrame(
            {Int32, Int32, Int32, Int32, Int32, Bool},
            ["event_index", "file_index", "run", "lumi", "event", "passes"], maxev
        )
    }

    n_processed = 0

    function loopfn(i::Integer, events::Events)

        global n_processed::Int64
        n_processed += 1

        dataframes[:events][n_processed, "event_index"] = i

        to!(events, i)

        dataframes[:events][n_processed, "file_index"] = where_file(events)
        dataframes[:events][n_processed, "run"], dataframes[:events][n_processed, "lumi"], dataframes[:events][n_processed, "event"] = where(events)

        muons = SingleTop.get_particles(events, :signal_muon)
        if length(muons)==1
            dataframes[:signal_muon][n_processed, :] = SingleTopData.to_df(muons[1])
        else
            dataframes[:events][n_processed, "passes"] = false
            return false
        end

        dataframes[:events][n_processed, "passes"] = true
        return true
    end
end #everywhere

println("Processing $maxev events on workers ", join(workers(), ", "))
n, refs = process_parallel(loopfn, :ev, workers())

elps = @elapsed for r in refs
    wait(r)
end
println("Processed $(maxev/elps) events/second")
dfs = Any[]
for w in workers()
    push!(dfs, @fetchfrom w eval(:(
        {s => head(df, n_processed) for (s, df) in dataframes}
    )))
end

using HDF5
using JLD

file = jldopen("output.jld", "w")
df = {s => vcat([df[s] for df in dfs]...) for (s) in keys(dfs[1])} 
for (k, v) in df
    #write(file, string(k), v)
    writetable("output_$(k).csv", v)
end
close(file)
#show(df)
