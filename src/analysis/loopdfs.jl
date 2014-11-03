include("base.jl")

sumfname = ARGS[1]
inf = ARGS[2:length(ARGS)]

tot_res = JSON.parse(readall(sumfname))

meantimes = Any[]
resdf = DataFrame()

i=1

rets = Any[]
for fi in inf
    println(fi)
    tic()	
    jfi = jldopen(fi, "r";mmaparrays=false)
    df = read(jfi, "df")::DataFrame
    
    #acc = accompanying(fi)
    #mvas = filter(x->match(r"mva.*", x)!=nothing, keys(acc))|>collect

    #
    #for mva in mvas
    #    t = readtable(acc[mva];allowcomments=true)
    #    println(mva, " ", size(t), " ", size(df))
    #    @assert nrow(t)==nrow(df)
    #    mvaname = match(r"mva_(.*)", mva).captures[1]     
    #    df[mvaname] = t[1]
    #end
    
    df[:ngen] = int64(0)
    df[:xsweight] = float64(0.0)

    for j=1:nrow(df)
        const subsample = hmap[:from][int(df[j, :subsample])]
        const iso = hmap[:from][int(df[j, :isolation])]
        const systematic = hmap[:from][int(df[j, :systematic])]
        const ngen = tot_res["$(subsample)/$(iso)/$(systematic)/counters/generated"]
        if contains(string(subsample), "T_t_ToLeptons_scale")
            k = (subsample, iso, systematic, ngen, fi)
            #(k in rets) || push!(rets, k)
            println("$j ", k)
        end
        df[j, :ngen] = ngen
        df[j, :xsweight] = cross_sections[subsample] / ngen
    end
    
    close(jfi)
    
    i += 1
end
#println(rets)
