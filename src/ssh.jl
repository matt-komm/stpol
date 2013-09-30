addprocs_kbfi(n::Integer) = addprocs(n, cman=Base.SSHManager(machines=["thebe.hep.kbfi.ee"]), dir="/home/joosep/local-sl6/julia/usr/bin")
