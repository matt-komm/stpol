include("../histo.jl")
using Hist
using Base.Test

@test_throws Histogram([1],[1],[0])
@test_throws Histogram([-1],[1],[0,1])

h = Histogram([1],[1],[0,1])
@test integral(h)==1

hs=h+h
@test hs==Histogram([2],[2],[0,1])

hs=sum([h,h])
@test hs==h+h

hs=sum([h])
@test hs==h

#show(h)
#df = todf(h)
#show(df)
#h1 = fromdf(df)
#show(h1)

@test fromdf(todf(h)) == h

h = Histogram([1,2],[3,4],[1,2,3])
@test rebin(h, 2)==Histogram([3],[7],[1,3])
@test rebin(
		Histogram([1,2,3, 0,1,2],[3,4,5, 0,4,5], [1,2,3, 4,5,6, 7]),
		3
	) ==
	Histogram([6, 3], [12, 9], [1, 4, 7])

@test_throws rebin(Histogram([1,2],[3,4],[1,2,3]), 3)