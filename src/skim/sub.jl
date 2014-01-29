#!/usr/bin/env julia
#run as julia sub.jl ofdir infile1.txt infile2.txt ...
println("running sub.jl")

#output directory
ofdir = ARGS[1]
isdir(ofdir) || mkpath(ofdir)

#input files
flist = Any[]

#input files
for a in ARGS[2:length(ARGS)]
    #split the file by lines
    append!(flist, open(readall, a) |> split)
end

#submit a slurm job on a list of files (infiles) with output to outfile.
#the job is given an index i
function submit(infiles, outfile, i::Integer)

    #just a single file
    if typeof(infiles) == ASCIIString
        infiles = [infiles]
    end

    #join the file list into one line
    infilelist = join(infiles, " ")

    fn = "$ofdir/job.$i"
    ofile = "$ofdir/slurm.out.$i"
    skimoutput = "$ofdir/skim.out.$i"
    
    subcmd = `sbatch --exclude=./exclude.txt -p prio -J julia_job_test.$i -o $ofile $fn`
    
    #the submit script (indents matter)
    cmd="#!/bin/bash
uname -a
echo \$SLURM_JOB_ID
\ls -1 /hdfs &> /dev/null
RET=\$?
if [ \$RET -ne 0 ]; then
    echo '/hdfs was not available'
else
    ~/.julia/ROOT/julia-basic \$STPOL_DIR/src/skim/skim.jl $ofdir/$outfile $infilelist > $skimoutput
    RET=\$?
fi
echo 'done '\$RET && exit \$RET

###SUBCMD=$subcmd

"
    
    #write the slurm script
    fi = open(fn, "w")
    write(fi, cmd)
    close(fi)
    
    #run(subcmd)
    while true
        try
            run(subcmd)
            break
        catch e
            println(e)
            sleep(1)
        end
    end
end

maxn = length(flist)
#either 50 files per job or split to 10 chunks
perjob = min(50, ceil(maxn/10)) |> int
N = int(ceil(maxn/perjob)-1)

for n=1:N
    r = (1+(n-1)*perjob):(n*perjob)

    #last chunk
    if r.start+r.len > maxn
        r = r.start:maxn-r.start
    end

    #submit
    println(n, " ", r.start)
    submit(flist[r], "output_$n", n)
    sleep(0.1)
end
