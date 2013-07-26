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
			ov1 = it1.overflow()
			ov2 = it2.overflow()

			un1 = it1.underflow()
			un2 = it2.underflow()

			if ov1+ov2>0 and abs(ov1-ov2)/(ov1+ov2):
				s += "ooo"
			if un1+un2>0 and abs(un1-un2)/(un1+un2):
				s += "uuu"
			print ov1, ov2, un1, un2
			for a, b, c, d in zip(list(it1.y()), list(it2.y()), list(it1.yerravg()), list(it2.yerravg()), ):
				s = ""
				
				x1=0
				x2=0
				if (a+b)>0:
					x1 = abs(a-b)/(a+b)
				if (c+d)>0:
					x2 = abs(c-d)/(c+d)

				print i, a, b, c, d, x1, x2
				i += 1
			chi2 = it1.Chi2Test(it2, "WW CHI2/NDF")
			ks = it1.KolmogorovTest(it2)
			print it, chi2, ks