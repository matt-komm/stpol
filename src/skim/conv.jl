include("../analysis/base.jl")
using ROOT

fn = ARGS[1]
of = ARGS[2]

println("reading input file $fn")

#Profile.init(10^10, 0.0001)

tic()
df = readtree(fn;progress=true)
toc()

#Profile.print(open("prof.txt", "w"); format=:flat, C=true, cols=80)

println("saving output file $of")

tic()
write(jldopen(of, "w"), "df", df)
toc()

