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

function save_df(fn::ASCIIString, df::AbstractDataFrame)
    fi = jldopen(fn, "w")
    write(fi, "data", df)
    close(fi)
    run(`gzip -9 $fn`)
end

# infiles = readall(`find /Users/joosep/Documents/stpol/data/tchan -name "*.csv.gz"`) |> split
# #infiles = filter(x -> endswith(x, ".gz"), ARGS)
# el1 = @elapsed df = open_multi(infiles)
# println("opened data frame: $(size(df)) in $el1 seconds")

# el2 = @elapsed save_df("tchan.jld", df)
# println("saved DataFrame in $el2 seconds")

