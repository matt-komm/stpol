module SkimUtil

using DataFrames
import DataFrames.AbstractDataStream
using HDF5
using JLD

unzname(fi) = "$fi.temp"
function readjld(fi, dname="stpol_events")
    #tmp = tempname()
    if endswith(fi, ".jld.gz")
        tmp = unzname(fi)
        println("unzipping to $tmp")
        run(`gzip -cd $fi` |> open(tmp, "w"))
    else
        println("opening $fi directly")
        tmp = fi
    end
    f = jldopen(tmp, "r", mmaparrays=true)
    d = read(f, dname)
    #close(f)
    #run(`rm -f $tmp`)
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
            elseif contains(fi, ".jld")
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

function MultiFileDataStream(arr)
    return MultiFileDataStream([ascii(string(a)) for a in arr], 1)
end

function Base.start(s::MultiFileDataStream)
    s.index = 1
    return DataFrame()
end

function Base.next(s::MultiFileDataStream, df::DataFrame)

    fn = s.flist[s.index]
    df2 = None
    if contains(fn, ".jld")
        df2 = readjld(fn)
    elseif contains(fn, ".csv")
        df2 = readtable(fn)
    else
        error("unknown format: $fn")
    end
    s.index += 1

    return df2, df
end

function Base.done(s::MultiFileDataStream, df::DataFrame)
    return s.index > length(s.flist)
end

function Base.length(s::MultiFileDataStream)
    return length(s.flist)
end

function Base.getindex(s::MultiFileDataStream, i::Int64)
    return MultiFileDataStream(s.flist[i:i], 1)
end

function Base.getindex(s::MultiFileDataStream, r::Range1{Int64})
    return MultiFileDataStream(s.flist[r], 1)
end

function classify(fname)
    identifiers = Symbol[]
    if contains(fname, "/iso/")
        push!(identifiers, :iso)
    end
    if contains(fname, "/antiiso/")
        push!(identifiers, :aiso)
    end
    if contains(fname, "/nominal/")
        push!(identifiers, :nominal)
    end
    if match(r".*/QCD.*/.*", fname)!=nothing
        push!(identifiers, :qcd)
    end    
    if match(r".*/T_t_ToLeptons/.*", fname)!=nothing
        push!(identifiers, :tchan)
        push!(identifiers, :top)
    end
    if match(r".*/Tbar_t_ToLeptons/.*", fname)!=nothing 
        push!(identifiers, :tchan)
        push!(identifiers, :atop)
    end
    if match(r".*/TTJets_FullLept/.*", fname)!=nothing 
        push!(identifiers, :ttbar)
        push!(identifiers, :flept)
    end
    if match(r".*/TTJets_SemiLept/.*", fname)!=nothing 
        push!(identifiers, :ttbar)
        push!(identifiers, :slept)
    end
    if match(r".*/W[1-4]Jets_exclusive/.*", fname)!=nothing
        push!(identifiers, :wjets)
    end
    return identifiers
end

end #module
