using DataFrames

function dataset_nevents(ds)
    ret = readall(`python das_cli.py --query="dataset dataset=$ds | grep dataset.nevents" --limit=0`)
    return int(ret)
end

df = similar(DataFrame(name=ASCIIString[], df=ASCIIString[], ngen=Int64[]), 1000)

i=1
for line in readlines(open("../../datasets/step1/mc/nominal_Summer12_DR53X"))
    line = strip(line)
    beginswith(line, "#") && continue
    spl = split(line)
    length(spl)==2 || continue 
    dsname = spl[1] 
    ds = spl[2] 
    x = dataset_nevents(ds)
    df[i, :name] = dsname
    df[i, :df] = ds
    df[i, :ngen] = x
    println("$dsname $x")
    i+=1
end
df = df[1:i, :]
println(df)
writetable("generated.csv", df)
