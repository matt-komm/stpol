using DataFrames

dir = ARGS[1]
jobfiles = split(readall(`find $dir -name "job*"`))
println("total jobs: $(length(jobfiles))")
df = similar(DataFrame(job=ASCIIString[], subcmd=ASCIIString[], ecode=Int64[]), length(jobfiles))

i = 1
for jf in jobfiles
    df[i, "job"] = string(jf)
    jf_contents = readall(jf)
    
    m = match(r"###SUBCMD=(.*)", jf_contents)
    subcmd = (m != nothing ? m.captures[1][2:length(m.captures[1])-1] : NA)
    df[i, "subcmd"] = string(subcmd)

    sf = replace(jf, "job", "slurm.out")
    ecode = -3
    if isfile(sf)
        contents = readall(sf)
        m = match(r"done ([0-9]+)", contents)
        ecode = (m != nothing ? m.captures[1] : -1)
        
    else
        ecode = -2
    end
    df[i, "ecode"] = int(ecode)
    i += 1
end

done = df[:(ecode .== 0), :]
println("done jobs: $(nrow(done))")

failed = df[:(ecode .!= 0), :]
println("failed jobs: $(nrow(failed))")
for i=1:nrow(failed)
    println(failed[i, :subcmd])
end


