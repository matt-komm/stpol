#!/home/joosep/.julia/ROOT/julia
addprocs(4)

const INFILE = ARGS[1]
const OUTFILE = ARGS[2]


#MAP
@eval @everywhere const INFILE=$(INFILE)
@eval @everywhere const OUTFILE=$(OUTFILE)

@everywhere using ROOT, DataFrames

@everywhere include("../analysis/base.jl")
@everywhere include("$BASE/src/analysis/selection.jl")

df = TreeDataFrame(INFILE)
const NROW = nrow(df)
#const NROW = 2000000

#distribute chunks across workers
wks = setdiff(workers(), myid())
cks = chunks(int(NROW/(length(wks)))+1, NROW)
@assert(length(wks)==length(cks), "incorrect number of chunks")
for (w, c) in zip(wks, cks)
    @spawnat w eval(:(const CHUNK=$c))
end

tic()

@everywhere begin

function perfsel(_chunk)
    println("loopin over chunk ", _chunk.start, ":", [_chunk][length(_chunk)-1])
    df = TreeDataFrame(INFILE)
    println("opened TreeDataFrame ", ARGS[1], " with ", nrow(df), " events")
    tic()

    arr(c) = BitArray(length(c))

    set_branch_status!(df.tree, "*", false)
    reset_cache!(df.tree)

    #only these branches are read from the TTree
    brs = [
        :sample, :njets, :ntags,
        :lepton_type, :systematic, :isolation,
        :n_signal_mu, :n_signal_ele, :n_veto_mu,
        :n_veto_ele,
        :mtw, :met,
        :ljet_dr, :bjet_dr, :hlt_mu, :hlt_ele, :ljet_rms
    ]

    for b in brs
        set_branch_status!(df.tree, "$(b)*", true)
        add_cache!(df.tree, "$(b)*")
    end

    loutput = Dict()
    loutput[(:chunk,)] = _chunk

    for (k, v) in flatsel
        loutput[k] = arr(_chunk)
    end
    println("performing ", length(loutput), " selections over ", length(_chunk), " events")

    j=1
    sdf = df[_chunk, brs]
    for (k, v) in flatsel
        ba = with(sdf, v)
        for i=1:length(loutput[k])
            loutput[k][i] = isna(ba[i]) ? false : ba[i]
        end
    end

    return loutput
end

end #everywhere

refs = [@spawnat(w, eval(Main, :(perfsel(CHUNK)))) for w in wks]
outputs = [fetch(r) for r in refs]
output = Dict()
for k in keys(outputs[1])
    output[k] = vcat([o[k] for o in outputs]...)
end
el = toq()
println("processed $(NROW/el) events/second in $el seconds")
@assert(length(output[(:chunk, )]) == NROW, "failed to process some chunks")
println("writing output")
tic()
write(jldopen(OUTFILE, "w"), "inds", output)
toc()
