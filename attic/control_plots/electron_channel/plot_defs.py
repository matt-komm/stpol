
hist_def = {
    "met": ["met", (100, 0, 200)],
#    "top_mass": ["top_mass", (100, 50, 300)],
#    "eta_lj": ["eta_lj", (100, 0, 5.0)],
#    "pt_lj": ["pt_lj",(100, 0, 200)],
#    "cos_theta": ["cos_theta", (100, -1.01, 1.01)],
#    "el_pt": ["el_pt",(100, 20, 200)],
    "el_mva": ["el_mva",(200, 0.85, 1.01)],
#    "deltaR_bj": ["deltaR_bj",(100, 0, 2*3.142)],
#    "deltaR_lj": ["deltaR_lj",(100, 0, 2*3.142)],
    "el_mother_id": ["el_mother_id",(51,-25,25)],
    }

sel_2j0t = "n_eles == 1 & n_jets == 2 & n_tags == 0"
sel_2j1t = "n_eles == 1 & n_jets == 2 & n_tags == 1 "
sel_3j1t = "n_eles == 1 & n_jets == 3 & n_tags == 1"
sel_3j2t = "n_eles == 1 & n_jets == 3 & n_tags == 2"

sel_ele = "el_mva > 0.9 & el_pt > 30 & deltaR_bj > 0.3 & deltaR_lj > 0.3"
sel_ele_antiiso = "el_pt > 30 & deltaR_bj > 0.3 & deltaR_lj > 0.3"

muon_veto = "n_muons == 0"

trigger = "( (HLT_Ele27_WP80_v10 ==1) || (HLT_Ele27_WP80_v11 == 1) || (HLT_Ele27_WP80_v9==1) || (HLT_Ele27_WP80_v8==1) )"

sel_met = "met > 45"
sel_topm = "top_mass > 130 & top_mass < 220"
sel_eta = "abs(eta_lj) > 2.5" 

cuts = {
    "2j0t_nomet": "(" + sel_2j0t + "&" + muon_veto + "&" + sel_ele + "&" + sel_topm + "&" + sel_eta  +")",
    "2j0t_nomet_antiiso": "(" + sel_2j0t + "&" + sel_ele_antiiso + "&" + muon_veto + "&" + sel_topm + "&" + sel_eta  + ")",
    
    "2j0t": "(" + sel_2j0t + "&" + sel_met + ")",

    "2j1t_nomet_antiiso": "(" + sel_2j1t + "&" + sel_ele_antiiso + "&" + muon_veto + ")",
    "2j1t_nomet": "(" + sel_2j1t + "&" + sel_ele + "&" + muon_veto  + ")",
   

    "final_nomet": "(" + sel_2j1t + "&" + muon_veto  + "&" + sel_ele + "&" + sel_topm + "&" + sel_eta  + ")",
    "final_nomet_antiiso": "(" + sel_2j1t + "&" + sel_ele_antiiso + "&" + muon_veto  + "&" + sel_topm + "&" + sel_eta  + ")",

    "2j1t": "("  + sel_2j1t + "&" + sel_met + "&" + muon_veto + "&" + sel_ele + ")",
    "2j1t_antiiso": "(" + sel_2j1t + "&" + sel_ele_antiiso + "&" + sel_met + "&" + muon_veto + ")",


    "3j1t": "(" + sel_3j1t + "&" + sel_met + ")",
    "3j2t": "(" + sel_3j2t + "&" + sel_met + ")",

    "final": "(" + sel_2j1t + "&" + sel_met + "&" + sel_topm + "&" + sel_eta + "&" + muon_veto  +  "&" + sel_ele + ")",
    "final_antiiso": "(" + sel_2j1t + "&" + sel_ele_antiiso + "&" + sel_met + "&" + sel_topm + "&" + sel_eta + "&" + muon_veto  + ")"
    
    }
