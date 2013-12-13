include("../analysis/base.jl")

fi = jldopen("$BASE/skim_nov29_5/merged/skim_nov29_5.jld.1T", "r"; mmaparrays=false);

println("reading data")
tic()
indata = DataFrame(read(fi, "df"));
toc();

println("performing selection")
tic()
inds = perform_selection(indata);
toc();

println("writing output")
tic()
write(jldopen("$BASE/skim.jld.1T.hmet.mu", "w"), "df", indata[inds[:nominal] .* inds[:mu] .* inds[:mtw], :])
write(jldopen("$BASE/skim.jld.1T.hmet.ele", "w"), "df", indata[inds[:nominal] .* inds[:ele] .* inds[:met], :])
toc();
