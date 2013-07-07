# Import necessary libraries and data
from ROOT import *
from copy import copy
from plots.common.cross_sections import xs
from file_names import dataFiles_ele, dataFiles_mu, mcFiles, dataLumi_ele, dataLumi_mu
from plots.common.colors import sample_colors_same

# Choose between electron / muon channel fitting
#sample = "mu"
#fn_data = sample+"/SingleMu.root"
sample = "ele"
fn_data = sample+"/SingleEle.root"

# Cut string by what to reduce events
cutstring='n_eles == 1 & n_jets == 2 & n_tags == 1 & n_muons == 0 & el_mva > 0.9 & el_pt > 30 & deltaR_bj > 0.3 & deltaR_lj > 0.3'
cut = TCut(cutstring)

# not used cutstring part:
#cutstring_other="met > 45 & top_mass > 130 & top_mass < 220"

# Select used luminosity
lumi=dataLumi_ele['Ele']
if sample == "mu": lumi=dataLumi_mu['Mu']

# Which weights we use?
usePU = true
useB = true
useLepTrig = true
useLepID = true
useLepIso = false

# To compute accurate weight we need to load from the tree also the weights in question
weightString = ""
if usePU:
    weightString += "pu_weight*"

if useB:
    weightString += "b_weight_nominal*"

if useLepTrig:
    cs = "electron_triggerWeight"
    if sample == "mu":
        cs="muon_triggerWeight"
    weightString += cs+"*"

if useLepID:
    cs = "electron_IDWeight"
    if sample == "mu":
        cs="muon_IDWeight"
    weightString += cs+"*"

if useLepIso and sample == "mu":
    weightString += "muon_IsoWeight*"

weightString = weightString[:-1]

t={}
f={}
w={}

def getDataset(name,filename):
    """ Function will read in the dataset tree, calculate weights and return relevant data """
    f[name] = TFile("../step3_latest/"+sample+"/"+filename)
    t[name] = f[name].Get("trees/Events")
    nh = f[name].Get("trees/count_hist")
    norg = nh.GetBinContent(1)
    w[name] = xs[name]*lumi / norg


for key in mcFiles:
    #for key in klist:
    if sample == "mu" and (key[-5:] == "BCtoE" or key[-10:] == "EMEnriched") or key[0:5] == "GJets":
        continue
    if sample == "ele" and key == "QCDMu":
        continue
    getDataset(key,mcFiles[key])

signal=['T_t_ToLeptons','Tbar_t_ToLeptons']

# Create output file
outf = TFile('TMVA.root','RECREATE')

# Initialize TMVA factory
factory=TMVA.Factory("stop_"+sample,outf,"Transformations=I;N;D")

# Which particle do we use for pt, eta etc
prt='el'
if sample=='mu': prt='mu'

# Let's define what variables we want to use for signal discrimination
factory.AddVariable("met",'D')
factory.AddVariable("top_mass",'D')
factory.AddVariable("eta_lj",'D')
#factory.AddVariable("eta_bj",'D')
#factory.AddVariable(prt+"_pt",'D')
#factory.AddVariable(prt+"_charge",'D')
#factory.AddVariable("pt_bj",'D')
#factory.AddVariable("pt_lj",'D')

print "Skimming now"
# Skim the trees
st={}
for k in t.keys():
    print "Skimming:",k
    st[k]=t[k].CopyTree(cutstring)

# Now let's add signal and background trees with proper weights
for k in st.keys():
    print "Adding trees to MVA:",k
    if st[k].GetEntries():
        if k in signal:
            factory.AddSignalTree(st[k],w[k])
        else:
            factory.AddBackgroundTree(st[k],w[k])

# Define what is used as per-event weight
factory.SetWeightExpression(weightString)

# Prepare training and testing
factory.PrepareTrainingAndTestTree(TCut(),TCut(),
               "NormMode=None:"\
               "NTrain_Signal=1000:"\
               "NTrain_Background=5000:"\
               "V")

# Now let's book an MVA method
factory.BookMethod(TMVA.Types.kBDT,
                   "BDT",
                   "BoostType=AdaBoost:"\
                   "NTrees=50:"\
                   "nCuts=-1")

factory.BookMethod( TMVA.Types.kMLP,
                   "MLP",
                   "!H:!V:"\
                   "VarTransform=N:"\
                   "HiddenLayers=10:"\
                   "TrainingMethod=BFGS")

factory.TrainAllMethods()
factory.TestAllMethods()
factory.EvaluateAllMethods()

outf.Close()
