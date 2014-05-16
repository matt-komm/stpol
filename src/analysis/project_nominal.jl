require("base.jl")
using CMSSW

infile = ARGS[1]

const df_base = TreeDataFrame(infile)
const df_added = TreeDataFrame("$infile.added")

systs = df_base[:systematic]
noms = (
    (systs .== hmap[:to]["nominal"]) |
    (systs .== hmap[:to]["unknown"])
#    (systs .== hmap[:to]["signal_comphep_anomWtb-0100"]) |
#    (systs .== hmap[:to]["signal_comphep_anomWtb-unphys"]) |
#    (systs .== hmap[:to]["signal_comphep_nominal"])
)

ba = BitArray(length(noms))
for i=1:length(noms)
    ba[i] = noms[i]
end

df = df_base[ba, names(df_base)]
df2 = df_added[ba, names(df_added)]
df = hcat(df, df2)

writetree_temp(ARGS[2], df)
