include("../analysis/basedir.jl")
include("xs.jl")

#list of all input files, good if sorted
#created with `find crabs -name "*.files.txt" >> in`, prefixed with file:/hdfs/cms/
infile = ARGS[1]

#prefix for running, typically `step3`
path = ARGS[2]

d = Dict()
for inf in split(readall(infile))
    st = sample_type(inf)
    p = "$path/$(st[:tag])/$(st[:iso])/$(st[:systematic])/$(st[:sample])"
    #println(p) 
    if !haskey(d, p)
        d[p] = Any[]
    end
    push!(d[p], inf)
end

of = open("out.txt", "w")
for (k, v) in d
    write(of, "[$k]\n")
    for x in v
        write(of, "$x = 1\n")
    end
end
close(of)
