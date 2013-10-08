
flist = Any[]

for a in ARGS[1:]
    append!(flist, open(readall, a) |> split)
end

function submit(infiles, outfile, i::Integer)
    if typeof(infiles) == ASCIIString
        infiles = [infiles]
    end
    infilelist = join(infiles, " ")
    cmd="#!/bin/bash
~/.julia/ROOT.jl/julia skim.jl $outfile $infilelist
echo 'done '\$?
"
    fn = tempname()
    fi = open(fn, "w")
    write(fi, cmd)
    close(fi)
    println("Temp file is $fn")
    ofile = "slurm.out.$i" 
    @async begin
        run(`sbatch -p phys,prio -J julia_job_test.$i -o $ofile $fn`)
        while true
            sleep(1.0)
            if !isfile(ofile)
                continue
            end
            s = open(readall, ofile)
            m = match(r".*done ([0-9]*).*", s)
            if m!=nothing
                return int(m.captures[1])
            end
        end
    end
end

rets = Any[]
el = @elapsed @sync begin
    maxn = length(flist)
    perjob = min(50, ceil(maxn/10))
    N = ceil(maxn/perjob)
    for n=1:N
        r = (1+(n-1)*perjob):(n*perjob)
        if r.start+r.len > maxn
            r = r.start:maxn-r.start
        end
        println(n, " ", r.start)
        ret = submit(flist[r], "output_$n", n)
    end
end
println("Return codes: ", join(rets, ", "))
println("Time elapsed: $el")
