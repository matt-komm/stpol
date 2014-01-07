include("../analysis/base.jl")
using ROOT

fn = ARGS[1]
of = ARGS[2]

println("reading input file $fn")

tic()
df = readtree(fn;progress=true)
toc()

println("saving output file $of")

tic()
write(jldopen(of, "w"), "df", df)
toc()

