using HDF5,JLD
using DataArrays, DataFrames
inf = ARGS[1]

fi = jldopen(inf, "r")
nam = names(fi)
println("names=", join(nam, ","))

el = @elapsed df = read(fi, "df");
close(fi)
println(size(df))
println("Opening time: $el seconds")
