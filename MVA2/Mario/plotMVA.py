# Import necessary libraries and data
import ROOT
from ROOT import TFile,TMVA,TCanvas,TH1D,THStack,TLegend,TPad
from copy import copy
from plots.common.cross_sections import xs
from file_names import dataFiles_ele, dataFiles_mu, mcFiles, dataLumi_ele, dataLumi_mu
from plots.common.colors import sample_colors_same
from array import array

# Choose between electron / muon channel fitting
#sample = "mu"
#fn_data = sample+"/SingleMu.root"
sample = "ele"
fn_data = '../step3_latest/'+sample+"/iso/nominal/SingleEle.root"

# Cut string by what to reduce events
cutstring='n_eles == 1 & n_jets == 2 & n_tags == 1 & n_muons == 0 & el_mva > 0.9 & el_pt > 30 & deltaR_bj > 0.3 & deltaR_lj > 0.3'

# not used cutstring part:
#cutstring_other="met > 45 & top_mass > 130 & top_mass < 220"

# Select used luminosity
lumi=dataLumi_ele['Ele']
if sample == "mu": lumi=dataLumi_mu['Mu']

# Which weights we use?
usePU = True
useB = True
useLepTrig = True
useLepID = True
useLepIso = False
lep="electron"
if sample=="mu": lep="muon"
t={}
f={}
w={}

def getDataset(name,filename):
    """ Function will read in the dataset tree, calculate weights and return relevant data """
    f[name] = TFile('../step3_latest/'+sample+"/"+filename)
    t[name] = f[name].Get("trees/Events")
    nh = f[name].Get("trees/count_hist")
    norg = nh.GetBinContent(1)
    w[name] = xs[name]*lumi / norg

def sig(s,b):
    if (b==0):
        return -1
    return sqrt(2*(s+b)*log(1+s/b)-2*s)

for key in mcFiles:
    #for key in klist:
    if sample == "mu" and (key[-5:] == "BCtoE" or key[-10:] == "EMEnriched") or key[0:5] == "GJets":
        continue
    if sample == "ele" and key == "QCDMu":
        continue
    print "Starting:",key
    getDataset(key,mcFiles[key])



print "Loading data"
f['data']=TFile(fn_data)
t['data']=f['data'].Get("trees/Events")
w['data']=1
st={} # Skimmed trees will be here

# Create output file
outf=TFile("skimmed_"+sample+".root","RECREATE")

print "Skimming now"
# Skim the trees
for k in t.keys():
    print "Skimming:",k
    st[k]=t[k].CopyTree(cutstring)

# Initialize TMVA reader
reader=TMVA.Reader()

prt='el'
if sample=='mu': prt='mu'

topm=array('f', [0])
etalj=array('f',[0])
met=array('f',[0])
etabj=array('f', [0])
pt_lep=array('f',[0])
charge=array('f',[0])
pt_bj=array('f', [0])
pt_lj=array('f',[0])
costh=array('f',[0])
w_pu=array('f',[0])
w_b=array('f',[0])
w_trig=array('f',[0])
w_id=array('f',[0])
w_iso=array('f',[0])

reader.AddVariable( "met", met)
reader.AddVariable( "top_mass", topm)
reader.AddVariable( "eta_lj", etalj)
#reader.AddVariable("eta_bj",etabj)
#reader.AddVariable(prt+"_pt",pt_lep)
#reader.AddVariable(prt+"_charge",charge)
#reader.AddVariable("pt_bj",pt_bj)
#reader.AddVariable("pt_lj",pt_lj)

reader.BookMVA("BDT","weights/stop_ele_BDT.weights.xml")
reader.BookMVA("MLP","weights/stop_ele_MLP.weights.xml")
mva="MLP"
nbin=150
bmin=-1.5
bmax=1.5

print "Starting histogram filling"
bdt_cut=0
h={}
ct={}
for k in t.keys():
    print "Starting:",k
    h[k]=TH1D("h_"+k,k+" bdt",nbin,bmin,bmax)
    ct[k]=TH1D("ct_"+k,k+" cos_theta",20,-1,1)
    tr=st[k]
    tr.SetBranchAddress('top_mass',topm)
    tr.SetBranchAddress('eta_lj',etalj)
    tr.SetBranchAddress('met',met)
    tr.SetBranchAddress('cos_theta',costh)
    tr.SetBranchAddress('pu_weight',w_pu)
    tr.SetBranchAddress('b_weight_nominal',w_b)
    tr.SetBranchAddress(lep+'_triggerWeight',w_trig)
    tr.SetBranchAddress(lep+'_IDWeight',w_id)
    tr.SetBranchAddress('muon_IsoWeight',w_iso)
    
    for i in range(tr.GetEntries()):
        tr.GetEntry(i)
        weight=1.
        if usePU: weight*=w_pu[0]
        if useB: weight*=w_b[0]
        if useLepTrig: weight*=w_trig[0]
        if useLepID: weight*=w_id[0]
        if useLepIso: weight*=w_iso[0]
        bdt=reader.EvaluateMVA(mva)
        h[k].Fill(bdt,w[k]*weight)
        if bdt > bdt_cut: ct[k].Fill(costh[0],w[k]*weight)

stack=THStack()
ctstack=THStack()
leg=TLegend(0.8,0.85,0.95,0.95)
merging={
    'stopother':['T_s', 'T_tW', 'Tbar_s', 'Tbar_tW'],
    'ttbar':['TTJets_FullLept', 'TTJets_SemiLept'],
    'wjets':['W1Jets_exclusive', 'W2Jets_exclusive', 'W3Jets_exclusive', 'W4Jets_exclusive'],
    'diboson':['DYJets','WW', 'WZ', 'ZZ'],
    'qcd':['GJets1', 'GJets2', 'QCDMu', 'QCD_Pt_170_250_BCtoE', 'QCD_Pt_170_250_EMEnriched', 'QCD_Pt_20_30_BCtoE', 'QCD_Pt_20_30_EMEnriched', 'QCD_Pt_250_350_BCtoE', 'QCD_Pt_250_350_EMEnriched', 'QCD_Pt_30_80_BCtoE', 'QCD_Pt_30_80_EMEnriched', 'QCD_Pt_350_BCtoE', 'QCD_Pt_350_EMEnriched', 'QCD_Pt_80_170_BCtoE', 'QCD_Pt_80_170_EMEnriched'],
    'signal':['T_t_ToLeptons','Tbar_t_ToLeptons'],
}
cols={'signal':ROOT.kRed,'stopother':ROOT.kBlue,'diboson':ROOT.kOrange,'wjets':ROOT.kYellow,'ttbar':ROOT.kGreen,'qcd':ROOT.kGray}

print "Starting merge"
# Create the actual merges
drawOrder=['stopother','diboson','wjets','ttbar','signal','qcd']
for k in drawOrder:
    for dataset in merging[k]:
        if dataset in t.keys():
            if k in h.keys():
                h[k].Add(h[dataset])
                ct[k].Add(ct[dataset])
            else:
                h[k]=copy(h[dataset])
                h[k].SetNameTitle(k+"_h",k+" bdt")
                h[k].SetLineColor(cols[k])
                h[k].SetFillColor(cols[k])
                ct[k]=copy(ct[dataset])
                ct[k].SetNameTitle(k+"_cth",k+" costh")
                ct[k].SetLineColor(cols[k])
                ct[k].SetFillColor(cols[k])
    stack.Add(h[k])
    ctstack.Add(ct[k])
    leg.AddEntry(h[k],k,'f')

leg.AddEntry(h['data'],'Data','p')
h['data'].SetMarkerStyle(20)
ct['data'].SetMarkerStyle(20)

print '183:',bmin
print drawOrder
bglist=copy(drawOrder)
print drawOrder; print bglist
print '187:',bmin
bglist.remove('signal')
print bmin
bg=TH1D('bg','bgtot',nbin,bmin,bmax)
for i in bglist:
    bg.Add(h[i])

bgInt=TH1D('bgInt','BG cumulative',nbin,bmin,bmax)
sigInt=TH1D('sigInt','Cumulative signal',nbin,bmin,bmax)
for i in range(nbin+2):
    sigInt.SetBinContent(i,h['signal'].Integral(i,nbin+1))
    bgInt.SetBinContent(i,bg.Integral(i,nbin+1))

sigInt.SetLineColor(ROOT.kRed)
bgInt.SetLineColor(ROOT.kBlue)

c=TCanvas("c","Drawing",800,600)
main=TPad("main","main",0.01,0.51,0.99,0.99)
main.Draw()
ratio=TPad("ratio","ratio",0.01,0.01,0.99,0.5)
ratio.Draw()

main.cd()
stack.Draw()
h['data'].Draw("E1same")
leg.Draw()

ratio.cd()
bgInt.Draw("l")
sigInt.Draw('lsame')

c2=TCanvas("c2","c2",800,600)
c2.Draw()
c2.cd()
ctstack.Draw()
ct['data'].Draw("E1same")
leg.Draw()
