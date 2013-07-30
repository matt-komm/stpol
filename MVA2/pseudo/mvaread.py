#!/usr/bin/python
from array import array
import sys
import ROOT

rdr = ROOT.TMVA.Reader()

r_x=array('f', [0])
r_y=array('f', [0])

rdr.AddVariable('x', r_x)
rdr.AddVariable('y', r_y)

rdr.BookMVA('LikelihoodD', 'weights/jobname_LikelihoodD.weights.xml')

# Apply to data
fin_name = sys.argv[1] if len(sys.argv) > 1 else 'data.root'
fin = ROOT.TFile(fin_name)
dtree = fin.Get("trees/Events")

dtree.SetBranchAddress('x', r_x)
dtree.SetBranchAddress('y', r_y)

h = ROOT.TH1D('', '', 20, 0, 1)

for i in range(dtree.GetEntries()):
	dtree.GetEntry(i)
	mvaVal = rdr.EvaluateMVA('LikelihoodD')
	mvaErr = rdr.GetMVAError();
	#print mvaVal, mvaErr
	h.Fill(mvaVal)
h.Draw()
