#!/home/joosep/.julia/ROOT/julia
include("$(homedir())/.juliarc.jl")
using DataFrames, JSON

include("../analysis/base.jl")

fname = ARGS[1]
ofile = ARGS[2]
infile = ARGS[3]
infiles = readall(infile)|>split

flist = split(readall(fname))
@assert length(flist)>0 "no files specified"

println("Running over $(length(flist)) files")

n = 0
res = Dict()
for fi in flist
    acc = accompanying(fi)
    md = readtable(acc["processed"], allowcomments=true)
    
    println(fi," ", acc["processed"])

    for i=1:nrow(md)
        f = md[i, :files]
        
        f in infiles || error("unrecognized file $f, not in $infile")
        splice!(infiles, findfirst(infiles, f))

        st = sample_type(f)
        #println("$f $st")
        sample, iso, systematic = st[:sample], st[:iso], st[:systematic]
        k = "$(sample)/$(iso)/$(systematic)"
        if !haskey(res, k)
            res[k] = 0
            res["$(k)/counters/generated"] = 0
        end 
        res[k] += 1
        res["$(k)/counters/generated"] += md[i, :total_processed]
        #println("\t$k $(md[i, :total_processed])") 
    end
end

length(infiles)==0 || error("incomplete processing: \n$infiles")


of = open(ofile, "w")
write(of, json(res))
close(of)

#for (k,v) in sort(collect(res), by=x->x[1])
#    println(k, " ", v)
#end
