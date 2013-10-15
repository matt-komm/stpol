
flist = Any[]

#output directory
ofdir = ARGS[1]
isdir(ofdir) || mkdir(ofdir)

#input files
for a in ARGS[2:]
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

    #the submit script (indents matter)
    cmd="#!/bin/bash
~/.julia/ROOT.jl/julia skim.jl $ofdir/$outfile $infilelist
echo 'done '\$?
"

    #write the slurm script
    fn = "$ofdir/job.$i"
    fi = open(fn, "w")
    write(fi, cmd)
    close(fi)
    
    #run sbatch
    #println("Temp file is $fn")
    ofile = "$ofdir/slurm.out.$i" 
    run(`sbatch -p phys,prio,main -J julia_job_test.$i -o $ofile $fn`)
end

#split a job(file list) into either 10 pieces or 50-file pieces, whichever is smaller
maxn = length(flist)
perjob = min(50, ceil(maxn/10))
N = ceil(maxn/perjob)-1

for n=1:N
    r = (1+(n-1)*perjob):(n*perjob)

    #last chunk
    if r.start+r.len > maxn
        r = r.start:maxn-r.start
    end

    #submit
    println(n, " ", r.start)
    submit(flist[r], "output_$n", n)
end
