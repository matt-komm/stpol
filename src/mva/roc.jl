#extracts the data points necessasry to calculate the ROC curve
#julia datadir mvaname ofname

using DataFrames

dir = ARGS[1]
mvaname = ARGS[2]
ofname = ARGS[3]

samples = Dict()

for samp in [:wjets, :ttjets, :tchan]
    samples[samp] = split(readall(`find $dir/$samp -name "*$mvaname.csv"`))
end

dfs = Dict()
for (samp, files) in samples
    dfs[samp] = rbind(map(readtable, files))
    println("$samp: $(nrow(dfs[samp]))")
end

function eff(df, x)
    col = symbol(colnames(df)[1])
    ex = :($col .> $x)
    s = df[ex, :]
    return nrow(s)/nrow(df)
end


n = 1000
effs = similar(
    DataFrame(
        x=Float32[], tchan=Float32[], ttjets=Float32[], wjets=Float32[]
    ), n 
)

i = 1
for x in linspace(-0.6, 0.2, n)
    effs[i, :x] = x
    for samp in [:wjets, :ttjets, :tchan]
        effs[i, samp] = eff(dfs[samp], x)
    end
    i += 1
    print(".")
end
print("\n")

writetable(ofname, effs, separator=',')
