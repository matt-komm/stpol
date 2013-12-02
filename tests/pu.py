import sys
import os

#Monkey-patch the system path to import the stpol header
sys.path.append(os.path.join(os.environ["STPOL_DIR"], "src/headers"))
from stpol import stpol, list_methods, is_na

from DataFormats.FWLite import Events, Handle, Lumis

#Open the list of files supplied on the command line
file_list = sys.argv[1:]
events = Events(file_list)

e = stpol.stable.event
w = stpol.stable.weights

for event in events:
    print e.id(event), w.pileup.nominal(event)
