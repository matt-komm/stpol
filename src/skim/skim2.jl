using DataFrames
require(joinpath(ENV["HOME"], ".juliarc.jl"))
require("util.jl")
findex = readtable("findex.csv")

symb = symbol(ARGS[1])
flist = findex[:($symb .== true), :fname]

mf = SkimUtil.MultiFileDataStream(flist)
tic()

ntot = 0

dfs = Dict()

dfs[symb] = similar(DataFrame(
    bjet_id=Int32[], met=Float32[], bjet_bd_a=Float32[], bjet_bd_b=Float32[], cos_theta=Float32[]
    ), 50000000
)


n = 0
for m in mf
    ntot += nrow(m)
    for i=1:nrow(m)
        cls = SkimUtil.classify(m[i, :fname])
        if symb in cls && :iso in cls
            n += 1
            for cn in colnames(dfs[symb])
                dfs[symb][n, cn] = m[i, cn]
            end
        end
    end
end
dfs[symb] = dfs[symb][1:n, :]
toc()
println("ntot = $ntot")
writetable("$(symb).csv", dfs[symb])
describe(dfs[symb])
