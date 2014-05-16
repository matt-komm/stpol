using ROOT, ROOTDataFrames, DataFrames

inf = ARGS[1]

df = TreeDataFrame(convert(ASCIIString, inf))
proc = replace(inf, ".root", "_processed.csv")
println(size(df))
p = readtable(proc)
println(sum(p[:total_processed]))
