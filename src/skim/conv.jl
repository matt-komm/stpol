include("util.jl")

indir = ARGS[1]
ofname = ARGS[2]

infiles = readall(`find $indir -name "*.csv.gz"`) |> split

el1 = @elapsed df = open_multi(infiles)
println("opened data frame: $(size(df)) in $el1 seconds")

el2 = @elapsed save_df(ofname, df)
println("saved DataFrame in $el2 seconds")

