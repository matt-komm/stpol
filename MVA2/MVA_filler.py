import argparse
import pickle
import ROOT
import common
import array
import shutil

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--inputs', nargs = '+', help = 'list of input root files', required=True)
parser.add_argument('-m', '--methods', nargs = '+', help = 'list of pickled MVA method files', required=True)
args = parser.parse_args()

methods = []
for meth in args.methods:
	pklfile = open(meth, "rb")
	meta = pickle.load(pklfile)
	pklfile.close()
	methods.append(meta)

discr = array.array('f', [0])

for inpfn in args.inputs:
	outfn = inpfn.split("/")[-1].replace(".root", "MVA.root")
	shutil.copyfile(inpfn, outfn)
	outf = ROOT.TFile(outfn, "UPDATE")
	outf.cd("trees")
	tree = outf.Get("trees/Events")
	
	for meta in methods:
		reader = ROOT.TMVA.Reader()
		varvalues = {}
		for var in meta.varlist:
			if common.vartypes[var] == "F":
				varvalues[var] = array.array("f", [0])
			elif common.vartypes[var] == "I":
				varvalues[var] = array.array("i", [0])
			reader.AddVariable(var, varvalues[var])
			tree.SetBranchAddress(var,varvalues[var])
		tempxml = open(".temp.xml", "w")
		tempxml.write(meta.xmlstring)
		tempxml.close()
		reader.BookMVA(meta.method_tag, ".temp.xml")
		
		newbranch = tree.Branch(meta.method_tag, discr, meta.method_tag+"/F")
		nentries = tree.GetEntries()
		
		for n in range(nentries):
			tree.GetEntry(n)
			discr[0] = reader.EvaluateMVA(meta.method_tag)
			newbranch.Fill()
		
		tree.Write("", ROOT.TObject.kOverwrite)
	
	outf.Close()
