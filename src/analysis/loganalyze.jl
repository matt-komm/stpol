inf = ARGS[1:length(ARGS)]

for f in inf
    d = readall(f) |> lowercase |> split
    fi = filter(x -> length(x)>0, d)
    fi = filter(x -> match(r".*warning.*", x)!=nothing, fi)
    fi = filter(x -> match(r".*use.*", x)!=nothing, fi)
    if length(fi)>0
        println("$f ", join(fi[1:min(3, length(fi))], ","))
    end
end
