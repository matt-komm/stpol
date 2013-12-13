
function split_tag(indata, ofname)
    for nt in Any[1, 2]
        println("ntags=$nt")
        tic()
        if isna(nt)
            df = select(:(isna(ntags)), indata)
        else
            df = select(:(ntags .== $nt), indata)
        end
        df = DataFrame(df) #make a copy
        of = jldopen("$ofname.jld.$(nt)T", "w")
        write(of, "df", df)
        close(of)
#        writetree("$ofname.root.$(nt)T", df)
        toc()
    end
end
