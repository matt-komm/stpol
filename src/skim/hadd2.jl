using DataArrays, DataFrames, HDF5, JLD

of = ARGS[1]
inf = ARGS[2:]

function readdf(fn)
    fi = jldopen(fn, "r"; mmaparrays=false)
    df = deepcopy(read(fi, "df"))
    close(fi)
    return df
end

tic()
println("reading $(length(inf)) datasets")
dfs = [readdf(f) for f in inf]
toc()

function frbind(dfs)
    totl = sum([nrow(df) for df in dfs])
    println("creating dataframe with $totl rows, $(ncol(dfs[1])) columns, $(length(dfs)) datasets")
    tot = DataFrame([DataArray(x, totl) for x in coltypes(dfs[1])], colnames(dfs[1]))
    for (cn, ct) in zip(colnames(dfs[1]), coltypes(dfs[1]))
        println("binding $cn")
        tot[cn] = vecbind([df[cn]::DataArray{ct, 1} for df in dfs]...)
    end
    println("total size of output: $(size(tot))")
    return tot
end

tic()
println("adding datasets")
df = frbind(dfs)
toc()

function writedf(fn, df)
    o = jldopen(fn, "w")
    write(o, "df", df)
    close(o)
end

tic()
println("writing datasets")
writedf(of, df)
toc()

