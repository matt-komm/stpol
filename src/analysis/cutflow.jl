using ROOT
using DataFrames

flists = Dict{Any, Any}() 

llists[:data] = (readall("data.txt") |> split)

function file_type(fn)
    endswith(fn, ".root") ? (return :events) :
    endswith(fn, "processed.csv") ? (return :metadata) :
    return nothing
end

for fi in flists[:data]
    ft = file_type(fi)
    if ft == :events
        df = TreeDataFrame(fi)
        println(nrow(df))
    end
end
