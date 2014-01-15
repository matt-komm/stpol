def get_varlist(channel):
    varlist = ["met", "c", "top_mass", "top_eta",
        "D", "circularity", "aplanarity", "isotropy", "thrust", 
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
        channel+"_mtw",
        #channel+"_eta", 
        #channel+"_phi"
        ]
    return varlist
