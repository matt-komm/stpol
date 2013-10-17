using ROOT
using DataFrames

include("../skim/xs.jl")
flists = Dict{Any, Any}() 

flists[:data] = (readall("wjets.txt") |> split)

cutflow = {
    :nproc => Dict(),
    :all => Dict(),
    :hlt => Dict(),
    :muon => Dict(),
    :met => Dict(),
    :jet => Dict(),
    :rms => Dict(),
    :tag => Dict(),
}

metadata(fn) = replace(fn, ".root", "_processed.csv")

function inc!(d, k, v=1)
    if !haskey(d, k)
        d[k] = 0
    end
    d[k] += v
end

total_elapsed = @elapsed begin
tot_processed = 0
for fi in flists[:data]
    tic()
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
        
        df[i, :hlt] != true ? continue :
        inc!(cutflow[:hlt], sample)
        
        lt != "muon" ? continue :
        inc!(cutflow[:muon], sample)
        
        mtw = df[i, :mtw] 
        (!isna(mtw) && mtw < 40) ? continue :
        inc!(cutflow[:met], sample)
        
        df[i, :njets] != 2 ? continue :
        inc!(cutflow[:jet], sample)
        
        df[i, :ljet_rms] > 0.025 ? continue :
        inc!(cutflow[:rms], sample)
        
        df[i, :ntags] != 1 ? continue :
        inc!(cutflow[:tag], sample)
        
    end
    tot_processed += nrow(df)
    toc()
    println("$tot_processed")
end
end #elapsed

println("processed $tot_processed events in $tota_elapsed seconds")

lumi = 19600
println("cross-section normalizations for lumi $lumi/pb")
xsnorm = Dict()
for (sampn, nproc) in cutflow[:nproc]
    xsnorm[sampn] = cross_sections[string(sampn)] * lumi / nproc
    println("   $sampn: $(xsnorm[sampn])")
end


procs = {
    :tchan => [:T_t_ToLeptons, :Tbar_t_ToLeptons],
    :wjets => [:W1Jets_exclusive, :W2Jets_exclusive, :W3Jets_exclusive, :W4Jets_exclusive],
}

println("cutflow")
samples = keys(cutflow[:nproc])
for x in [:nproc, :all, :hlt, :muon, :met, :jet, :rms, :tag]

    for (proc, subprocs) in procs
        tot = 0
        for subpr in subprocs
            tot += cutflow[x][string(subpr)]*xsnorm[string(subpr)]
        end
        println("   $x $proc $tot")
    end
end



