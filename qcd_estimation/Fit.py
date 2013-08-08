class Fit:
    def __init__(self, isMC = False, tags = 1, isSR = False, isSB = False, maxY = 9000, extra="", diffIso = False, jets=2):
        self.result = {}
        self.mtwMass_nonqcd=0
        self.mtwMass_nonqcd_uncert=0
        self.mtwMass_qcd=0
        self.mtwMass_qcd_uncert=0
        self.isMC = isMC
        self.isSR = isSR
        self.isSB = isSB
        self.tags = tags
        self.maxY = maxY
        self.extra = extra
        self.diffIso = diffIso
        self.isoCut = ""
        self.isoUpCut = ""
        self.isoDownCut = ""
        self.jets = jets
        self.nonqcd = None
        self.nonqcd_uncert = None
        self.qcd = None
        self.qcd_uncert = None
        self.qcd_histo = None
   
    def __str__(self):
        string = self.getTitle()+"\n" 
        string += "qcd = "+str(self.qcd)+ " +- " +str(self.qcd_uncert)+"\n"
        string += "nonqcd = "+str(self.nonqcd)+ " +- " +str(self.nonqcd_uncert)+"\n"
        string += str(self.result)
        return string

    def getLabel(self):
        label = self.getRegion()
        if self.isSR:
            label += "_SR"
        elif self.isSB:
            label += "_SB"         
        if self.isMC:
            label += "_MC"
        if len(self.extra)>0:
            label += "_"+self.extra
        return label
    
    def getTitle(self):
        label = self.getRegion()
        if self.isSR:
            label += ", SR"
        elif self.isSB:
            label += ", SB"         
        if self.isMC:
            label += ", MC"
        if len(self.extra)>0:
            label += "_"+self.extra
        return label
    
    def getRegion(self):
        label = str(self.jets)+"J_"+str(self.tags)+"T"
        return label
   
results = []
res_2J_0T = Fit(tags = 0, maxY=6000)
res_2J_1T = Fit(maxY = 1500)
res_2J_1T_SR = Fit(isSR = True, maxY = 1500)
res_2J_1T_SR_Mu = Fit(isSR = True, maxY = 200, extra="Mu")
res_2J_1T_SB = Fit(isSB = True, maxY = 400)
res_2J_0T_MC = Fit(isMC = True, tags = 0)
res_2J_1T_MC = Fit(isMC = True, maxY = 1500)
res_2J_1T_SR_MC = Fit(isMC = True, isSR = True, maxY = 1200)
res_2J_1T_SB_MC = Fit(isMC = True, isSB = True, maxY = 400)

res_2J_0T_mtwMass50 = Fit(tags = 0, extra="mtwMass50")
res_2J_1T_mtwMass50 = Fit(maxY = 1000, extra="mtwMass50")
res_2J_1T_SR_mtwMass50 = Fit(isSR = True, maxY = 1200, extra="mtwMass50")
res_2J_1T_SB_mtwMass50 = Fit(isSB = True, maxY = 400, extra="mtwMass50")
res_2J_0T_MC_mtwMass50 = Fit(isMC = True, tags = 0, extra="mtwMass50", maxY = 8000)
res_2J_1T_MC_mtwMass50 = Fit(isMC = True, maxY = 1000, extra="mtwMass50")
res_2J_1T_SR_MC_mtwMass50 = Fit(isMC = True, isSR = True, maxY = 600, extra="mtwMass50")
res_2J_1T_SB_MC_mtwMass50 = Fit(isMC = True, isSB = True, maxY = 400, extra="mtwMass50")

#results.append(res_2J_0T)
results.append(res_2J_1T)
results.append(res_2J_1T_SB)
results.append(res_2J_1T_SR)
#results.append(res_2J_1T_SR_Mu)
#results.append(res_2J_0T_MC)
results.append(res_2J_1T_MC)
results.append(res_2J_1T_SR_MC)
results.append(res_2J_1T_SB_MC)

#results.append(res_2J_0T_mtwMass50)
#results.append(res_2J_1T_mtwMass50)
#results.append(res_2J_1T_SB_mtwMass50)
results.append(res_2J_1T_SR_mtwMass50)
#results.append(res_2J_0T_MC_mtwMass50)
#results.append(res_2J_1T_MC_mtwMass50)
#results.append(res_2J_1T_SR_MC_mtwMass50)
#results.append(res_2J_1T_SB_MC_mtwMass50)


res_2J_0T_mtwMass20plus = Fit(tags = 0, extra="mtwMass20plus")
res_2J_1T_mtwMass20plus = Fit(maxY = 1000, extra="mtwMass20plus")
res_2J_1T_SR_mtwMass20plus = Fit(isSR = True, maxY = 1200, extra="mtwMass20plus")
res_2J_1T_SB_mtwMass20plus = Fit(isSB = True, maxY = 400, extra="mtwMass20plus")
res_2J_0T_MC_mtwMass20plus = Fit(isMC = True, tags = 0, extra="mtwMass20plus")
res_2J_1T_MC_mtwMass20plus = Fit(isMC = True, maxY = 1000, extra="mtwMass20plus")
res_2J_1T_SR_MC_mtwMass20plus = Fit(isMC = True, isSR = True, maxY = 500, extra="mtwMass20plus")
res_2J_1T_SB_MC_mtwMass20plus = Fit(isMC = True, isSB = True, maxY = 400, extra="mtwMass20plus")

res_2J_0T_mtwMass70 = Fit(tags = 0, extra="mtwMass70")
res_2J_1T_mtwMass70 = Fit(maxY = 1000, extra="mtwMass70")
res_2J_1T_SR_mtwMass70 = Fit(isSR = True, maxY = 1200, extra="mtwMass70")
res_2J_1T_SB_mtwMass70 = Fit(isSB = True, maxY = 400, extra="mtwMass70")
res_2J_0T_MC_mtwMass70 = Fit(isMC = True, tags = 0, extra="mtwMass70")
res_2J_1T_MC_mtwMass70 = Fit(isMC = True, maxY = 1000, extra="mtwMass70")
res_2J_1T_SR_MC_mtwMass70 = Fit(isMC = True, isSR = True, maxY = 600, extra="mtwMass70")
res_2J_1T_SB_MC_mtwMass70 = Fit(isMC = True, isSB = True, maxY = 400, extra="mtwMass70")

#results.append(res_2J_0T_mtwMass20plus)
#results.append(res_2J_1T_mtwMass20plus)
#results.append(res_2J_1T_SB_mtwMass20plus)
results.append(res_2J_1T_SR_mtwMass20plus)
#results.append(res_2J_0T_MC_mtwMass20plus)
#results.append(res_2J_1T_MC_mtwMass20plus)
#results.append(res_2J_1T_SR_MC_mtwMass20plus)
#results.append(res_2J_1T_SB_MC_mtwMass20plus)

#results.append(res_2J_0T_mtwMass70)
#results.append(res_2J_1T_mtwMass70)
#results.append(res_2J_1T_SB_mtwMass70)
results.append(res_2J_1T_SR_mtwMass70)
#results.append(res_2J_0T_MC_mtwMass70)
#results.append(res_2J_1T_MC_mtwMass70)
#results.append(res_2J_1T_SR_MC_mtwMass70)
#results.append(res_2J_1T_SB_MC_mtwMass70)

res_2J_0T_iso_0_3_plus = Fit(tags = 0, extra = "iso_0_3_plus")
res_2J_1T_iso_0_3_plus = Fit(maxY = 1000, extra = "iso_0_3_plus")
res_2J_1T_SR_iso_0_3_plus = Fit(isSR = True, maxY = 1200, extra = "iso_0_3_plus")
res_2J_1T_SB_iso_0_3_plus = Fit(isSB = True, maxY = 400, extra = "iso_0_3_plus")
res_2J_0T_MC_iso_0_3_plus = Fit(isMC = True, tags = 0, extra = "iso_0_3_plus")
res_2J_1T_MC_iso_0_3_plus = Fit(isMC = True, maxY = 1000, extra = "iso_0_3_plus")
res_2J_1T_SR_MC_iso_0_3_plus = Fit(isMC = True, isSR = True, maxY = 600, extra = "iso_0_3_plus")
res_2J_1T_SB_MC_iso_0_3_plus = Fit(isMC = True, isSB = True, maxY = 400, extra = "iso_0_3_plus")

res_2J_0T_iso_0_5_plus = Fit(tags = 0, extra = "iso_0_5_plus")
res_2J_1T_iso_0_5_plus = Fit(maxY = 1000, extra = "iso_0_5_plus")
res_2J_1T_SR_iso_0_5_plus = Fit(isSR = True, maxY = 1200, extra = "iso_0_5_plus")
res_2J_1T_SB_iso_0_5_plus = Fit(isSB = True, maxY = 400, extra = "iso_0_5_plus")
res_2J_0T_MC_iso_0_5_plus = Fit(isMC = True, tags = 0, extra = "iso_0_5_plus")
res_2J_1T_MC_iso_0_5_plus = Fit(isMC = True, maxY = 1000, extra = "iso_0_5_plus")
res_2J_1T_SR_MC_iso_0_5_plus = Fit(isMC = True, isSR = True, maxY = 600, extra = "iso_0_5_plus")
res_2J_1T_SB_MC_iso_0_5_plus = Fit(isMC = True, isSB = True, maxY = 400, extra = "iso_0_5_plus")

res_2J_0T_qcdneg = Fit(tags = 0, maxY = 4000, extra = "qcdneg")
res_2J_1T_qcdneg = Fit(maxY = 1200, extra = "qcdneg")
res_2J_1T_SR_qcdneg = Fit(isSR = True, maxY = 260, extra = "qcdneg")
res_2J_1T_SB_qcdneg = Fit(isSB = True, maxY = 140, extra = "qcdneg")

res_2J_0T_qcdpos = Fit(tags = 0, maxY = 5000, extra = "qcdpos")
res_2J_1T_qcdpos = Fit(maxY = 420, extra = "qcdpos")
res_2J_1T_SR_qcdpos = Fit(isSR = True, maxY = 280, extra = "qcdpos")
res_2J_1T_SB_qcdpos = Fit(isSB = True, maxY = 180, extra = "qcdpos")


#results.append(res_2J_0T_iso_0_3_plus)
#results.append(res_2J_1T_iso_0_3_plus)
#results.append(res_2J_1T_SB_iso_0_3_plus)
results.append(res_2J_1T_SR_iso_0_3_plus)
#results.append(res_2J_0T_MC_iso_0_3_plus)
#results.append(res_2J_1T_MC_iso_0_3_plus)
#results.append(res_2J_1T_SR_MC_iso_0_3_plus)
#results.append(res_2J_1T_SB_MC_iso_0_3_plus)

#results.append(res_2J_0T_iso_0_5_plus)
#results.append(res_2J_1T_iso_0_5_plus)
#results.append(res_2J_1T_SB_iso_0_5_plus)
results.append(res_2J_1T_SR_iso_0_5_plus)
#results.append(res_2J_0T_MC_iso_0_5_plus)
#results.append(res_2J_1T_MC_iso_0_5_plus)
#results.append(res_2J_1T_SR_MC_iso_0_5_plus)
#results.append(res_2J_1T_SB_MC_iso_0_5_plus)



"""results.append(res_2J_0T_qcdneg)
results.append(res_2J_1T_qcdneg)
results.append(res_2J_1T_SB_qcdneg)
results.append(res_2J_1T_SR_qcdneg)
results.append(res_2J_0T_qcdpos)
results.append(res_2J_1T_qcdpos)
results.append(res_2J_1T_SB_qcdpos)
results.append(res_2J_1T_SR_qcdpos)"""



