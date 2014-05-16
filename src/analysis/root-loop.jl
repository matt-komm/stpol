using ROOT, DataFrames
import Base.length, Base.getindex

import DataFrames.nrow, DataFrames.size

immutable TreeDataFrame <: AbstractDataFrame
    tf::TFile
    tt::TTree
    bvars::Vector{Any}
    index::DataFrames.Index
    types::Vector{Type}
end

function TreeDataFrame(fn::ASCIIString)
    tf = TFile(fn)
    tt = root_cast(TTree, Get(root_cast(ROOT.TDirectory, tf), "dataframe"))

    brs = GetListOfBranches(tt);
    brs = [root_cast(TBranch, brs[i]) for i=1:length(brs)];
    
    bd = Dict()
    bd_isna = Dict()
    for b in brs
        bn = GetName(root_cast(TObject, b))|>bytestring;
        if contains(bn, "ISNA")
            bd_isna[join(split(bn, "_")[1:end-1], "_")] = b
        else
            bd[bn] = b
        end
    end

    bridx = 1
    bvars = Any[]
    bidx = Dict{Symbol,Union(Real,AbstractArray{Real,1})}()
    types = Type[]
    for k in keys(bd)
        leaves = GetListOfLeaves(bd[k])
        length(leaves)==1 || error("$k, Nleaf=$(length(leaves))")
        leaf = root_cast(TLeaf, leaves[1])
        t = GetTypeName(leaf)|>bytestring|>parse
        t = eval(ROOT.type_replacement[t])::Type
        push!(types, t)
        
        bvar = (t[0.0], Bool[true]);
        push!(bvars, bvar)
        
        br = GetBranch(tt, k)
        SetAddress(br, convert(Ptr{Void}, bvar[1]))
        br = GetBranch(tt, "$(k)_ISNA")
        SetAddress(br, convert(Ptr{Void}, bvar[2]))
        
        bidx[symbol(k)] = bridx

        bridx += 1
    end

    idx = DataFrames.Index(bidx, collect(keys(bidx)))
    
    TreeDataFrame(tf, tt, bvars, idx, types)
end

Base.length(t::TreeDataFrame) = GetEntries(t.tt)
Base.size(df::TreeDataFrame) = (nrow(df), ncol(df))
Base.size(df::TreeDataFrame, n) = size(df)[n]

#df = TreeDataFrame(string(ENV["HOME"], "/Dropbox/kbfi/top/stpol/results/skims/feb27.root"))
function Base.getindex(df::TreeDataFrame, i::Int64, s::Symbol, get_entry=false)
    get_entry && GetEntry(df.tt, i)
    v, na = df.bvars[df.index[s]]
    return na[1] ? NA : v[1]
end

import DataFrames.nrow, DataFrames.ncol
DataFrames.nrow(df::TreeDataFrame) = length(df)
DataFrames.ncol(df::TreeDataFrame) = length(df.bvars)

import Base.names
Base.names(x::TreeDataFrame) = names(x.index)

function Base.getindex(df::TreeDataFrame, i::Int64)
    da = DataVector(df.types[i], nrow(df))
    ns = names(df.index)
    name = ns[i]
    enable_branches(df, ["$(name)*"])
    for n=1:nrow(df)
        GetEntry(df.tt, n)
        da[n] = df[n, name]
    end
    return da
end

set_branch_status!(df, pat, status) = SetBranchStatus(
    df.tt, pat, status, convert(Ptr{Uint32}, 0)
)

function enable_branches(df, brs)
    SetCacheSize(df.tt, 0)
    SetCacheSize(df.tt, 100000000)
    set_branch_status!(df, "*", false)
    for b in brs
        set_branch_status!(df, "$b", true)
        AddBranchToCache(df.tt, "$b")
    end
end

function Base.getindex(df::TreeDataFrame, s::Symbol)
    enable_branches(df, ["$(s)*"])
    ret = DataArray(df.types[df.index[s]], nrow(df))
    for i=1:nrow(df)
        GetEntry(i)
        ret[i] = df[i, s]
    end
    return ret
end
