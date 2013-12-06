using DataArrays, DataFrames, HDF5, JLD

of = ARGS[1]
inf = ARGS[2:]

readdf(fn) = read(jldopen(fn, "r"), "df")

dfs = [readdf(f) for f in inf]

df = vcat(dfs...)

o = jldopen(of, "w")
write(o, "df", df)
close(o)
