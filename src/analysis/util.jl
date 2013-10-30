
import Base.+
    
function accompanying(fn)
    files = readdir(dirname(fn))
    bn = split(basename(fn), ".")[1]
    
    out = Dict()
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
