from rootpy.io import File

if __name__=="__main__":
	fi1 = "efficiency.root"
	fi2 = "efficiency_working.root"

	fi1 = File(fi1)
	fi2 = File(fi2)
	for root, dirs, items in fi1.walk():
		for it in items:
			it1 = fi1.Get("/".join([root,it]))
			it2 = fi2.Get("/".join([root,it]))
			print it1, it2

			i = 0
			for a, b, c, d in zip(list(it1.y()), list(it2.y()), list(it1.yerravg()), list(it2.yerravg()), ):
				s = ""
				if (a+b)>0 and abs(a-b)/(a+b)>0.01:
					s += "***"
				if (c+d)>0 and abs(c-d)/(c+d)>0.01:
					s += "+++"
				print s, i, a, b, c, d
				i += 1
			chi2 = it1.Chi2Test(it2, "WW CHI2/NDF")
			ks = it1.KolmogorovTest(it2)
			print it, chi2, ks