using ROOT, Histograms, ROOT.ROOTHistograms

fn = convert(ASCIIString, ARGS[1])

tf = TFile(fn)
@assert tf.p != C_NULL

kl = GetListOfKeys(tf)
@assert kl.p != C_NULL

key_iterator = TListIter(kl.p)
#kl = GetListOfKeys(tf)
#objs = GetList(tf)

ret = Dict()

tic()

path(l) = replace(join(kl, "/"), "=", "__")
for i=1:length(kl)
    #(i % 10000 == 0) && (println("$(i)/$(length(kl)) ", toq());tic())
    _k = Next(key_iterator)
    @assert _k != C_NULL
    const k = TKey(_k)
    const n = GetName(k) |> bytestring
    kl = split(n, ";")
    println(path(kl))
    #hfilter(n) || continue
    #const o = ReadObj(k) |> to_root
    #ret[n] = from_root(o)
end

toc()
Close(tf)
