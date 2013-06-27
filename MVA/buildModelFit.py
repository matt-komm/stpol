# Import workspace with datasets
from ROOT import *
f_mc=TFile("mc.root")
ws=f_mc.Get('ws')
f_data=TFile('data.root')
ws_data=f_data.Get('kala')

# Define processes
procs=['diboson', 'stopother', 'signal', 'wjets', 'qcd', 'ttbar']
cols={'signal':kRed,'stopother':kPink,'diboson':kOrange,'wjets':kYellow,'ttbar':kGreen,'qcd':kGray}

eta_lj=ws.var('eta_lj')
#eta_lj_abs=RooFormulaVar("eta_lj_abs","|eta_lj|","fabs(eta_lj)",RooArgList(eta_lj))
fr=eta_lj.frame()

ds={}
for p in procs:
  ds[p]=ws.data(p)
  #ds[p].plotOn(fr,RooFit.MarkerColor(cols[p]))

# Now let's build the actual model by making histograms
dh={}
hpdf={}
for p in procs:
    dh[p]=RooDataHist(p+"_hist",p+" histogram",RooArgSet(eta_lj),ds[p])
    hpdf[p]=RooHistPdf(p+"_pdf",p+" pdf",RooArgSet(eta_lj),dh[p])
    getattr(ws,'import')(hpdf[p])
    

# Let's get the data we want to fit
data=ws_data.data('data')

getattr(ws,'import')(data)

# Let's build our model
print "Starting model build"
ws.factory("prod:nwj(kwj[2,.5,3],cwj[" + str(ds['wjets'].sumEntries()) + "])")
ws.factory("prod:ntt(ktt[1.,0.5,1.5],ctt[" + str(ds['ttbar'].sumEntries()) + "])")
ws.factory("prod:nwz(kwz[1.,0.9,1.1],cwz[" + str(ds['diboson'].sumEntries()) + "])")
ws.factory("prod:ntW(ktW[1.],ctW[" + str(ds['stopother'].sumEntries()) + "])")
ws.factory("prod:nsig(ksig[1.,0.5,1.5],csig[" + str(ds['signal'].sumEntries()) + "])")
ws.factory("SUM:model(nwj*wjets_pdf,ntt*ttbar_pdf,ntW*stopother_pdf,nwz*diboson_pdf,nsig*signal_pdf)")
mod=ws.pdf('model')
mod.fitTo(data)
mod.plotOn(fr)
#data2=mod.generate(RooArgSet(eta_lj))
data.plotOn(fr)
mod.plotOn(fr,RooFit.MarkerColor(kRed))
for p in procs:
    mod.plotOn(fr,RooFit.Components(p+"_pdf"),RooFit.LineStyle(kDashed),RooFit.LineColor(cols[p]))

fr.Draw()
#ws.Print()

s=0
for p in procs:
    s+=ds[p].sumEntries()

print "Total MC:",s,"Total data:",data.sumEntries()
