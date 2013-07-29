from FitConfig import *

def systematics_cuts():
    cuts = {}
    cutsFinal = FitConfig("2J_1T_SR")
    cuts["2J_1T_SR"] = cutsFinal

    #TODO change append statements as above
    """cutsSB = FitConfig("2J_1T_SB")
    cutsSB.setFinalCuts("abs(eta_lj)>2.5 && (top_mass > 220 || top_mass < 130)")
    cutsSB.calcCuts()
    cuts.append(cutsSB)

    cuts2J1T = FitConfig("2J_1T")
    cuts2J1T.setFinalCuts("abs(eta_lj)>2.5")
    cuts2J1T.calcCuts()
    cuts.append(cuts2J1T)

    cutsMtwMass50 = FitConfig("2J_1T_m_T_50minus")
    cutsMtwMass50.setFinalCuts("abs(eta_lj)>2.5 && top_mass < 220 && top_mass > 130 && mt_mu < 50")
    cutsMtwMass50.calcCuts()
    cuts.append(cutsMtwMass50)

    cutsMtwMass70 = FitConfig("2J_1T_m_T_70minus")
    cutsMtwMass70.setFinalCuts("abs(eta_lj)>2.5 && top_mass < 220 && top_mass > 130 && mt_mu < 70")
    cutsMtwMass70.calcCuts()
    cuts.append(cutsMtwMass70)

    cutsMtwMass20plus = FitConfig("2J_1T_m_T_20plus")
    cutsMtwMass20plus.setFinalCuts("abs(eta_lj)>2.5 && top_mass < 220 && top_mass > 130 && mt_mu > 20")
    cutsMtwMass20plus.calcCuts()
    cuts.append(cutsMtwMass20plus)

    cuts_iso_0_2_plus = FitConfig("2J_1T_SR_iso_0_2_plus")
    cuts_iso_0_2_plus.setAntiIsolationCut("mu_iso>0.22")
    cuts_iso_0_2_plus.setAntiIsolationCutUp("mu_iso>0.242")
    cuts_iso_0_2_plus.setAntiIsolationCutDown("mu_iso>0.2")
    cuts_iso_0_2_plus.calcCuts()
    cuts.append(cuts_iso_0_2_plus)    
    
    cuts_iso_0_3_plus = FitConfig("2J_1T_SR_iso_0_3_plus")
    cuts_iso_0_3_plus.setAntiIsolationCut("mu_iso>0.3")
    cuts_iso_0_3_plus.setAntiIsolationCutUp("mu_iso>0.33")
    cuts_iso_0_3_plus.setAntiIsolationCutDown("mu_iso>0.27")
    cuts_iso_0_3_plus.calcCuts()
    cuts.append(cuts_iso_0_3_plus)

    cuts_iso_0_5_plus = FitConfig("2J_1T_SR_iso_0_5_plus")
    cuts_iso_0_5_plus.setAntiIsolationCut("mu_iso>0.5")
    cuts_iso_0_5_plus.setAntiIsolationCutUp("mu_iso>0.55")
    cuts_iso_0_5_plus.setAntiIsolationCutDown("mu_iso>0.45")
    cuts_iso_0_5_plus.calcCuts()
    cuts.append(cuts_iso_0_5_plus)

    cuts_iso_0_2_to_0_5 = FitConfig("2J_1T_SR_iso_0_2_to_0_5")
    cuts_iso_0_2_to_0_5.setAntiIsolationCut("mu_iso>0.22 && mu_iso<0.5")
    cuts_iso_0_2_to_0_5.setAntiIsolationCutUp("mu_iso>0.242 && mu_iso<0.55")
    cuts_iso_0_2_to_0_5.setAntiIsolationCutDown("mu_iso>0.2 && mu_iso<0.45")
    cuts_iso_0_2_to_0_5.calcCuts()
    cuts.append(cuts_iso_0_2_to_0_5)
    """
    """cuts2J0T = FitConfig("2J_0T_SR")
    cuts2J0T.setBaseCuts("n_jets == 2 && n_tags == 0")
    cuts2J0T.calcCuts()
    cuts.append(cuts2J0T)"""
    """cutsMC = FitConfig("2J_1T_SR_MC")
    cutsMC.isMC = True
    cuts.append(cutsMC)
    """

    return cuts
