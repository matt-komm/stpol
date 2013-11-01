inf = split(readall(`head -n5 input/iso_csvt.txt`))
flist = join(inf, " ")
exe=joinpath(ENV["HOME"], ".julia/ROOT/julia")
run(`$exe skim.jl test $flist`)
