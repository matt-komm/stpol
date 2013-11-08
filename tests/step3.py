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
w = stpol.stable.event
sigmu = stpol.stable.tchan.muon
sigele = stpol.stable.tchan.electron
#Loop over the events

sum_nveto_mu = 0
sum_nveto_ele = 0
cos_thetas = []
for event in events:
    #print e.id(event)
    mu_pt = sigmu.pt(event)
    ele_pt = sigele.pt(event)

    cos_thetas += [e.costheta.lj(event)]

    sum_nveto_mu += e.VetoLepton.nmuons()
    sum_nveto_ele += e.VetoLepton.nelectrons()

assert(sum([not is_na(c) for c in cos_thetas]) == 16)
print sum_nveto_mu, sum_nveto_ele
print "step3 tests ran successfully"
