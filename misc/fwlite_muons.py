import ROOT
from DataFormats.FWLite import Events, Handle, Lumis
import time
import numpy

file_list = [
#"sync/inclusive/step1_noSkim.root"
#"sync/pickevents.root"
"sync/inclusive/step1_noSkim.root"
#"/hdfs/cms/store/mc/Summer12_DR53X/T_t-channel_TuneZ2star_8TeV-powheg-tauola/AODSIM/PU_S10_START53_V7A-v1/0000/0059C6F3-7CDC-E111-B4CB-001A92811726.root"
]

events = Events(
    file_list
)

lumis = Lumis(
    file_list
)

patMuH1 = Handle('std::vector<pat::Muon>')
patMuL1 = ("muonsWithID")

patMuH2 = Handle('std::vector<pat::Muon>')
patMuL2 = ("muonsWithIDAll")

recoMuH = Handle('std::vector<reco::Muon>')
recoMuL = ("muons")

def analyze_pat_muon(handle, label):
   event.getByLabel(label, handle)
   if handle.isValid():
       muons = handle.product()
       nMu = 0
       for mu in muons:
           print label,nMu
           print "pt =",mu.pt()," eta =", mu.eta(), " pfIso05 =",mu.pfIsolationR04()
           try:
               print "globaltrack hits =", mu.userFloat("globalTrack_hitPattern_numberOfValidMuonHits"), mu.globalTrack().hitPattern().numberOfValidMuonHits()
           except:
               print "invalid track"
           print "dz =",mu.userFloat("dz")
           a=mu.chargedHadronIso()
           b=mu.pfIsolationR04().sumChargedHadronPt
           print "chHad pt =",a,b
           if abs(a-b)>0.0001:
               print "Error: isolations differ"
           nMu += 1


def analyze_reco_muon(handle, label):
    event.getByLabel(label, handle)
    if handle.isValid():
        muons = handle.product()
        nMu = 0
        for mu in muons:
            print label,nMu
            print "pt =",mu.pt()," eta =", mu.eta()
            try:
                print "globaltrack hits =",mu.globalTrack().hitPattern().numberOfValidMuonHits()
            except:
                print "invalid track"
            nMu += 1

nEv = 0
t0 = time.time()

for event in events:

    print 10*"-"
    print "event id =",event.object().id().event()

    analyze_pat_muon(patMuH1, patMuL1)
    analyze_pat_muon(patMuH2, patMuL2)
    analyze_reco_muon(recoMuH, recoMuL)

    nEv += 1

t1 = time.time()
print "processing speed: %.2f events/sec" % (nEv / (t1-t0))
