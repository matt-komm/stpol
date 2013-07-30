from FitConfig import *

def systematics_cuts_ele():
    cuts = {}

    #Always set anti-isolation cuts, as the default is disabled for systematic checks
    cutsBasic = FitConfig("2J1T")
    cutsBasic.setFinalCuts("1") # estimate before final cuts of eta and top_mass
    cutsBasic.setAntiIsolationCut("el_iso>0.15 && el_iso<0.5")
    cutsBasic.setAntiIsolationCutUp("el_iso>0.17 && el_iso<0.55")
    cutsBasic.setAntiIsolationCutDown("el_iso>0.13 && el_iso<0.45")
    cutsBasic.calcCuts()
    cuts["2J1T"] = cutsBasic

    cuts_iso_015_02 = FitConfig("2J1T_iso_015_02")
    cuts_iso_015_02.setFinalCuts("1")
    cuts_iso_015_02.setAntiIsolationCut("el_iso>0.15 && el_iso<0.2")
    cuts_iso_015_02.setAntiIsolationCutUp("el_iso>0.17 && el_iso<0.22")
    cuts_iso_015_02.setAntiIsolationCutDown("el_iso>0.13 && el_iso<0.18")
    cuts_iso_015_02.calcCuts()
    cuts["2J1T_iso_015_02"] = cuts_iso_015_02 

    cuts_iso_03_05 = FitConfig("2J1T_iso_03_05")
    cuts_iso_03_05.setFinalCuts("1" )
    cuts_iso_03_05.setAntiIsolationCut("el_iso>0.2 && el_iso<0.5")
    cuts_iso_03_05.setAntiIsolationCutUp("el_iso>0.22 && el_iso<0.55")
    cuts_iso_03_05.setAntiIsolationCutDown("el_iso>0.18 && el_iso<0.45")
    cuts_iso_03_05.calcCuts()
    cuts["2J1T_iso_03_05"] = cuts_iso_03_05

    return cuts
    
def systematics_cuts_mu():
    cuts = {}

    cutsBasic = FitConfig("2J1T")
    cutsBasic.setFinalCuts("1") #estimate systematics before final cuts
    cutsBasic.calcCuts()
    cuts["2J1T"] = cutsBasic

    cuts_iso_02_03 = FitConfig("2J1T_iso_02_03")
    cuts_iso_02_03.setFinalCuts("1")
    cuts_iso_02_03.setAntiIsolationCut("mu_iso>0.2 && mu_iso<0.3")
    cuts_iso_02_03.setAntiIsolationCutUp("mu_iso>0.22 && mu_iso<0.33")
    cuts_iso_02_03.setAntiIsolationCutDown("mu_iso>0.18 && mu_iso<0.27")
    cuts_iso_02_03.calcCuts()
    cuts["2J1T_iso_02_03"] = cuts_iso_02_03
                     
    cuts_iso_03_05 = FitConfig("2J1T_iso_03_05")
    cuts_iso_03_05.setFinalCuts("1" )
    cuts_iso_03_05.setAntiIsolationCut("mu_iso>0.3 && mu_iso<0.5")
    cuts_iso_03_05.setAntiIsolationCutUp("mu_iso>0.33 && mu_iso<0.55")
    cuts_iso_03_05.setAntiIsolationCutDown("mu_iso>0.27 && mu_iso<0.45")
    cuts_iso_03_05.calcCuts()
    cuts["2J1T_iso_03_05"] = cuts_iso_03_05

    return cuts
