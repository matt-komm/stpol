def get_varlist(channel):
    varlist = ["met", "c", "top_mass", "top_eta",
        "D", "aplanarity", "isotropy", "thrust", 
        #"bjet_dr", 
        #"bjet_eta", 
        "bjet_mass", 
        #"bjet_phi", 
        "bjet_pt",
        #"ljet_dr", 
        #"ljet_eta", 
        "ljet_mass", 
        #"ljet_phi", 
        "ljet_pt",
        #channel+"_pt",
        #channel+"_eta", 
        #channel+"_phi",
        ]
    if channel == "mu":
        varlist.append(channel+"_mtw")        
    return varlist

def get_extra_vars(channel):
    varlist = varlist = [#"bjet_dr", 
        #"bjet_eta", 
        #"bjet_phi", 
        #"ljet_dr", 
        "ljet_eta", 
        #"ljet_phi", 
        channel+"_pt",
        #channel+"_mtw",
        channel+"_eta", 
        channel+"_phi",
        "iso",
        "cos_theta",
        "cos_theta_bl",
        "qcd_mva"
        ]
    if channel == "ele":
        varlist.append(channel+"_mtw")        
    
    return varlist
