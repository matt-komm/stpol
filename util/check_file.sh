#!/bin/bash
python -c "import ROOT; import sys; f = ROOT.TFile(sys.argv[1]); sys.exit(f.IsZombie())" $@
