function load_files(p)
    files = map(strip,
        filter(x->contains(x, ".root"), split(readall(p))),
    )
    filed = Dict()
    for x in files
        x = convert(ASCIIString, x)
        sample = join(split(x, "/")[end-4:end-2], "/")
        if !haskey(filed, sample)
            filed[sample] = Any[]
        end
        push!(filed[sample], x)
    end
    return filed
end

added(x) = replace(x, ".root", ".root.added");

