using CMSSW
import CMSSW.writetree

function accompanying(fn)
    #get all the files in the directory containing this file
    files = readdir(dirname(fn))
    
    #get the name without the extension
    bn = splitext(basename(fn))[1]
    
    out = Dict()
    out["df"] = fn
    for fi in files
        reg = Regex(".*$(bn)_(.*).csv")
        m = match(reg, fi)
        m == nothing && continue
        out[m.captures[1]] = joinpath(dirname(fn), fi)
    end
    return out
end
   
import Base.+ 
function +(d1::Associative, d2::Associative)

    k1 = Set([x for x in keys(d1)]...)
    k2 = Set([x for x in keys(d2)]...)

    common = intersect(k1, k2)

    ret = Dict()
    for k in common
        ret[k] = d1[k] + d2[k]
    end

    #in d1
    for k in [x for x in setdiff(k1, k2)]
        if !haskey(d2, k)
            ret[k] = d1[k]
        end
    end

    #in d2
    for k in [x for x in setdiff(k2, k1)]
        if !haskey(d1, k)
            ret[k] = d2[k]
        end
    end

    return ret
end

function writetree_temp(outfile, df::DataFrame)
    tempf = mktemp()[1]
    print("writing to $tempf...");CMSSW.writetree(tempf, df);println("done")
    
    for i=1:5
        try
            println("cleaning $outfile...");isfile(outfile) && rm(outfile)
            println("copying...");cp(tempf, outfile)
            s = stat(outfile)
            s.size == 0 && error("file corrupted")
            break
        catch err
            warn("$err: retrying after sleep")
            sleep(5)
        end
    end
end

export accompanying
export writetree_temp
