include("../analysis/basedir.jl")
include("xs.jl")

infile = ARGS[1]

d = Dict()
for inf in split(readall(infile))
    st = sample_type(inf)
    p = "$infile/$(st[:tag])/$(st[:iso])/$(st[:systematic])/$(st[:sample])"
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
