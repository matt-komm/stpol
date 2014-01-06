using HDF5,JLD
using DataFrames
inf = ARGS[1]

tic()

fi = jldopen(inf, "r")
nam = names(fi)
println("names=", join(nam, ","))

df = read(fi, "df");
close(fi)
println(size(df))
