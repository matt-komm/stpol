using Base.Test

include("../histo.jl")
using Hist

include("../hplot.jl")

hi = Histogram(linspace(-1, 1, 10))

for i=1:1000
	x = 0.5 * randn()
	x = (x>1 || x<-1) ? NA : x
	hfill!(hi, x)
end

ax = axes()
x = hplot(ax, hi)
@test length(x)==9
savefig("hplot.png")
close()

ax = axes()
x = eplot(ax, hi)
savefig("eplot.png")
close()


nh = NHistogram({
	vcat(-Inf, linspace(-3, 3, 20), Inf),
	vcat(-Inf, linspace(-3, 3, 20), Inf)
})
for i=1:100000
	x = randn()
	y = rand()>0.8 ? NA : 0.2*randn()
	hfill!(nh, {x, y})
end
fig = figure(figsize=(15,15))
ax = axes()
hplot(ax, nh)
savefig("2d.png")
close()
