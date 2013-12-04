from DataFormats.FWLite import Events, Handle, Lumis
import sys
import os

#Monkey-patch the system path to import the stpol header
sys.path.append(os.path.join(os.environ["STPOL_DIR"], "src/headers"))
from stpol import stpol, list_methods, is_na


file_list = sys.argv[1:]
events = Events(file_list)

for ev in events:
    print(stpol.stable.event.id(ev))
