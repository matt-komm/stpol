#!/home/joosep/.julia/ROOT/julia
include("../analysis/base.jl")
using ROOT

fn = ARGS[1]
of = ARGS[2]

println("reading input file $fn")

df = readtree(fn;progress=true)

println("saving output file $of")

write(jldopen(of, "w"), "df", df)

