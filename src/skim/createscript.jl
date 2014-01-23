cmd = ARGS[1]
jobname = ARGS[2]

i=1
for line in readlines(STDIN)
    line = strip(line)
    x = deepcopy(cmd)
    x = replace(x, "{}", line)
    x = replace(x, "{#}", i)

    i += 1
    out = "echo \$'#!/bin/bash\\necho $line\\nset -e\\n$x\\necho \$?' | sbatch --exclude ./exclude.txt -p prio -J $jobname -e error-%j.out "
    println(out)
end
