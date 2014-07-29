include("../analysis/base.jl")

for l in readlines(STDIN)
    l = first(split(l, " "))
    if contains(l, ".root") 
        println(l, "=>", collect(sample_type(l)))
    end
end
