scale_factors = dict()
for channel in ["mu", "ele"]:
    scale_factors[channel] = dict()
    for jt in ["2j0t", "2j1t", "3j1t", "3j2t"]:
        scale_factors[channel][jt] = dict()
scale_factors["mu"]["2j0t"]["met"] = 14.6874513178
scale_factors["mu"]["2j0t"]["mtw"] = 8.46760776463
scale_factors["mu"]["2j1t"]["met"] = 9.48447671263
scale_factors["mu"]["2j1t"]["mtw"] = 6.6720269212
scale_factors["mu"]["3j1t"]["met"] = 0.319652480076
scale_factors["mu"]["3j1t"]["mtw"] = 0.221800737672
scale_factors["mu"]["3j2t"]["met"] = 0.102671125287
scale_factors["mu"]["3j2t"]["mtw"] = 0.0777717192089

scale_factors["ele"]["2j0t"]["met"] = 6.22486944012
scale_factors["ele"]["2j0t"]["mtw"] = 3.78769087229
scale_factors["ele"]["2j1t"]["met"] = 5.45486347542
scale_factors["ele"]["2j1t"]["mtw"] = 3.05365275868
scale_factors["ele"]["3j1t"]["met"] = 0.435239212117
scale_factors["ele"]["3j1t"]["mtw"] = 0.153936203257
scale_factors["ele"]["3j2t"]["met"] = 0.245998596181
scale_factors["ele"]["3j2t"]["mtw"] = 2.11648078839e-07
