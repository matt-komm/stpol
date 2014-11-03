set -e
\ls -1 /hdfs &> /dev/null
RET=$?
if [ $RET -ne 0 ]; then
    echo '/hdfs was not available'
    exit 1
fi

outfile="output"
scpath=/home/joosep/Dropbox/kbfi/top/stpol/src/skim
mvapath=$scpath/../mva

~/.julia/CMSSW/julia $scpath/skim.jl $outfile $FILE_NAMES

#source ~/local-sl6/root/bin/thisroot.sh && ( python $mvapath/adder.py bdt_sig_bg_old $mvapath/weights/stpol_bdt_sig_bg_lepton_flavour.weights.xml $outfile.root )
#source ~/local-sl6/root/bin/thisroot.sh && ( python $mvapath/adder.py bdt_sig_bg $mvapath/weights/stpol_bdt_sig_bg_mixed_lepton_flavour.weights.xml $outfile.root ) 
#source ~/local-sl6/root/bin/thisroot.sh && ( python $mvapath/qcd_mva_adder.py $outfile.root )
#source ~/local-sl6/root/bin/thisroot.sh && ( python $mvapath/top_13_001_mva_adder.py $outfile.root )
\ls -1 .

p=/hdfs/local/joosep/stpol/skims/@DATASETPATH@/@MY_JOBID@
rm -Rf $p
mkdir -p $p
rsync -c output* $p
echo $p
find $p -name "*"
