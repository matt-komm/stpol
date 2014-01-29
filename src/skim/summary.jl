#!/usr/bin/env julia
using DataFrames

do_print_failed = "--list" in ARGS

function elem_count(arr)
    outd = Dict()
    for k in arr
        if !haskey(outd, k)
            outd[k] = 0
        end
        outd[k] += 1
    end
    return outd
end

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

done = df[df["ecode"] .== 0, :]
println("done jobs: $(nrow(done))")

if nrow(done) == length(jobfiles)
    println("all jobs are done")
    exit(0)
end

failed = df[df["ecode"] .!= 0, :]
failed_counts = elem_count(failed[:ecode])

for excode in keys(failed_counts)
    failed = df[df["ecode"] .== excode, :]
    println("failed jobs with exit code $excode $(nrow(failed))")
    for i=1:nrow(failed)
        if do_print_failed
            println(failed[i, :subcmd])
        end
    end
    println()
end

println("jobs are not done")
exit(1)
