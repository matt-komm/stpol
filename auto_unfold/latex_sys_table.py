#!/usr/bin/python
import os

def cov(value):
    return str(round(value,3))

systematics=[
"nominal",
"sys_tchan",
"sys_wzjets",
"sys_top",
"sys_qcd",
"sys_En",
"sys_Res",
"sys_UnclusteredEn",
"sys_btaggingBC",
"sys_btaggingL",
"sys_wjets_flat",
"sys_wjets_shape"
#"sys_ttbar_scale",
#"sys_ttbar_matching"
]

asymmetryDict={}
for sys in systematics:
    f=open(os.path.join(sys,"asymmetry.txt"),"r")
    info={}
    for line in f:
        key,value=line.replace(" ","").replace("\n","").replace("\r","").split(",")
        info[key]=float(value)
    asymmetryDict[sys]=info
latexTable=""    
latexTable+="\\begin{tabular}{ l|| c c| c c}  \n"
latexTable+=" & \\multicolumn{2}{c|}{asymmetry} & \\\\ \n" 

latexTable+="systematic & mean & rms & abs. change & rel. change \\\\ \n" 
latexTable+="\\hline \n"
latexTable+="\\hline \n"
for sys in systematics:
        
    latexTable+=sys.replace("_"," ")+" & "
    latexTable+=cov(asymmetryDict[sys]["mean"])+" & "
    latexTable+=cov(asymmetryDict[sys]["rms"])+" & "
    latexTable+=cov(asymmetryDict[sys]["rms"]-asymmetryDict["nominal"]["rms"])+" & "
    latexTable+=cov(100.0*(asymmetryDict["nominal"]["rms"]-asymmetryDict[sys]["rms"])/asymmetryDict["nominal"]["rms"])+"\% \\\\ \n "
    latexTable+="\\hline \n"
latexTable+="\\end{tabular}\n"
out=open("sys.tex","w")
out.write(latexTable)
out.close()

