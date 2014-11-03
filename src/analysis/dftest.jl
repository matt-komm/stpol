using DataFrames, HDF5, JLD
#fi = jldopen("/scratch/joosep/skim_jan31_2/output_1.jld")
fi = jldopen("output_1.jld")
df = read(fi, "df")
println(size(df))
