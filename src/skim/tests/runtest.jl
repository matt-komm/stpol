#!/usr/bin/env julia
inf = split(readall("input/tchan.test.txt"))
flist = join(inf, " ")
exe=joinpath(ENV["HOME"], ".julia/ROOT/julia")
run(`$exe skim.jl test $flist`)
