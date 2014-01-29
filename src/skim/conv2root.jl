#!/home/joosep/.julia/ROOT/julia
include("../analysis/base.jl")
using ROOT

fn = ARGS[1]
of = ARGS[2]

println("reading input file $fn")

df = read(jldopen(fn, "r";mmaparrays=true), "df")

println("saving output file $of")

writetree(of, df)

