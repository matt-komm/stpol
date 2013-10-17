using ROOT
using DataFrames

include("../skim/xs.jl")
flists = Dict{Any, Any}() 

flists[:data] = (readall("tchan.txt") |> split)

cutflow = {
    :nproc => Dict(),
    :all => Dict(),
    :muon => Dict(),
    :jet => Dict(),
    :tag => Dict(),
    :met => Dict(),
}
nproc = Dict()
muon = Dict()
nj = Dict()
nt = Dict()

metadata(fn) = replace(fn, ".root", "_processed.csv")

function inc!(d, k, v=1)
    if !haskey(d, k)
        d[k] = 0
    end
    d[k] += v
end

for fi in flists[:data]
    md = readtable(metadata(fi))

    for i=1:nrow(md)
        f = md[i, :files]
        cls = sample_type(f)[:sample]
        inc!(cutflow[:nproc], cls, md[i, :total_processed])
    end

    df = TreeDataFrame(fi)
    for i=1:nrow(df)
        findex = df[i, :fileindex]
        cls = sample_type(md[findex, :files])
        sample = cls[:sample] 
        lt = df[i, :lepton_type]
        k = "$(sample)_$(lt)"
        
        inc!(cutflow[:all], sample) 
        
        lt != "muon" ? continue :
        inc!(cutflow[:muon], sample)
        
        mtw = df[i, :mtw] 
        (!isna(mtw) && mtw < 40) ? continue :
        inc!(cutflow[:met], sample)
        
        df[i, :njets] != 2 ? continue :
        inc!(cutflow[:jet], sample)
        
        df[i, :ntags] != 1 ? continue :
        inc!(cutflow[:tag], sample)
        
    end
end

lumi = 20000
xsnorm = Dict()
for (sampn, nproc) in cutflow[:nproc]
    xsnorm[sampn] = cross_sections[string(sampn)] * lumi / nproc
end

println(xsnorm)

procs = {
    :tchan => [:T_t_ToLeptons, :Tbar_t_ToLeptons]
}

samples = keys(cutflow[:nproc])
for x in [:all, :muon, :met, :jet, :tag]

    for (proc, subprocs) in procs
        tot = 0
        for subpr in subprocs
            tot += cutflow[x][string(subpr)]*xsnorm[string(subpr)]
        end
        println("$x $proc $tot")
    end
end



