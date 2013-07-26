class FitConfig():
    """
    Constructor for FitConfig
    Default values valid for fitting in final muon selection are provided
    If you want to change just a few values, using setters is a good idea
    """
    def __init__(self,
            name = "final_selection",    #name will go into output file names 
            trigger = "(HLT_IsoMu24_eta2p1_v11==1 || HLT_IsoMu24_eta2p1_v12==1 || HLT_IsoMu24_eta2p1_v13==1 || HLT_IsoMu24_eta2p1_v14==1 || HLT_IsoMu24_eta2p1_v15==1 || HLT_IsoMu24_eta2p1_v16==1 || HLT_IsoMu24_eta2p1_v17==1)",
          weightMC = "b_weight_nominal*pu_weight*muon_IDWeight*muon_IsoWeight*muon_TriggerWeight*wjets_mg_flavour_flat_weight*wjets_mg_flavour_shape_weight",
            baseCuts = "n_jets == 2 && n_tags == 1 && n_veto_ele==0 && n_veto_mu==0",
            jetCuts = "pt_lj>40 && pt_bj>40 && rms_lj<0.025",
            finalCuts = "abs(eta_lj)>2.5 && top_mass < 220 && top_mass > 130",
            isolationCut = "mu_iso<0.12",
            antiIsolationCut = "mu_iso>0.2 && mu_iso<0.5", 
            antiIsolationCutDown = "mu_iso>0.2 && mu_iso<0.45", 
            antiIsolationCutUp = "mu_iso>0.22 && mu_iso<0.55",
            extraAntiIsoCuts = "deltaR_lj > 0.3 && deltaR_bj > 0.3",
            finalCutsAntiIso = "abs(eta_lj)>2.5 && top_mass < 220 && top_mass > 130",
            useMCforQCDTemplate = False,    #Take QCD template from MC?
            weightQCD = "pu_weight*muon_IDWeight*muon_IsoWeight*muon_TriggerWeight" #Only needed if taking QCD template from MC           
        ):
        self.name = name
        self.setTrigger(trigger)
        self.setWeightMC(weightMC)
        self.setWeightQCD(weightQCD)
    
        self.setBaseCuts(baseCuts)
        self.setJetCuts(jetCuts)
        self.setFinalCuts(finalCuts)
        self.setIsolationCut(isolationCut)
        self.setAntiIsolationCut(antiIsolationCut)
        self.setAntiIsolationCutUp(antiIsolationCutUp)
        self.setAntiIsolationCutDown(antiIsolationCutDown)
        self.setExtraAntiIsoCuts(extraAntiIsoCuts)
        self.setFinalCutsAntiIso(finalCutsAntiIso)
        self.isMC = useMCforQCDTemplate

        self.calcCuts()
    
    """
    Setters for different cuts.
    Remember to call calcCuts after finishing with the setters.
    (Unless you have a special reason not to -  then you have to compose the final cuts yourself)
    """  
    def setTrigger(self, trigger):
        self._trigger = trigger

    def setWeightMC(self, weight):
        self._weightMC = weight

    def setWeightQCD(self, weight):
        self._weightQCD = weight

    def setBaseCuts(self, cut):
        self._baseCuts = cut

    def setJetCuts(self, cut):
        self._jetCuts = cut

    def setFinalCuts(self, cut):
        self._finalCuts = cut

    def setFinalCutsAntiIso(self, cut):
        self._finalCutsAntiIso = cut

    def setIsolationCut(self, cut):
        self._isolationCut = cut

    def setAntiIsolationCut(self, cut):
        self._antiIsolationCut = cut
    
    def setAntiIsolationCutUp(self, cut):
        self._antiIsolationCutUp = cut

    def setAntiIsolationCutDown(self, cut):
        self._antiIsolationCutDown = cut    
    
    def setExtraAntiIsoCuts(self, cut):
        self._extraAntiIsoCuts = cut

    """
    Calculates all necessary cuts from the base values
    In case you need some special configuration, you can change the values manually afterwards
    """
    def calcCuts(self):
        isoCuts = self._trigger + "*(" + self._baseCuts + " && " + self._jetCuts + " && " + self._finalCuts + " && " + self._isolationCut +")"
        self.isoCutsMC = self._weightMC + "*(" + isoCuts +")"
        self.isoCutsData = isoCuts
        self.isoCutsQCD = self._weightQCD + "*(" + isoCuts +")"

        antiIsoCuts = self._trigger + "*(" + self._baseCuts + " && " + self._jetCuts + " && " + self._finalCutsAntiIso + " && " + self._extraAntiIsoCuts + " && " + self._antiIsolationCut +")"
        antiIsoCutsDown = self._trigger + "*(" + self._baseCuts + " && " + self._jetCuts + " && " + self._finalCutsAntiIso + " && " + self._extraAntiIsoCuts + " && " + self._antiIsolationCutDown +")"
        antiIsoCutsUp = self._trigger + "*(" + self._baseCuts + " && " + self._jetCuts + " && " + self._finalCutsAntiIso + " && " + self._extraAntiIsoCuts + " && " + self._antiIsolationCutUp +")"
        self.antiIsoCutsMC = self._weightMC + "*(" + antiIsoCuts +")"
        self.antiIsoCutsMCIsoDown = self._weightMC + "*(" + antiIsoCutsDown +")"
        self.antiIsoCutsMCIsoUp = self._weightMC + "*(" + antiIsoCutsUp +")"
        self.antiIsoCutsData = antiIsoCuts
        self.antiIsoCutsDataIsoDown = antiIsoCutsDown
        self.antiIsoCutsDataIsoUp = antiIsoCutsUp
        
        self.antiIsoCutsQCD = self._weightQCD + "*(" + antiIsoCuts +")"
        self.antiIsoCutsQCDIsoDown = self._weightQCD + "*(" + antiIsoCutsDown +")"
        self.antiIsoCutsQCDIsoUp = self._weightQCD + "*(" + antiIsoCutsUp +")"
        

    def __str__(self):
        string = "Fitconf " + self.name + "\n" 
        string += "Iso cuts MC: " + self.isoCutsMC + "\n" 
        string += "Iso cuts Data: " + self.isoCutsData + "\n" 
        string += "Antiiso cuts MC: " + self.antiIsoCutsMC + "\n" 
        string += "Antiiso cuts MC iso down: " + self.antiIsoCutsMCIsoDown + "\n" 
        string += "Antiiso cuts MC iso up: " + self.antiIsoCutsMCIsoUp + "\n" 
        string += "Antiiso cuts Data: " + self.antiIsoCutsData + "\n" 
        string += "Antiiso cuts Data iso down: " + self.antiIsoCutsDataIsoDown + "\n" 
        string += "Antiiso cuts Data iso up: " + self.antiIsoCutsDataIsoUp + "\n" 
        string += "Antiiso cuts QCD MC: " + self.antiIsoCutsQCD + "\n" 
        string += "Antiiso cuts QCD MC iso down: " + self.antiIsoCutsQCDIsoDown + "\n" 
        string += "Antiiso cuts QCD MC iso down: " + self.antiIsoCutsQCDIsoUp + "\n" 
        return string
