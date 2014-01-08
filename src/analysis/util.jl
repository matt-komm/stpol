
import Base.+
    
function accompanying(fn)
    #get all the files in the directory containing this file
    files = readdir(dirname(fn))
    
    #get the name without the extension
    bn = split(basename(fn), ".")[1]
    
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
    
function +(d1::Dict{Any, Any}, d2::Dict{Any, Any})

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

function issame(arr::Vector{Any})
    f = first(arr)
    for x in arr
        if x!= f
            return false
        end
    end
    return true
end

#outputs <: AbstractVector{Associative{Any, Histogram}}
function merge_outputs(outputs)
    output = Dict()
    for o in outputs
        for (k, v) in o
            if k in keys(output)
                output[k] += v
            else
                output[k] = v
            end
        end
    end
    return output
end
