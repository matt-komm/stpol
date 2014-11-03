#!/usr/bin/env julia
inf = ["/hdfs/cms/store/user/joosep/Jul4_newsyst_newvars_metshift/iso/nominal/T_t_ToLeptons/output_1_1_l1M.root"]
flist = join(inf, " ")
exe=joinpath(ENV["HOME"], ".julia/CMSSW/julia")
run(`$exe skim.jl test $flist`)
