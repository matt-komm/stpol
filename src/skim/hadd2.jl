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
    #for cn in colnames(tot)
    #    tot[1:nrow(tot), cn] = NA
    #end

    #for i in [1:length(dfs)]
    #    tic()
    #    prevl = sum([nrow(df) for df in dfs[1:i-1]])
    #    println("binding $i=$prevl:$(nrow(dfs[i]))")
    #    println("df = $(size(dfs[i]))")
    #    #describe(dfs[i])
    #    for cn in colnames(dfs[i])
    #        println(cn)
    #        tot[prevl+1:nrow(dfs[i]), cn] = dfs[i][cn]
    #    #    for j=1:nrow(dfs[i])
    #    #        tot[prevl+j, cn] = dfs[i][j,cn]
    #    #    end
    #    end
    #    toc()
    #end
    println("total size of output: $(size(tot))")
    println(colnames(tot))
    #describe(tot)
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
println("splitting datasets")
df_lowmet = df[:(met .< 30), :]
df_highmet = df[:(met .>= 30), :]
toc()

tic()
println("writing datasets")
writedf(of, df)
#writedf("$of.lowmet", df_lowmet) 
#writedf("$of.highmet", df_highmet) 
toc()

