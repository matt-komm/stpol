    
def asymmetry_weight(asymmetry, weight):
    print asymmetry, weight
    weight = "("+str(weight)+") * (("+str(asymmetry)+" * true_cos_theta + 0.5) / (0.44*true_cos_theta + 0.5))"
    return weight
