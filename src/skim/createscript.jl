#!/usr/bin/env julia
cmd = join(ARGS[1:end-1], " ")
jobname = ARGS[end]

i=1
of = open("$jobname.submit.sh", "w")
for line in readlines(STDIN)
    line = strip(line)
    x = deepcopy(cmd)
    x = replace(x, "{}", line)
    x = replace(x, "{#}", i)

    i += 1
    out = "echo \$'#!/bin/bash\\nuname -a\\nhostname\\nwhich julia\\necho LINE=$line\\necho CMD=\"$cmd\"\\necho FCMD=\"$x\"\\nset -e\\ntime $x\\necho \$?' | sbatch --exclude ../skim/exclude.txt -p prio -J $jobname -e error-%j.out"
    write(of, "$out\n") 
end
close(of)
