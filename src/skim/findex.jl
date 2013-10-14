require(joinpath(ENV["HOME"], ".juliarc.jl"))
require("util.jl")

using DataFrames
using HDF5
using JLD

flist = readall("done") |> split

findex = similar(
    DataFrame(qcd=Bool[], tchan=Bool[], wjets=Bool[], ttbar=Bool[], fname=ASCIIString[]),
    length(flist)
)
n = 0
tic()
for fn in flist
    n+=1
    #println(fn)
    fi = jldopen(fn)
    processed_files = read(fi, "processed_files")
    close(fi)

    for x in [:tchan, :wjets, :ttbar, :qcd]
        findex[n, x] = false
    end

    for fname in processed_files
        cls = SkimUtil.classify(fname)
        for x in [:tchan, :wjets, :ttbar, :qcd]
            if x in cls
                findex[n, x] = true
            end
        end
    end
    findex[n, :fname] = fn
    df = 0
end
writetable("findex.csv", findex)
toc()

for x in [:tchan, :wjets, :ttbar, :qcd]
    println(x)
    println(join(findex[:($x .== true), :fname], "\n"))
end
