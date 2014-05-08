#!/usr/bin/env julia
inf = split(readall("input/tchan.test.txt"))
flist = join(inf, " ")
exe=joinpath(ENV["HOME"], ".julia/CMSSW/julia")
run(`$exe skim.jl test $flist`)
