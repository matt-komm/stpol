#!/home/joosep/.julia/ROOT/julia
include("$(homedir())/.juliarc.jl")
using DataFrames, JSON

include("../analysis/base.jl")

fname = ARGS[1]
ofile = ARGS[2]
infile = ARGS[3]
infiles = sort(map(x -> convert(ASCIIString, strip(x)), readall(infile)|>split))|>collect
processed = ASCIIString[]

flist = sort(map(
    x -> convert(ASCIIString, strip(x)),
    split(readall(fname))
))|>collect

@assert length(flist)>0 "no files specified"

println("Running over $(length(flist)) files")

n = 0
res = Dict()

processed2 = ASCIIString[]
for fi in flist
    fi in processed2 && error("double processing of $fi")
    push!(processed2, fi)

    acc = accompanying(fi)
    md = nothing

    println(fi," ", acc["processed"])
    try
        md = readtable(acc["processed"], allowcomments=true)
    catch err
        warn("could not read table with processed=$(acc["processed"])")
        continue 
    end

    for i=1:nrow(md)
        f = convert(ASCIIString, strip(md[i, :files]))
        
        #idx = searchsortedfirst(infiles, f)
        #if !in(f, infiles)
        #    println("unrecognized file $f, not in $infile")
        #    error("unrecognized file $f, not in $infile")
        #    continue
        #end
        f in processed && warn("double processing of $f")
        push!(processed, f)

        st = sample_type(f)
        #println("$f $st")
        tag, sample, iso, systematic = st[:tag], st[:sample], st[:iso], st[:systematic]
        k = "$(tag)/$(sample)/$(iso)/$(systematic)"
        if !haskey(res, k)
            res[k] = 0
            res["$(k)/counters/generated"] = 0
        end 
        res[k] += 1
        res["$(k)/counters/generated"] += md[i, :total_processed]
        #println("\t$k $(md[i, :total_processed])") 
    end
end

processed = sort(processed)|>collect

((length(infiles) == length(processed)) && (infiles .== processed)) ||
    warn("incomplete processing, some files in input file but not in root")

of = open(ofile, "w")
write(of, json(res))
close(of)

