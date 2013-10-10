module SkimUtil

using DataFrames
import DataFrames.AbstractDataStream
using HDF5
using JLD

function readjld(fi, dname="stpol_events")
    tmp = tempname()
    run(`gzip -cd $fi` |> open(tmp, "w")) 
    f = jldopen(tmp, "r")
    d = read(f, dname)
    close(f)
    run(`rm -f $tmp`)
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


type MultiFileDataStream <: AbstractDataStream
    flist::Vector{ASCIIString}
    index::Int64 
end

function Base.start(s::MultiFileDataStream)
    s.index = 1
    return DataFrame()
end

function Base.next(s::MultiFileDataStream, df::DataFrame)
    df2 = readjld(s.flist[s.index])
    s.index += 1
    return df2, df
end

function Base.done(s::MultiFileDataStream, df::DataFrame)
    return s.index > length(s.flist)
end

end #module
