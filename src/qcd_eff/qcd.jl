#addprocs(4)

@everywhere begin

    using ROOT
    using DataFrames

    include("stpol.jl")
    using SingleTop

    files = {
        :aiso => "/Users/joosep/Documents/stpol/data/qcd_aiso.txt",
        :iso => "/Users/joosep/Documents/stpol/data/qcd_iso.txt"
    }

    el = @elapsed ev = Events(
        convert(
            Vector{ASCIIString},
            [
                split(open(readall, fname)) for (key, fname) in files
            ]
        )
    )

    println("Opened $(length(files)) files in $el seconds.")
    maxev = length(ev)

    muon = DataFrame(
        {Float64,Float64},
        ["mu_pt", "mu_iso"],
        maxev
    )

    event_ids = DataFrame(
        {Int64, Int64, Int64, Int64, Int64},
        ["event_index", "file_index", "run", "lumi", "event"], maxev
    )

    frames = [muon, event_ids]

    n_processed = 0

    function get(events::Events, obj)
        rets = Dict{Symbol, Any}()
        for name in names(obj)
            x = events[getfield(obj, name)]
            x = length(x)==1 ? x[1] : NA
            rets[name] = x
        end
        return rets
    end 

    function loopfn(i::Integer, events::Events)

        global n_processed::Int64
        n_processed += 1

        event_ids[n_processed, "event_index"] = i

        to!(events, i)

        mu = get(events, SingleTop.signal_mu)
        muon[n_processed, "mu_pt"] = mu[:pt]
        muon[n_processed, "mu_iso"] = mu[:iso]

        event_ids[n_processed, "file_index"] = where_file(events)
        event_ids[n_processed, "run"], event_ids[n_processed, "lumi"], event_ids[n_processed, "event"] = where(events)
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
        head(hcat(muon, event_ids), n_processed)
    )))
end
df = vcat(dfs...)
#println(dfs)
#dfs = {:iso => df[:(evn .<=15), :], :uniso => df[:(evn .>15), :]}

using Stats

describe(df["mu_pt"])

speed = n/elps
println("Processed $speed events/second")