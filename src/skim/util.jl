using DataFrames
using HDF5
using JLD

function readjld(fi)
    tmp = tempname()
    run(`gzip -cd $fi` |> open(tmp, "w")) 
    f = jldopen(tmp, "r")
    d = read(f, "data")
    close(f)
    assert(typeof(d)==DataFrame) 
    return d
end

function open_multi(files)
    tables = DataFrame[]
    for fi in files
        try
            table = Void
            if endswith(fi, ".csv.gz")
                table = readtable(fi)
            elseif endswith(fi, ".jld.gz")
                table = readjld(fi)
            else
                error("unknown file format: $fi")
            end
            println("Opened: $fi: $(size(table))")
            push!(tables, table)
        catch e
            warn("could not read $fi: $e")
            continue
        end
    end
    
    df = rbind(tables)
    return df
end

infiles = readall(`find tchan -name "*.jld.gz"`) |> split
#infiles = filter(x -> endswith(x, ".gz"), ARGS)
df = open_multi(infiles)
println("Opened data frame: $(size(df))")

