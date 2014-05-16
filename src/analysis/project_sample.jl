require("base.jl")
using CMSSW

sample = ARGS[1]
infile = ARGS[2]

const df_base = TreeDataFrame(infile)
const df_added = TreeDataFrame("$infile.added")

samples = df_base[:sample]
#iso = df_base[:isolation]
#syst = df_base[:systematic]

noms = (
    (samples .== hmap[:to][sample]) 
#    (iso .== hmap[:to]["iso"]) & 
#    ((syst .== hmap[:to]["nominal"]) | 
)

ba = BitArray(length(noms))
for i=1:length(noms)
    ba[i] = noms[i]
end

println("loading main df")
df = df_base[ba, :]

println("loading added df")
df2 = df_added[ba, :]
println("catting")
df = hcat(df, df2)

println("writing output")
println(df)
outfile = ARGS[3]
writetree_temp(outfile, df)

