import Base.append!, Base.getindex
import DataFrames.nrow

function with(df::AbstractDataFrame, ex::Expr)
    # By-column operation with the columns of a DataFrame.
    # Returns the result of evaluating ex.

    # helper function to replace symbols in ex with a reference to the
    # appropriate column in df
    replace_symbols(x, syms::Dict) = x
    replace_symbols(e::Expr, syms::Dict) = Expr(e.head, (isempty(e.args) ? e.args : map(x -> replace_symbols(x, syms), e.args))...)
    function replace_symbols(s::Symbol, syms::Dict)
        if (string(s) in keys(syms))
            :(_DF[$(syms[string(s)])])
        else
            s
        end
    end
    # Make a dict of colnames and column positions
    cn_dict = Dict(names(df), [1:ncol(df)])
    ex = replace_symbols(ex, cn_dict)
    f = @eval (_DF) -> $ex
    ret = f(df)
    return ret
end

with(df::AbstractDataFrame, s::Symbol) = df[string(s)]

#creates an interface which allows column-wise access to separate dataframes containing the same rows,
#but different columns
immutable MultiColumnDataFrame{T <: AbstractDataFrame} <: AbstractDataFrame
    dfs::Vector{T}
    index::DataFrames.Index
end

function MultiColumnDataFrame{T<:AbstractDataFrame}(dfs::AbstractVector{T})
    d = Dict{Symbol,Union(AbstractArray{Real,1},Real)}()
    ns = Symbol[]
    nr = nrow(dfs[1])
    for i=1:length(dfs)
        dfs[i]::T
        if nrow(dfs[i]) != nr
            error("rows are not equal: ", join(map(nrow, dfs), ", "))
        end

        for name in names(dfs[i])
            !(name in ns) || error("$name already defined")
            d[name] = i
            push!(ns, name)
        end
    end
    
    MultiColumnDataFrame{T}(
        T[df for df in dfs],
        DataFrames.Index(d, ns)
    )
end

Base.getindex{T <: Real, K <: Symbol}(df::MultiColumnDataFrame, r::T, c::K) = df.dfs[df.index[c]][r, c]
Base.getindex{K <: Symbol}(df::MultiColumnDataFrame, c::K) = df.dfs[df.index[c]][c]
DataFrames.nrow(df::MultiColumnDataFrame) = nrow(df.dfs[1])

export MultiColumnDataFrame
