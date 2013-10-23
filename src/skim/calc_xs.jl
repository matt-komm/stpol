#julia calc_xs.jl dir > output
using JSON

indir = ARGS[1]
ispath(indir) || error("input directory $indir is not valid")

include("xs.jl")

flist = split(readall(`find $indir -name "*processed*.csv"`))
xs = xsweight(flist)
println(json(xs))
