using ROOT, ROOTDataFrames, DataFrames

indir = ARGS[1]
outfile = ARGS[2]

subdirs = readdir(indir)

v1 = Any[]
v2 = Any[]
for sd in subdirs
    push!(v1, joinpath(indir, sd, "output.root"))
    push!(v2, joinpath(indir, sd, "output.root.added"))
end

df1 = TreeDataFrame(v1)
df2 = TreeDataFrame(v2)

dtf = TreeDataFrame(
    convert(ASCIIString, outfile),
    [names(df1)..., names(df2)...],
    [eltypes(df1)..., eltypes(df2)...];
)

println(length(dtf.bvars), " ", length(dtf.types))
println("tree created, looping")

for i=1:nrow(df1)
    println(i)
    for d in {df1, df2}

        for n in names(d)
            #println(n)
            const j = dtf.index[n]

            const nc = 2 * j - 1
            const nc_isna = 2 * j
            println(nc, " ", nc_isna, " ", j)

            if !isna(d[i, n])
                dtf.bvars[nc][1] = d[i, n]
                dtf.bvars[nc_isna][1] = false
            else
                dtf.bvars[nc][1] = convert(dtf.types[j], 0)
                dtf.bvars[nc_isna][1] = true
            end
        end
    end
    Fill(dtf.tt)
end

Write(dtf.tt)
Close(dtf.tf)
