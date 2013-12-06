using HDF5,JLD
using DataArrays, DataFrames
inf = ARGS[1]

tic()
al = @allocated let 
fi = jldopen(inf, "r")
nam = names(fi)
println("names=", join(nam, ","))

df = read(fi, "df");
close(fi)
println(size(df))
