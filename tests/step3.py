import sys
import os

#Monkey-patch the system path to import the stpol header
sys.path.append(os.path.join(os.environ["STPOL_DIR"], "src/headers"))
from stpol import stpol, list_methods, is_na

from DataFormats.FWLite import Events, Handle, Lumis

#Open the list of files supplied on the command line
file_list = sys.argv[1:]
events = Events(file_list)

for fi in file_list:
    try:
        typ = stpol.stable.file.sample_type(fi)
    except:
        print "sample_type: could not parse file name, sample metainfo not available"
        typ = {}
    print fi, stpol.stable.file.total_processed(fi), typ

#Very temporary short names for convenience
e = stpol.stable.event
w = stpol.stable.weights
sigmu = stpol.stable.tchan.muon
sigele = stpol.stable.tchan.electron
#Loop over the events

nveto_mu = []
nveto_ele = []

puweights = []
def notna(arr):
    return sum([not is_na(c) for c in arr])

cos_thetas = []
for event in events:
    #print e.id(event)
    mu_pt = sigmu.pt(event)
    ele_pt = sigele.pt(event)

    cos_thetas += [e.costheta.lj(event)]
    nveto_mu += [e.vetolepton.nmuons(event)]
    nveto_ele += [e.vetolepton.nelectrons(event)]
    puweights += [w.pileup.nominal(event)]
    #w.toppt.nominal(event)

assert(notna(cos_thetas) == 16)
assert(notna(nveto_mu) == 39)
assert(notna(nveto_ele) == 39)
assert(notna(puweights) == 16)

print "step3 tests ran successfully"
