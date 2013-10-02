addprocs(20)

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
            {Int32, Int32, Int32, Int32, Int32},
            ["event_index", "file_index", "run", "lumi", "event"], maxev
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
            return false
        end

        return true
    end
end #everywhere

println("Processing $maxev events on workers ", join(workers(), ", "))
n, refs = process_parallel(loopfn, :ev, workers())

elps = @elapsed for r in refs
    wait(r)
end

dfs = DataFrame[]
for w in workers()
    push!(dfs, @fetchfrom w eval(:(
        head(hcat([df[2] for df in dataframes]...), n_processed)
    )))
end
df = vcat(dfs...)
save("output.jld", df)
writetable("output.csv", df)
speed = n/elps
println("Processed $speed events/second")
show(df)
