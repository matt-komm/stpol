#!/bin/bash

#julia yields.jl data_ele /hdfs/local/joosep/stpol/skims/step3/csvt/Jul4_newsyst_newvars_metshift/antiiso/SingleEle*/*/output.root
julia yields.jl data_ele `cat singleele.txt | xargs`

#julia yields.jl data_mu /hdfs/local/joosep/stpol/skims/step3/csvt/Jul4_newsyst_newvars_metshift/antiiso/SingleMu*/*/output.root
#julia yields.jl data_mu /home/andres/single_top/stpol_pdf/src/step3/output/Oct28_reproc/antiiso/data/SingleMu/output*.root
#
#julia yields.jl tchan /hdfs/local/joosep/stpol/skims/step3/csvt/Jul4_newsyst_newvars_metshift/iso/nominal/T*_t_ToLeptons/*/output.root
#julia yields.jl tchan /home/andres/single_top/stpol_pdf/src/step3/output/Oct28_reproc/iso/nominal/T*_t_ToLeptons/output*.root
#
#julia yields.jl ttjets /hdfs/local/joosep/stpol/skims/step3/csvt/Jul4_newsyst_newvars_metshift/iso/nominal/TTJets_*Lept/*/output.root
#julia yields.jl ttjets /home/andres/single_top/stpol_pdf/src/step3/output/Oct28_reproc/iso/nominal/TTJets_*Lept/output*.root

#julia yields.jl wjets /hdfs/local/joosep/stpol/skims/step3/csvt/Jul4_newsyst_newvars_metshift/iso/nominal/W*Jets_exclusive/*/output.root
julia yields.jl wjets `cat wjets.txt | xargs` 
