import ROOT
from DataFormats.FWLite import Events, Handle
import sys
events = Events(sys.argv[1])

muL = ("muonsWithIDAll")
muH = Handle("std::vector<pat::Muon>")

n = 0
for event in events:
    print n
    event.getByLabel(muL, muH)
    if muH.isValid():
    	for mu in muH.product():
    		print "pt=",mu.pt()
    n += 1
