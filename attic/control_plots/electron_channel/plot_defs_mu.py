#--------------cut values -------------------
mu_iso_cut = 0.12
mu_antiiso_cut = [0.3, 0.5]
mtW_cut = 50
jetpt_cut = 40
mupt_cut = 26

#-------------Initialize histogram and plot parameters-------------
hist_def = {
    "mt_mu": ["mt_mu", (100, 0, 200)],
    "met": ["met", (100, 0, 200)],
    "top_mass": ["top_mass", (100, 50, 300)],
    "eta_lj": ["eta_lj", (100, 0, 5.0)],
    "pt_lj": ["pt_lj",(100, 0, 200)],
    "cos_theta": ["cos_theta", (100, -1., 1.)],
    "mu_pt": ["mu_pt",(100, 20, 200)],
    "deltaR_bj": ["deltaR_bj",(100, 0, 2*3.142)],
    "deltaR_lj": ["deltaR_lj",(100, 0, 2*3.142)],
    "mu_mother_id": ["mu_mother_id",(51,-25.5,25.5)],
    }

hist_def_toplot = {
    "mt_mu": ["mt_mu", (100, mtW_cut, 200)],
    "met": ["met", (100, 0, 200)],
    "top_mass": ["top_mass", (100, 50, 300)],
    "eta_lj": ["eta_lj", (100, 2.5, 5.0)],
    "pt_lj": ["pt_lj",(100, jetpt_cut, 200)],
    "cos_theta": ["cos_theta", (100, -1, 1)],
    "mu_pt": ["mu_pt",(100, mupt_cut, 200)],
    "deltaR_bj": ["deltaR_bj",(100, 0, 2*3.142)],
    "deltaR_lj": ["deltaR_lj",(100, 0, 2*3.142)],
    "el_mother_id": ["el_mother_id",(51,-25.5,25.5)],
    }

#--------------------------cuts--------------------------------
jet_cuts = "pt_lj > 40 & pt_bj > 40 & rms_lj < 0.025"

sel_2j0t = "n_muons == 1 & n_eles == 0 & n_jets == 2 & n_tags == 0" + "&" + jet_cuts
sel_2j1t = "n_muons == 1 & n_eles == 0 & n_jets == 2 & n_tags == 1" + "&" + jet_cuts
sel_3j1t = "n_muons == 1 & n_eles == 0 & n_jets == 3 & n_tags == 1" + "&" + jet_cuts
sel_3j2t = "n_muons == 1 & n_eles == 0 & n_jets == 3 & n_tags == 2" + "&" + jet_cuts 

mu_iso_cut = 0.12
mu_antiiso_cut = [0.3, 0.5]
mtW_cut = 50

#---------------------------------------------------------------------------------

sel_lep = "1" #mu_pt > 26 & mu_iso < " + str(mu_iso_cut) + "& deltaR_bj > 0.5 & deltaR_lj > 0.5"
sel_lep_a = "1" #"mu_pt > 26 & mu_iso > " + str(mu_antiiso_cut[0]) + "& mu_iso < " + str(mu_antiiso_cut[1]) + "& deltaR_bj > 0.5 & deltaR_lj > 0.5"


#trigger = "( (HLT_Ele27_WP80_v10 ==1) || (HLT_Ele27_WP80_v11 == 1) || (HLT_Ele27_WP80_v9==1) || (HLT_Ele27_WP80_v8==1) )"

sel_mtW = "mt_mu > " + str(mtW_cut)
sel_topm = "top_mass > 130 & top_mass < 220"
sel_eta = "abs(eta_lj) > 2.5" 

cuts = {
    "2j0t_nomet": "(" + sel_2j0t + "&" + sel_lep + "&" + sel_topm + "&" + sel_eta  +")",
    "2j0t_nomet_antiiso": "(" + sel_2j0t + "&" + sel_lep_a + "&" + sel_topm + "&" + sel_eta  + ")",
    
     "2j1t_nomet": "(" + sel_2j1t + "&" + sel_lep + ")",
    "2j1t_nomet_antiiso": "(" + sel_2j1t + "&" + sel_lep_a + ")",   

    "final_nomet": "(" + sel_2j1t  + "&" + sel_lep + "&" + sel_topm + "&" + sel_eta  + ")",
    "final_nomet_antiiso": "(" + sel_2j1t + "&" + sel_lep_a + "&" + "&" + sel_topm + "&" + sel_eta  + ")",

    "2j1t": "("  + sel_2j1t + "&" + sel_lep + "&" + sel_mtW + "&" + ")",
    "2j1t_antiiso": "(" + sel_2j1t + "&" + sel_lep_a + "&" + sel_mtW + ")",

    "3j1t": "(" + sel_3j1t + "&" + sel_lep + "&" + sel_mtW +")",
    "3j1t_antiiso": "(" + sel_3j1t + "&" + sel_lep_a + "&" + sel_mtW + ")",
    
    "3j2t": "(" + sel_3j2t + "&" + sel_lep_a + "&" + sel_mtW +  ")",
    "3j2t_antiiso": "(" + sel_3j2t + "&" + sel_lep_a + "&" + sel_mtW + "&" + sel_lep_a + ")",

    "final": "(" + sel_2j1t + "&" + sel_lep + "&" + sel_mtW + "&" + sel_topm + "&" + sel_eta + ")",
    "final_antiiso": "(" + sel_2j1t + "&" + sel_lep_a + "&" + sel_mtW + "&" + sel_topm + "&" + sel_eta + ")"
    
    }
