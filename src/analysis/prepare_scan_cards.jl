using JSON

infiles = readall(`find /hdfs/local/joosep/stpol/skims/feb27/split/feb19/ -name "*.root"` |> `sort`)|>split
infile(i) = "/hdfs/local/joosep/stpol/skims/feb27/split/feb19/output_$i.root"

binning=vcat(-Inf, linspace(-1, 1, 11), Inf)

function card(infile, n)
    return {
        "infile"=>infile,
        "outfile"=>"/hdfs/local/joosep/stpol/hists/$n.root",
        "tm_nominal_only" => false, 
    }
end

i = 1
card_path = "input/bdt_scan/cards/"
mkpath(card_path)

for i=1:length(infiles)
    of = open("$card_path/bdt_$i.json", "w")
    c = card(infile(i), i)
    write(of, json(c))
    close(of)
end

