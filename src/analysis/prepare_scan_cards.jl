using JSON

infiles = readall(`find /home/joosep/singletop/output/skims/feb19 -name "*.root"` |> `sort`)|>split
infile(i) = "/home/joosep/singletop/output/skims/feb19/output_$i.root"

#bdtpoints = vcat(-1.0, [-0.2:0.01:1.0])
bdtpoints = vcat(-1.0, 0.35, 0.4, 0.45, 0.85)

binning=vcat(-Inf, linspace(-1, 1, 11), Inf)

function card(infile, n)
    return {
        "infile"=>infile,
        "outfile"=>"/home/joosep/singletop/output/bdt_scan/$n.root",
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

