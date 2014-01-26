of = ARGS[1]
dfs = ARGS[2:length(ARGS)]

addprocs(24)

@everywhere resd = Dict()
@everywhere include(joinpath(ENV["HOME"], ".juliarc.jl"))
@everywhere include("evloop.jl")

include("util.jl")

tic()
println("mapping")
pmap(process_file, dfs)
println("done mapping")
toc()

tic()
println("reducing on workers")
@everywhere res=sum(collect(values(resd)))
toc()

println("fetching from workers, summing")
tic()
lres = sum([remotecall_fetch(w, ()->res) for w in workers()])
toc()

tic()
println("writing output with $(length(lres)) objects")
f = jldopen(of, "w")
write(f, "res", lres)
close(f)
toc()
