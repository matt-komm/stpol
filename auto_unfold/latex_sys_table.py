#!/usr/bin/python
import os
import math

systematics=[
["sys_nominal",""],


["sys_stat","statistical"],
["hline"],
["sys_leptonID","lepton ID"],
["sys_leptonIso","lepton isolation"],
["sys_leptonTrigger","lepton trigger"],
["sys_pileup","pileup"],
["sys_btaggingBC","b-tagging"],
["sys_btaggingL","mistagging"],


["sys_ttbar_scale","$Q^2$, \\ttbar"],
["sys_topPt","top \\pt, \\ttbar"],
["sys_ttbar_matching","Matching \\ttbar"],


["sys_wjets_shape","\\wjets\\ modeling"],
["sys_wjets_flat","\\wjets\\ flavour"],

["sys_En","JES"],
["sys_Res","JER"],
["sys_UnclusteredEn","unclustered \\MET"],
["sys_tchan_scale","$Q^2$, signal"],
["sys_wzjets_scale","$Q^2$, \\wjets"],

["sys_comphep","signal generator"],

["sys_pdf","PDF"],

["sys_tchan","signal normalization"],
["sys_top","top background normalization"],
["sys_wzjets","W/Z+jets normalization"],
["sys_qcd","QCD normalization"],

["sys_mcstat","simulation statistics"],
["hline"],
["sys_totalsys","total systematics"]


]

def convertBias(value):
    if value<0.001:
        return "$<0$ & $001$"
    #return "$"+str(round(value,3))+"$"
    valuePre,valuePost= ("%4.3f" % (value)).split(".")
    return "$"+valuePre+"$ & $"+valuePost+"$"

def convertDelta(value):
    if value<0.001:
        return "$<0$ & $001$"
    #return "$"+str(round(value,3))+"$"
    valuePre,valuePost= ("%4.3f" % (value)).split(".")
    return "$"+valuePre+"$ & $"+valuePost+"$"
    

    
def readAsymmetries(targetDict,path):
    for sys in systematics:
        if os.path.exists(os.path.join(path,sys[0],"asymmetry.txt")):
            
            f=open(os.path.join(path,sys[0],"asymmetry.txt"),"r")
            info={"path":path}
            for line in f:
                key,value=line.replace(" ","").replace("\n","").replace("\r","").split(",")
                info[key]=float(value)
            print "reading... ",os.path.join(path,sys[0],"asymmetry.txt"),info["mean"],info["rms"]
            targetDict[sys[0]]=info
            f.close()
        else:
            targetDict[sys[0]]=False
        
def printResult(asymmetryDict,sys):
    latexTable=""
    if not asymmetryDict[sys[0]]:
        latexTable+="FIX & ME & FIX & ME"
    else:
        asymmetryMean=asymmetryDict[sys[0]]["mean"]
        asymmetryNominalMean=asymmetryDict["sys_nominal"]["mean"]
        asymmetryRMS=asymmetryDict[sys[0]]["rms"]
        asymmetryNominalRMS=asymmetryDict["sys_nominal"]["rms"]
        deltaAsymmetryMean=asymmetryMean-asymmetryNominalMean
        deltaAsymmetryRMS=math.sqrt(math.fabs(asymmetryNominalRMS**2-asymmetryRMS**2))
        latexTable+=convertBias(deltaAsymmetryMean)+" & "
        latexTable+=convertDelta(deltaAsymmetryRMS)
    return latexTable
    
    
def printResultDeltaOnly(asymmetryDict,sys):
    latexTable=""
    if not asymmetryDict[sys[0]]:
        latexTable+="FIX & ME"
    else:
        asymmetryRMS=asymmetryDict[sys[0]]["rms"]
        asymmetryNominalRMS=asymmetryDict["sys_nominal"]["rms"]
        deltaAsymmetryRMS=math.sqrt(math.fabs(asymmetryNominalRMS**2-asymmetryRMS**2))
        latexTable+=convertDelta(deltaAsymmetryRMS)
    return latexTable

asymmetryMuonDict={}
asymmetryElectronDict={}
readAsymmetries(asymmetryMuonDict,"muon")
readAsymmetries(asymmetryElectronDict,"electron")



        
latexTable=""
latexTable+="\\begin{tabular}{  |c|| r@{.}l | r@{.}l || r@{.}l | r@{.}l | }  \n"
latexTable+="\\hline \n"
latexTable+="Uncertainty source  & \\multicolumn{2}{c |}{ bias $\\langle A_l^{\\mu} \\rangle$ } & \\multicolumn{2}{c ||}{ $\\delta A_l^{\\mu}$ } & \\multicolumn{2}{c |}{ bias $\\langle A_l^{e}\\rangle$ } & \\multicolumn{2}{c |}{ $\\delta A_l^{e}$ } \\\\ \n" 
latexTable+="\\hline \n"
for sys in systematics:
    if sys[0]=="sys_nominal":
        continue
    if sys[0]=="hline":
        latexTable+="\\hline \n"
    else:
        print "add row: ",sys[1]
        latexTable+=sys[1]+" & "
        latexTable+=printResult(asymmetryMuonDict,sys)
        latexTable+=" & "
        latexTable+=printResult(asymmetryElectronDict,sys)
        latexTable+="\\\\ \n"

latexTable+="\\hline \n"
latexTable+="total & \\multicolumn{2}{c |}{}"
latexTable+=" & "+convertDelta(asymmetryMuonDict["sys_nominal"]["rms"])
latexTable+=" & \\multicolumn{2}{c |}{} & "+convertDelta(asymmetryElectronDict["sys_nominal"]["rms"])
latexTable+="\\\\ \n"
latexTable+="\\hline \n"
latexTable+="\\end{tabular}\n"
out=open("sysAN.tex","w")
out.write(latexTable)
out.close()



latexTable=""
latexTable+="\\begin{tabular}{  |c|| r@{.}l || r@{.}l | }  \n"
latexTable+="\\hline \n"
latexTable+="Uncertainty source  & \\multicolumn{2}{c ||}{ $\\delta A_l^{\\mu}$ } & \\multicolumn{2}{c |}{ $\\delta A_l^{e}$ } \\\\ \n" 
latexTable+="\\hline \n"
for sys in systematics:
    if sys[0]=="sys_nominal":
        continue
    if sys[0]=="hline":
        latexTable+="\\hline \n"
    else:
        print "add row: ",sys[1]
        latexTable+=sys[1]+" & "
        latexTable+=printResultDeltaOnly(asymmetryMuonDict,sys)
        latexTable+=" & "
        latexTable+=printResultDeltaOnly(asymmetryElectronDict,sys)
        latexTable+="\\\\ \n"

latexTable+="\\hline \n"
latexTable+="total "
latexTable+=" & "+convertDelta(asymmetryMuonDict["sys_nominal"]["rms"])
latexTable+=" & "+convertDelta(asymmetryElectronDict["sys_nominal"]["rms"])
latexTable+="\\\\ \n"
latexTable+="\\hline \n"
latexTable+="\\end{tabular}\n"
out=open("sysPAS.tex","w")
out.write(latexTable)
out.close()

