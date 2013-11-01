
hist_def = {
    "met": ["met", (100, 0, 200)],
    "top_mass": ["top_mass", (100, 50, 300)],
    "eta_lj": ["eta_lj", (100, 0, 5.0)],
    "pt_lj": ["pt_lj",(100, 0, 200)],
    "cos_theta": ["cos_theta", (100, -1.01, 1.01)],
    "el_pt": ["el_pt",(100, 20, 200)],
    "el_mva": ["el_mva",(200, 0.85, 1.0)],
    "el_reliso": ["el_reliso",(100, 0, 0.5)],
    "deltaR_bj": ["deltaR_bj",(100, 0, 2*3.142)],
    "deltaR_lj": ["deltaR_lj",(100, 0, 2*3.142)],
    "el_mother_id": ["el_mother_id",(51,-25.5,25.5)],
    }

hist_def_toplot = {
    "met": ["met", (100, 45, 200)],
    "top_mass": ["top_mass", (100, 50, 300)],
    "eta_lj": ["eta_lj", (100, 2.5, 5.0)],
    "pt_lj": ["pt_lj",(100, 0, 200)],
    "cos_theta": ["cos_theta", (100, -1, 1)],
    "el_pt": ["el_pt",(100, 30, 200)],
    "el_mva": ["el_mva",(200, 0.9, 1.0)],
    "el_reliso": ["el_reliso",(100, 0, 0.5)],
    "deltaR_bj": ["deltaR_bj",(100, 0, 2*3.142)],
    "deltaR_lj": ["deltaR_lj",(100, 0, 2*3.142)],
    "el_mother_id": ["el_mother_id",(51,-25.5,25.5)],
    }

jet_cuts = "pt_lj > 40 & pt_bj > 40 & rms_lj < 0.025"

sel_2j0t = "n_eles == 1 & n_muons == 0 & n_jets == 2 & n_tags == 0" + "&" + jet_cuts
sel_2j1t = "n_eles == 1 & n_muons == 0 & n_jets == 2 & n_tags == 1" + "&" + jet_cuts
sel_3j1t = "n_eles == 1 & n_muons == 0 & n_jets == 3 & n_tags == 1" + "&" + jet_cuts
sel_3j2t = "n_eles == 1 & n_muons == 0 & n_jets == 3 & n_tags == 2" + "&" + jet_cuts

trigger = "( (HLT_Ele27_WP80_v8 == 1 ) || (HLT_Ele27_WP80_v9 == 1) || (HLT_Ele27_WP80_v10==1) || (HLT_Ele27_WP80_v11==1) )"

el_mva_cut = 0.9
el_iso_cut = 0.1
el_antiiso_cut = [ 0.15, 0.5 ]
met_cut = 45

#---------------------------------------------------------------------------------
sel_lep = "el_pt > 30 & el_mva > " + str(el_mva_cut) + "& el_reliso < " + str(el_iso_cut) + " & deltaR_bj > 0.5 & deltaR_lj > 0.5"
sel_lep_a = "el_pt > 30 & el_reliso > " + str(el_antiiso_cut[0]) + "& el_reliso < " + str(el_antiiso_cut[1]) + " & deltaR_bj > 0.5  & deltaR_lj > 0.5" #& el_mva < " + str(el_mva_cut)

sel_met = "met > " + str(met_cut)
sel_topm = "top_mass > 130 & top_mass < 220"
sel_eta = "abs(eta_lj) > 2.5" 

cuts = {
    "2j0t_nomet": "(" + sel_2j0t + "&" + sel_lep +")",
    "2j0t_nomet_antiiso": "(" + sel_2j0t + "&" + sel_lep_a + ")",
    
    "2j0t": "(" + sel_2j0t + "&" + "&" + sel_lep + "&" + sel_met + ")",
    "2j0t_antiiso": "(" + sel_2j0t + "&" + sel_lep_a + "&" + sel_met + ")",

    "2j1t_nomet": "(" + sel_2j1t + "&" + sel_lep + ")",
    "2j1t_nomet_antiiso": "(" + sel_2j1t + "&" + sel_lep_a + ")",   

    "final_nomet": "(" + sel_2j1t  + "&" + sel_lep + "&" + sel_topm + "&" + sel_eta  + ")",
    "final_nomet_antiiso": "(" + sel_2j1t + "&" + sel_lep_a + "&" + "&" + sel_topm + "&" + sel_eta  + ")",

    "2j1t": "("  + sel_2j1t + "&" + sel_lep + "&" + sel_met + ")",
    "2j1t_antiiso": "(" + sel_2j1t + "&" + sel_lep_a + "&" + sel_met + ")",

    "3j1t": "(" + sel_3j1t + "&" + sel_lep + "&" + sel_met + ")",
    "3j1t_antiiso": "(" + sel_3j1t + "&" + sel_lep_a + "&" + sel_met  + ")",
    
    "3j2t": "(" + sel_3j2t + "&" + sel_lep + "&" + sel_met + ")",
    "3j2t_antiiso": "(" + sel_3j2t + "&" + sel_lep_a + "&" + sel_met + ")",

    "final": "(" + sel_2j1t + "&" + sel_lep + "&" + sel_met + "&" + sel_topm + "&" + sel_eta + ")",
    "final_antiiso": "(" + sel_2j1t + "&" + sel_lep_a + "&" + sel_met + "&" + sel_topm + "&" + sel_eta + ")"
    
    }
