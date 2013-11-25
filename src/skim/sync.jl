#!/home/joosep/.julia/ROOT/julia
tstart = time()
println("hostname $(gethostname())")

using ROOT

inf = ARGS[1:]
events = Events(convert(Vector{ASCIIString}, inf))

maxev = length(events) 
println("running over $maxev events")

#Loop over the events
println("Beginning event loop")
nproc = 0

include("stpol.jl")

tots = Dict()
tots[:hlt] = 0
tots[:mu] = 0
tots[:ele] = 0
tots[:muele] = 0
tots[:nomuele] = 0

tic()
timeelapsed = @elapsed for i=1:maxev
    to!(events, i)
    nproc += 1

    hlt = passes_hlt(events, hlts)
    if (hlt) tots[:hlt] += 1 end
    nmu = events[sources[:nsignalmu]]
    nele = events[sources[:nsignalele]]
    njets = events[sources[:njets]]
    ntags = events[sources[:ntags]]
    println("hlt=$hlt nmu=$nmu nele=$nele nj=$njets nt=$ntags")
    
    if (isna(nmu) || isna(nele))
        tots[:nomuele] += 1
        continue
    end
    if (nmu==0 && nele==1) tots[:ele] += 1 end
    if (nmu==1 && nele==0) tots[:mu] += 1 end
    if (nmu==1 && nele==1) tots[:muele] += 1 end

end

println("processed $(nproc/timeelapsed) events/second")

tend = time()
ttot = tend-tstart
println("total script time $ttot seconds")
println(tots)
