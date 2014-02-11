include("../histo.jl")
using Hist
#include("../hroot.jl")
using Base.Test
using DataFrames

@test_throws Histogram([1],[1],[0,1])
@test_throws Histogram([-1],[1],[0])

h = Histogram([-Inf, -1, 0, 1, Inf])

@test nbins(h)==5

@test findbin(h, -1.0001) == 1
@test findbin(h, -1)== 1
@test findbin(h, -0.9999)== 2

@test findbin(h, 0.9999)== nbins(h)-2
@test findbin(h, 1) == nbins(h)-2
@test findbin(h, 1.0001) == nbins(h)-1

hfill!(h, -1.0)
@test(h.bin_entries[1]==1)
hfill!(h, -0.999)
@test(h.bin_entries[2]==1)
hfill!(h, NaN)
@test(h.bin_entries[1]==2)
hfill!(h, NA)
@test(h.bin_entries[1]==3)

hfill!(h, 0.5, float32(0.5))
hfill!(h, 0.5, 0.5)

h = Histogram([1],[1],[0])
@test integral(h)==1

hs=h+h
@test hs==Histogram([2],[2],[0])

hs=sum([h,h])
@test hs==h+h

hs=sum([h])
@test hs==h

#@test fromdf(todf(h)) == h

h = Histogram([1,2],[3,4],[1,2])
@test rebin(h, 2)==Histogram([3],[7],[1])
@test rebin(
		Histogram([1,2,3, 0,1,2],[3,4,5, 0,4,5], [1,2,3, 4,5,6]),
		3
	) ==
	Histogram([6, 3], [12, 9], [1, 4])

@test_throws rebin(Histogram([1,2],[3,4],[1,2,3]), 3)

h = Histogram([1,2],[3,4],[1,2])
@test cumulative(h)==Histogram([1,3],[3,7],[1,2])

@test_approx_eq_eps(test_ks(h, h), 0.0, 0.00001)
@test_approx_eq_eps(test_ks(h, 3.3*h), 0.0, 0.00001)


nh = NHistogram({[-1, 0, 1], [-1, 0, 1]})
@test nbins(nh)==9
@test ndim(nh)==2
@test findbin_nd(nh, [0.1, 0.1]) == [2,2]
@test findbin_nd(nh, [1.1, 0.1]) == [3,2]
@test findbin_nd(nh, [0.1, 1.1]) == [2,3]

hfill!(nh, (NA, NA))
@test nh[1,1]==1

hfill!(nh, (0.5, 0.5))
hfill!(nh, (0.5, 0.5))
@test nh[2,2] == 2

hfill!(nh, (0.5, 1.1))
hfill!(nh, (0.5, 1.1))
hfill!(nh, (0.5, 1.1))
@test nh[2,3] == 3

hfill!(nh, (1.1, 1.1))
hfill!(nh, (1.1, 1.1))
hfill!(nh, (1.1, 1.1))
hfill!(nh, (1.1, 1.1))
@test nh[3, 3] == 4

# writecsv("test_2d.csv", nh)
# @test isfile("test_2d.csv.json")
# @test isfile("test_2d.csv.hist")
# @test readhist("test_2d.csv") == nh

nh = NHistogram({
	vcat(-Inf, linspace(-3, 3, 20), Inf),
	vcat(-Inf, linspace(-2, 2, 10), Inf)
})
for i=1:100000
	x = randn()
	y = rand()>0.8 ? NA : 0.2*randn()
	hfill!(nh, {x, y})
end
# writecsv("test_2d_large.csv", nh)
# @test readhist("test_2d_large.csv") == nh

nc, ne = asarr(nh)
x = fromarr(nc, ne, nh.edges)
nht = transpose(nh)
@test nht[2,3]==nh[3,2]
@test transpose(nht)==nh
@test x == nh



# verybigdf = DataFrame(x=randn(1000000),y=randn(1000000))
# tic()
# makehist_2d(verybigdf, {vcat(-Inf, linspace(-3, 3, 10), Inf), vcat(-Inf, linspace(-3, 3, 10), Inf)})
# toc()

println("* histo.jl passed")