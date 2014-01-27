#!/usr/bin/python
import os
import math

def convertRel(value):
    return str(round(value,1))

def convertDelta(value):
    return str(round(value,3))

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

["sys_mcstat","Simulation statistics"]




]

asymmetryDict={}
for sys in systematics:
    if os.path.exists(sys[0]):
        f=open(os.path.join(sys[0],"asymmetry.txt"),"r")
        info={}
        for line in f:
            key,value=line.replace(" ","").replace("\n","").replace("\r","").split(",")
            info[key]=float(value)
        asymmetryDict[sys[0]]=info
    else:
        asymmetryDict[sys[0]]=False
        
latexTable=""
latexTable+="\\begin{tabular}{  |c||c|c||c|c| }  \n"

latexTable+="Uncertainty source  & $\\Delta A_l^{\\mu}$ & $\\Delta A_l^{\\mu}/A_l^{\\mu}$ (\\%) & $\\Delta A_l^{e}$ & $\\Delta A_l^{e}/A_l^{e}$ (\%) \\\\ \n" 
latexTable+="\\hline \n"
for sys in systematics:
    if sys[0]=="sys_nominal":
        continue
    if sys[0]=="hline":
         latexTable+="\\hline \n"
    if not asymmetryDict[sys[0]]:
        latexTable+=sys[1]+" & "
        latexTable+=" FIXME & "
        latexTable+=" FIXME & "
        latexTable+=" FIXME & "
        latexTable+=" FIXME & "
        latexTable+="\\\\ \n"
    else:
        asymmetryRMSMuon=asymmetryDict[sys[0]]["rms"]
        asymmetryNominalRMSMuon=asymmetryDict["sys_nominal"]["rms"]
        deltaAsymmetryMuon=math.sqrt(asymmetryNominalRMSMuon**2-asymmetryRMSMuon**2)
        deltaAsymmetryRelMuon=deltaAsymmetryMuon/asymmetryNominalRMSMuon
        asymmetryRMSElectron=0.0
        asymmetryNominalRMSElectron=0.0
        deltaAsymmetryElectron=math.sqrt(asymmetryNominalRMSElectron**2-asymmetryRMSElectron**2)
        deltaAsymmetryRelElectron=deltaAsymmetryElectron/asymmetryNominalRMSElectron
        
        latexTable+=sys[1]+" & "
        latexTable+=convertDelta(deltaAsymmetryMuon)+" & "
        latexTable+=convertRel(deltaAsymmetryRelMuon)+" & "
        latexTable+=convertDelta(deltaAsymmetryMuon)+" & "
        latexTable+=convertRel(deltaAsymmetryRelMuon)+" & "
        latexTable+="\\\\ \n"
latexTable+="\\end{tabular}\n"
out=open("sys.tex","w")
out.write(latexTable)
out.close()

