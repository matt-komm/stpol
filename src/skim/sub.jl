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

    #fn = "$ofdir/job.$i"
    #ofile = "$ofdir/slurm.out.$i"
    fn = "/home/joosep/singletop/output/skims/output/job.$i"
    ofile = "/home/joosep/singletop/output/skims/output/slurm.out.$i"
    skimoutput = "$ofdir/skim.out.$i"
    scpath = dirname(Base.source_path())

    subcmd = `sbatch --exclude=$scpath/exclude.txt -p prio -J julia_job_test.$i -o $ofile $fn`
    
    #the submit script (indents matter)
    cmd="#!/bin/bash
uname -a
echo \$SLURM_JOB_ID
\ls -1 /hdfs &> /dev/null
RET=\$?
if [ \$RET -ne 0 ]; then
    echo '/hdfs was not available'
else
    ~/.julia/CMSSW/julia $scpath/skim.jl $ofdir/$outfile $infilelist > $skimoutput
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
            #println(e)
            sleep(1)
        end
    end
end

maxn = length(flist)
#either 50 files per job or split to 10 chunks
#perjob = min(100, ceil(maxn/10)) |> int
empty_flist = deepcopy(flist)

perjob=200
#N = int(ceil(maxn/perjob)-1)

j = 1
for n=1:perjob:maxn
    r = n:(n+perjob-1)

    #last chunk
    if r.start + r.len > maxn
        r = r.start:maxn
        #println(r.start, ":", r.len)
    end

    #submit
    #println(n, " ", r.start, ":", r.start:r.len-1)
    submit(flist[r], "output_$j", j)
    #println(flist[r])
    for x in flist[r]
        splice!(empty_flist, findfirst(empty_flist, x)) 
    end
    j += 1
    sleep(0.05)
end

length(empty_flist) ==0 || error("did not submit all jobs: $empty_flist")
