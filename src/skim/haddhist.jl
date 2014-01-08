#!/usr/bin/env julia
include("../analysis/base.jl")
include("$BASE/src/fraction_fit/hists.jl")
include("../analysis/util.jl");

outfile = ARGS[1]
infiles = ARGS[2:]
println(join(infiles, ","))

output = Dict()
for inf in infiles
    tic()
    o = read(jldopen(inf, "r"), "hists")
    println(inf, " ", length(o))
    for (k, v) in o
        if k in keys(output)
            output[k] += v
        else
            output[k] = v
        end
    end
    toc()
end

println("writing output")
write(jldopen(outfile, "w"), "hists", output)
