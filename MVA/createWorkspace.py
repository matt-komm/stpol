# Import necessary libraries and data
from ROOT import *
from copy import copy
from plots.common.cross_sections import xs
from file_names import dataFiles_ele, dataFiles_mu, mcFiles, dataLumi_ele, dataLumi_mu
from plots.common.colors import sample_colors_same

# Make RooFit talk less
msgservice = RooMsgService.instance()
msgservice.setGlobalKillBelow(RooFit.WARNING)

# Choose between electron / muon channel fitting
#sample = "mu"
#fn_data = sample+"/SingleMu.root"
sample = "ele"
fn_data = sample+"/SingleEle.root"

# Cut string by what to reduce events
cutstring='n_eles == 1 & n_jets == 2 & n_tags == 1 & met > 45 & top_mass > 130 & top_mass < 220 & n_muons == 0 & el_mva > 0.9 & el_pt > 30 & deltaR_bj > 0.3 & deltaR_lj > 0.3'

cutVars=['n_eles','n_jets','n_tags','met','top_mass','n_muons','el_mva','el_pt','deltaR_bj','deltaR_lj']
cutV={}
cutVArgSet = RooArgSet()
for i in cutVars:
    cutV[i]=RooRealVar(i,i,-1000,1000)
    cutVArgSet.add(cutV[i])

# Select used luminosity
lumi=dataLumi_ele['Ele']
if sample == "mu": lumi=dataLumi_mu['Mu']

# declare variables that we plan to use
eta_lj = RooRealVar("eta_lj","Eta of light jet",-5,5)
cos_th = RooRealVar("cos_theta","cos(#theta)",-1,1)
eta_lj_abs = RooFormulaVar("eta_lj_abs","|eta_lj|","fabs(eta_lj)",RooArgList(eta_lj))

# Which weights we use?
usePU = true
useB = true
useLepTrig = true
useLepID = true
useLepIso = false

# To compute accurate weight we need to load from the tree also the weights in question
wVarList = RooArgList()
pu_weight=RooRealVar()
b_weight=RooRealVar()
lepTrig_weight=RooRealVar()
lepID_weight=RooRealVar()
lepIso_weight=RooRealVar()

weightString = ""
if usePU:
    pu_weight = RooRealVar("pu_weight","Pileup weight",0,10)
    wVarList.add(pu_weight)
    weightString += "pu_weight*"

if useB:
    b_weight = RooRealVar("b_weight_nominal","B weight",0,10)
    wVarList.add(b_weight)
    weightString += "b_weight_nominal*"

if useLepTrig:
    cs = "electron_triggerWeight"
    if sample == "mu":
        cs="muon_triggerWeight"
    lepTrig_weight = RooRealVar(cs,cs,0,10)
    wVarList.add(lepTrig_weight)
    weightString += cs+"*"

if useLepID:
    cs = "electron_IDWeight"
    if sample == "mu":
        cs="muon_IDWeight"
    lepID_weight = RooRealVar(cs,cs,0,10)
    wVarList.add(lepID_weight)
    weightString += cs+"*"

if useLepIso and sample == "mu":
    lepIso_weight = RooRealVar("muon_IsoWeight","Muon isolation weight",0,10)
    wVarList.add(lepIso_weight)
    weightString += "muon_IsoWeight*"

argSet = RooArgSet(eta_lj,cos_th)
argSet.add(RooArgSet(wVarList))
argSet.add(cutVArgSet)
f={}
t={}
weight={}
args={}
ds={}

def getDataset(name,filename):
    """ Function will read in the dataset tree, calculate weights and return relevant data """
    f[name] = TFile(sample+"/"+filename)
    t[name] = f[name].Get("trees/Events")
    nh = f[name].Get("trees/count_hist")
    norg = nh.GetBinContent(1)
    xssf = xs[name]*lumi / norg
    w = RooFormulaVar("w_"+name,"event weight",weightString+str(xssf),wVarList)
    print "Sample:",name,"using weightstring:",weightString+str(xssf)
    dstmp=RooDataSet("data","dataset",t[name],argSet,cutstring)
    weight[name]=dstmp.addColumn(w)
    dstmp.addColumn(eta_lj_abs)
    args[name]=copy(argSet)
    args[name].add(weight[name])
    args[name].add(eta_lj_abs)
    ds[name]=RooDataSet(name+"_data",name+" dataset",dstmp,args[name],cutstring,"w_"+name)
    ds[name].Print()

#fn_data="ele/T_s.root"
f['data']=TFile(fn_data)
t['data']=f['data'].Get("trees/Events")
ds['data']=RooDataSet("data","actual data",t['data'],argSet,cutstring)
ds['data'].addColumn(eta_lj_abs)

ds['data'].Print()

for key in mcFiles:
    #for key in klist:
    if sample == "mu" and (key[-5:] == "BCtoE" or key[-10:] == "EMEnriched") or key[0:5] == "GJets":
        continue
    if sample == "ele" and key == "QCDMu":
        continue
    getDataset(key,mcFiles[key])


# How to merge the samples into processes
merging={
    'signal':['T_t_ToLeptons','Tbar_t_ToLeptons'],
    'stopother':['T_s', 'T_tW', 'Tbar_s', 'Tbar_tW'],
    'ttbar':['TTJets_FullLept', 'TTJets_SemiLept'],
    'wjets':['W1Jets_exclusive', 'W2Jets_exclusive', 'W3Jets_exclusive', 'W4Jets_exclusive'],
    'diboson':['DYJets','WW', 'WZ', 'ZZ'],
    'qcd':['GJets1', 'GJets2', 'QCDMu', 'QCD_Pt_170_250_BCtoE', 'QCD_Pt_170_250_EMEnriched', 'QCD_Pt_20_30_BCtoE', 'QCD_Pt_20_30_EMEnriched', 'QCD_Pt_250_350_BCtoE', 'QCD_Pt_250_350_EMEnriched', 'QCD_Pt_30_80_BCtoE', 'QCD_Pt_30_80_EMEnriched', 'QCD_Pt_350_BCtoE', 'QCD_Pt_350_EMEnriched', 'QCD_Pt_80_170_BCtoE', 'QCD_Pt_80_170_EMEnriched']
}
cols={'signal':kRed,'stopother':kPink,'diboson':kOrange,'wjets':kYellow,'ttbar':kGreen,'qcd':kGray}

# Create RooWorkspace to save the output datasets
ws=RooWorkspace("ws")
getattr(ws,'import')(ds['data'])

# Create the actual merges
for k in merging.keys():
    for dataset in merging[k]:
        if dataset in ds.keys():
            if k in ds.keys():
                ds[k].append(ds[dataset])
            else:
                ds[k]=copy(ds[dataset])
                ds[k].SetNameTitle(k,k+" dataset")
    ds[k].plotOn(frame,RooFit.MarkerColor(cols[k]))
    getattr(ws,'import')(ds[k])

ws.writeToFile('workspace.root')