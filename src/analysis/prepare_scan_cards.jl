error("DEPRECATED")
using JSON

function card(infile, outpath, n, qcd_cut)
    return {
        "infile"=>infile,
        "outfile"=>"$outpath/$n.root",
        "tm_nominal_only" => false, 
        "qcd_cut" => qcd_cut,
    }
end

#indir = "/hdfs/local/joosep/stpol/skims/feb27/split/feb19/"
indir = 

function prepare_cards(indir, outpath, card_path, qcd_cut="mva_nominal") 
    mkpath(card_path)
    infiles = readall(`find $indir -name "*.root"` |> `sort`)|>split
    infile(i) = "$indir/output_$i.root"
    
    i = 1
    
    for i=1:length(infiles)
        of = open("$card_path/bdt_$i.json", "w")
        c = card(infile(i), outpath, i, qcd_cut)
        write(of, json(c))
        close(of)
    end
end

prepare_cards(
    "/hdfs/local/joosep/stpol/skims/mar19",
    "/home/joosep/singletop/output/hists/mar19", "input/hists/mar19"
)

prepare_cards(
    "/hdfs/local/joosep/stpol/skims/mar19",
    "/home/joosep/singletop/output/hists/mar19__qcd_metmtw_nominal", "input/hists/mar19__qcd_metmtw_nominal", "metmtw_nominal"
)

prepare_cards(
    "/hdfs/local/joosep/stpol/skims/mar22_tchpt",
    "/home/joosep/singletop/output/hists/mar22_tchpt", "input/hists/mar22_tchpt"
)
