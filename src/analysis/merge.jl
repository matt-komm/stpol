INDIR="../../results/hists/Jul23/output/bdt_scan/hists/"
OUTDIR="../../results/hists/Jul23/merged"

function merge(fn, lep, jet, tag, kind, outdir)
    ofn = basename(fn)
    run(`python regroup.py $fn $outdir/$(jet)j_$(tag)t/$lep/$ofn $lep $(jet)j$(tag)t $kind`)
end

for (jet, tag) in [(2,1), (3,2), (2,0)]
    for lep in [:mu, :ele]
        infs = readall(`find $INDIR/preselection/$(jet)j_$(tag)t/$lep -name "*.root"`)|>split
        for inf in infs
            merge(inf, lep, jet, tag, "plot", "$OUTDIR/preselection")
        end
    end
end
