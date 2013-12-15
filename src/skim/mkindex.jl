#!/home/joosep/.julia/ROOT/julia
using ROOT,DataFrames

include("../analysis/base.jl")
include("$BASE/src/analysis/selection.jl")

df = TreeDataFrame(ARGS[1])
println("opened TreeDataFrame ", ARGS[1], " with ", nrow(df), " events")
tic()

arr() = BitArray(nrow(df))

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

output = Dict()
for (k, v) in flatsel
    output[k] = arr()
end
println("performing ", length(output), " selections")

for i=1:2
    if i%100000 == 0
        print(".")
        flush_cstdio()
    end
    if i%1000000 == 0
        print("|")
        flush_cstdio()
    end

    x = df[i:i, brs]
    for (k::Any, v::Expr) in flatsel
        n = nrow(select(v, x))
        output[k][i] = (n == 1)
    end
    # for b in brs
    #     sb = symbol(string(":", b))
    #     ex = :($b = df[$i, $sb])
    #     println(ex)
    #     println(df[i, :sample])
    #     #eval(ex)
    # end
end
el = toq()

println("processed ", nrow(df)/el, " events/second")

for (k, v) in output
    println(join(k, "->"), " ", sum(v))
end
write(jldopen(ARGS[2], "w"), "inds", output)
